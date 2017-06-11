#include <chrono>
#include <string>
#include <iostream>
#include <iomanip>

#include "tensorflow/core/public/session.h"
#include "tensorflow/core/framework/tensor.h"
#include "tensorflow/core/framework/graph.pb.h"

#include <opencv2/opencv.hpp>

#include "json.hpp"

using json = nlohmann::json;

#define RETURN_IF_ERROR(status)                                 \
	do {                                                        \
		if (!status.ok()) {                                     \
			std::cerr << status.error_message() << std::endl;   \
			return -1;                                          \
		}                                                       \
	} while (0)

const std::string INPUT_ENDPOINT = "Cast:0";
const std::string OUTPUT_ENDPOINT = "final_result:0";

typedef struct {
	int frame_number;
	float nos_score;
	float non_nos_score;
} FrameInfo;

void copyMatToTensor(cv::Mat mat, tensorflow::Tensor *tensor) {
	// initialize mat vars
	int depth = mat.channels();
	int height = mat.rows;
	int width = mat.cols;
	const float* data = (float*)mat.data;

	// initial tensor vars
	// 3 dimensional data (rows x columns x depth)
	auto eigen_tensor = tensor->tensor<float, 3>();
	
	// copy frame
	for (int y = 0; y < height; y++) {
		const float* row = data + (y * width * depth);

		for (int x = 0; x < width; x++) {
			const float* pixel = row + (x * depth);

			// convert from bgr to rgb
			const float* blue = pixel + 0;
			const float* green = pixel + 1;
			const float* red = pixel + 2;

			// y, x, channel
			eigen_tensor(y, x, 0) = *red;
			eigen_tensor(y, x, 1) = *green;
			eigen_tensor(y, x, 2) = *blue;
		}
	}
}

int main(int argc, char* argv[]) {
	std::vector<FrameInfo> frame_infos(top_k);

	// parse arguments
	std::string graph_path = argv[1];
	std::string video_path = argv[2];
	int skip_frames = std::stoi(argv[3]);

	// import model
	tensorflow::GraphDef graph_def;
	RETURN_IF_ERROR(ReadBinaryProto(
		tensorflow::Env::Default(),
		graph_path,
		&graph_def
	));

	// create session
	tensorflow::SessionOptions options;
	std::unique_ptr<tensorflow::Session> session(
		tensorflow::NewSession(options));
	RETURN_IF_ERROR(session->Create(graph_def));

	// initialize video
	cv::VideoCapture capture(video_path);
	if (!capture.isOpened()) {
		std::cerr << "Failed to open video file: " << video_path
			<< std::endl;

		return 1;
	}

	std::unique_ptr<tensorflow::Tensor> input_tensor;

	// go through frames
	int frame_number = 0;

	while(true) {
		auto start_time = std::chrono::high_resolution_clock::now();

		// skip skip_frames
		bool grab_failed = false;
		for (int i = 0; i < skip_frames + 1; i++) {
			if (!capture.grab()) {
				grab_failed = true;
				break;
			}

			frame_number++;
		}

		if (grab_failed) {
			std::cerr << "Failed to grab next frame" << std::endl;
			break;
		}

		// continue processing frames
		cv::Mat raw_frame;
		if (!capture.retrieve(raw_frame)) {
			std::cerr << "Failed to retrive next frame" << std::endl;
			break;
		}

		std::cerr << "Frame Number: " << frame_number << std::endl;

		int type = raw_frame.type();
		if (type != CV_8UC3) {
			std::cerr << "Unexpected mat format" << type << std::endl;
			break;
		}

		// convert to full color float
		cv::Mat frame;
		raw_frame.convertTo(frame, CV_32FC3);

		// initialize tensor
		if (!input_tensor) {
			int height = frame.rows;
			int width = frame.cols;

			input_tensor.reset(new tensorflow::Tensor(tensorflow::DT_FLOAT, {
				height,           // rows
				width,            // columns
				frame.channels(), // depth
			}));
		}

		// copy into tensor
		copyMatToTensor(frame, input_tensor.get());

		// infer frame
		std::vector<tensorflow::Tensor> inferences;
		RETURN_IF_ERROR(session->Run(
			{{INPUT_ENDPOINT, *input_tensor}},
			{OUTPUT_ENDPOINT},
			{},
			&inferences
		));

		// get inferences
		tensorflow::Tensor output_tensor = std::move(inferences.at(0));
		auto scores = output_tensor.flat<float>();
		float nos_score = scores(0);
		float non_nos_score = scores(1);

		// print scores
		std::cerr << std::setprecision(2) << nos_score << std::endl;
		std::cerr << std::setprecision(2) << non_nos_score << std::endl;

		// add only if > than top k
		for (int i = 0; i < frame_infos.size(); i++) {
			FrameInfo frame_info = frame_infos.at(i);

			if (nos_score >= frame_info.nos_score) {
				// > than top k

				// store inferences
				FrameInfo frame_info = {};
				frame_info.frame_number = frame_number;
				frame_info.nos_score = nos_score;
				frame_info.non_nos_score = non_nos_score;

				// remove last, insert ours
				frame_infos.pop_back();
				frame_infos.insert(frame_infos.begin() + i, frame_info);

				break
			}
		}

		auto end_time = std::chrono::high_resolution_clock::now();
		auto iter_time = std::chrono::duration_cast<std::chrono::milliseconds>
			(end_time - start_time);

		std::cerr << "Took " << iter_time.count() << "ms" << std::endl;
		std::cerr << std::endl;
	}

	json j_frame_infos(frame_infos);
	std::cout << j_frame_infos << std::endl;

	capture.release();
}

void to_json(json& j, const FrameInfo& frame_info) {
	j = json{
		{"frame_number", frame_info.frame_number},
		{"scores", {frame_info.nos_score, frame_info.non_nos_score}}
	};
}

