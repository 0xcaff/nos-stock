TF_PATH=/home/drone/code/tensorflow
MAKEFILE_PATH=$(TF_PATH)/tensorflow/contrib/makefile

TF_LIB=$(MAKEFILE_PATH)/gen/lib/libtensorflow-core.a
PROTOBUF_LIB=$(MAKEFILE_PATH)/gen/protobuf/lib/libprotobuf.a

INCLUDES=-iquote$(TF_PATH) -I$(MAKEFILE_PATH)/downloads/eigen -I$(MAKEFILE_PATH)/gen/proto
TF_FLAGS=-lpthread -ldl -lz
OPENCV_FLAGS=$(shell pkg-config --cflags --libs opencv)
CXXFLAGS=$(OPENCV_FLAGS) $(TF_FLAGS) -g -Wl,--allow-multiple-definition -Wl,--whole-archive -std=c++0x

infer: infer.cc $(TF_LIB) $(PROTOBUF_LIB) json.hpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o ./infer infer.cc $(TF_LIB) $(PROTOBUF_LIB)

clean:
	rm ./infer

json.hpp:
	curl -O https://raw.githubusercontent.com/nlohmann/json/v2.1.1/src/json.hpp

all: infer
.PHONY: clean
