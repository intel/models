<!--- 0. Title -->
# PyTorch Mask R-CNN inference

<!-- 10. Description -->
## Description

This document has instructions for running Mask R-CNN inference using
Intel-optimized PyTorch.

## Model Package

The model package includes the Dockerfile and scripts needed to build and
run Mask R-CNN inference in a container.
```
pytorch-spr-maskrcnn-inference
├── README.md
├── build.sh
├── download_dataset.sh
├── licenses
│   ├── LICENSE
│   └── third_party
├── model_packages
│   └── pytorch-spr-maskrcnn-inference.tar.gz
├── pytorch-spr-maskrcnn-inference.Dockerfile
└── run.sh
```

<!--- 40. Quick Start Scripts -->
## Quick Start Scripts

| Script name | Description |
|-------------|-------------|
| `inference_realtime.sh` | Runs multi instance realtime inference using 4 cores per instance for the specified precision (fp32, avx-fp32, or bf16). |
| `inference_throughput.sh` | Runs multi instance batch inference using 24 cores per instance for the specified precision (fp32, avx-fp32, or bf16). |
| `accuracy.sh` | Measures the inference accuracy for the specified precision (fp32, avx-fp32, or bf16). |

> Note: The `avx-fp32` precision runs the same scripts as `fp32`, except that the
> `DNNL_MAX_CPU_ISA` environment variable is unset. The environment variable is
> otherwise set to `DNNL_MAX_CPU_ISA=AVX512_CORE_AMX`.

## Datasets

Download the 2017 [COCO dataset](https://cocodataset.org) using the `download_dataset.sh` script
from the container package.
Export the `DATASET_DIR` environment variable to specify the directory where the dataset
will be downloaded. This environment variable will be used again when running quickstart scripts.
```
cd pytorch-spr-maskrcnn-inference
export DATASET_DIR=<directory where the dataset will be saved>
bash download_dataset.sh
```

## Build the container

The Mask R-CNN inference package has scripts and a Dockerfile that are
used to build a workload container that runs the model. This container
uses the PyTorch/IPEX container as it's base, so ensure that you have built
the `pytorch-ipex-spr.tar.gz` container prior to building this model container.

Use `docker images` to verify that you have the base container built. For example:
```
$ docker images | grep pytorch-ipex-spr
model-zoo         pytorch-ipex-spr         f5b473554295        2 hours ago         4.08GB
```

To build the Mask R-CNN inference container, extract the package and
run the `build.sh` script.
```
# Extract the package
tar -xzf pytorch-spr-maskrcnn-inference.tar.gz
cd pytorch-spr-maskrcnn-inference

# Build the container
./build.sh
```

After the build completes, you should have a container called
`model-zoo:pytorch-spr-maskrcnn-inference` that will be used to run the model.

## Run the model

Download the pretrained model and set the `PRETRAINED_MODEL` environment variable
to point to the file.
```
curl -O https://download.pytorch.org/models/maskrcnn/e2e_mask_rcnn_R_50_FPN_1x.pth
export PRETRAINED_MODEL=$(pwd)/e2e_mask_rcnn_R_50_FPN_1x.pth
```

After you've downloaded the pretrained model and followed the instructions to
[build the container](#build-the-container) and [prepare the dataset](#datasets),
use the `run.sh` script from the container package to run Mask R-CNN inference.
Set environment variables to specify the dataset directory, precision to run, and
an output directory. By default, the `run.sh` script will run the
`inference_realtime.sh` quickstart script. To run a different script, specify
the name of the script using the `SCRIPT` environment variable.
```
# Navigate to the container package directory
cd pytorch-spr-maskrcnn-inference

# Set the required environment vars
export PRECISION=<specify the precision to run>
export PRETRAINED_MODEL=<path to the downloaded .pth file>
export DATASET_DIR=<path to the dataset>
export OUTPUT_DIR=<directory where log files will be written>

# Run the container with inference_realtime.sh quickstart script
./run.sh

# Specify a different quickstart script to run, for example, accuracy.sh
SCRIPT=accuracy.sh ./run.sh
```

<!--- 80. License -->
## License

Licenses can be found in the model package, in the `licenses` directory.
