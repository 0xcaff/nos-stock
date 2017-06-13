// A webpack plugin which generates a list of video ids from our collection of
// inferences along with titles from the youtube api.

const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');

const VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"
const INFERENCE_SUFFIX = '.mp4.infer.json';

function GenerateMetadata(options) {
	// The file system search path from wich to build the inference metadata.
	this.searchPath = options.path;

	// The published date must be before this time for the metadata to be
	// emitted.
	this.mustBeBefore = options.before;

	// The API key used to make requests with the youtube data api.
	this.apiKey = options.apiKey;
};

GenerateMetadata.prototype.apply = function(compiler) {
	compiler.plugin('emit', (compilation, callback) => {
		this.__onEmit(compilation).then(() => callback());
	});
};

GenerateMetadata.prototype.__onEmit = async function onEmit(compilation) {
	// get all inference files
	const ids = (await getFiles(this.searchPath))
		.filter(file => file.endsWith(INFERENCE_SUFFIX))
		.map(infered => infered.substring(
				0, infered.length - INFERENCE_SUFFIX.length));

	const params = {
		part: 'snippet',
		id: ids.join(','),
		key: this.apiKey,
	};

	// encode params
	var esc = encodeURIComponent;
	var query = Object.keys(params)
		.map(k => `${esc(k)}=${esc(params[k])}`)
		.join('&');

	// request data
	const resp = await fetch(VIDEOS_ENDPOINT + "?" + query)
	const body = await resp.json();
	if (!resp.ok) {
		throw body;
	}

	// format data
	const output = body['items']
		.map(item => ({
				id: item['id'],
				title: item['snippet']['title'],
				published: new Date(item['snippet']['publishedAt']),
			}))
		.filter(item => item.published.getTime() <= this.mustBeBefore)

		// sort from newest to oldest
		.sort((a, b) => b['published'].getTime() - a['published'].getTime());

	// emit
	const rawOutput = JSON.stringify(output);
	compilation.assets['inferences/index.json'] = {
		source: () => rawOutput,
		size: () => rawOutput.length,
	};

	// copy inference files
	const filesPromises = output.map(item => item['id'])
		.map(id => readFile(path.join(this.searchPath, id+INFERENCE_SUFFIX))
			.then(data => compilation.assets[`inferences/${id}.json`] = {
				source: () => data,
				size: () => data.length,
			}));

	// wait for population to complete
	await Promise.all(filesPromises);
};

function getFiles(path) {
	return new Promise((resolve, reject) => {
		fs.readdir(path, (err, files) => {
			if (err) {
				reject(err);
			}

			resolve(files);
		});
	});
}

function readFile(path) {
	return new Promise((resolve, reject) => {
		fs.readFile(path, (err, data) => {
			if (err) {
				reject(err);
			}

			resolve(data);
		});
	});
}

module.exports = GenerateMetadata;

