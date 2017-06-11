#include <chrono>
#include <string>
#include <iostream>
#include <iomanip>

#include "tensorflow/core/public/session.h"
#include "tensorflow/core/framework/tensor.h"
#include "tensorflow/core/framework/graph.pb.h"

#include <opencv2/opencv.hpp>
#include <opencv2/core/eigen.hpp>

#define RETURN_IF_ERROR(status)									\
	do {                                                        \
		if (!status.ok()) {                                     \
			std::cerr << status.error_message() << std::endl;   \
			return -1;                                          \
		}                                                       \
	} while (0)

const std::string INPUT_ENDPOINT = "Cast:0";
const std::string OUTPUT_ENDPOINT = "final_result:0";

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

std::vector<std::string> get_labels(std::string file_name) {
	std::vector<std::string> result;
	std::ifstream label_file(file_name);

	std::string line;
	while (std::getline(label_file, line)) {
		result.push_back(line);
	}

	return result;
}

int main(int argc, char* argv[]) {
	// parse arguments
	std::string graph_path = argv[1];
	std::string labels_path = argv[2];
	std::string video_path = argv[3];

	std::vector<std::string> labels = get_labels(labels_path);

	// TODO: Implement
	int skip_frames = std::stoi(argv[4]);
	// int batch_frames = std::stoi(argv[5]);

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
		for (int i = 0; i < skip_frames + 1; i++) {
			if (!capture.grab()) {
				std::cerr << "Failed to grab next frame" << std::endl;
				return -1;
			}

			frame_number++;
		}

		// continue processing frames
		cv::Mat raw_frame;
		if (!capture.retrieve(raw_frame)) {
			std::cerr << "Failed to retrive next frame" << std::endl;
			break;
		}

		std::cout << "Frame Number: " << frame_number << std::endl;

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

		// print inferences
		tensorflow::Tensor output_tensor = std::move(inferences.at(0));
		auto scores = output_tensor.flat<float>();
		for (unsigned int i = 0; i < labels.size(); i++) {
			std::string label = labels.at(i);
			float score = scores(i);

			std::cout << label << ": " << std::setprecision(2) << score << std::endl;
		}

		auto end_time = std::chrono::high_resolution_clock::now();
		auto iter_time = std::chrono::duration_cast<std::chrono::milliseconds>
			(end_time - start_time);

		std::cout << "Took " << iter_time.count() << "ms" << std::endl;

		std::cout << std::endl;
	}

	capture.release();
}

