<!-- 60. Docker -->
## Docker

The model container `<docker image>` includes the scripts
and libraries needed to run <model name> <mode>. To run one of the model
inference quickstart scripts using this container, you'll need to provide volume mounts for
the ImageNet dataset (if a real dataset is being used) and an output directory where
checkpoint files will be written.

```
DATASET_DIR=<path to the preprocessed imagenet dataset>
PRECISION=<set the precision to "fp32" or "bfloat16">
OUTPUT_DIR=<directory where log files will be written>
# For a custom batch size, set env var `BATCH_SIZE` or it will run with a default value.
export BATCH_SIZE=<customized batch size value>

docker run \
  --env DATASET_DIR=${DATASET_DIR} \
  --env PRECISION=${PRECISION} \
  --env OUTPUT_DIR=${OUTPUT_DIR} \
  --env BATCH_SIZE=${BATCH_SIZE} \
  --env http_proxy=${http_proxy} \
  --env https_proxy=${https_proxy} \
  --volume ${DATASET_DIR}:${DATASET_DIR} \
  --volume ${OUTPUT_DIR}:${OUTPUT_DIR} \
  --privileged --init -t \
  <docker image> \
  /bin/bash quickstart/<script name>.sh
```

If you are new to docker and are running into issues with the container,
see [this document](https://github.com/IntelAI/models/tree/master/docs/general/docker.md)
for troubleshooting tips.