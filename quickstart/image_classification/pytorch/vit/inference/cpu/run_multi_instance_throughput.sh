#!/bin/bash
#
# Copyright (c) 2021 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



ARGS=""

export DNNL_PRIMITIVE_CACHE_CAPACITY=1024
export MALLOC_CONF="oversize_threshold:1,background_thread:true,metadata_thp:auto,dirty_decay_ms:9000000000,muzzy_decay_ms:9000000000"

num_warmup=${num_warmup:-"10"}
num_iter=${num_iter:-"100"}
ARGS="$ARGS --benchmark --perf_begin_iter ${num_warmup} --perf_run_iters ${num_iter}"

precision="fp32"
if [[ "$1" == "bf16" ]]
then
    precision="bf16"
    ARGS="$ARGS --bf16"
    echo "### running bf16 mode"
elif [[ "$1" == "fp16" ]]
then
    precision=fp16
    ARGS="$ARGS --fp16_cpu"
    echo "### running fp16 mode"
elif [[ "$1" == "fp32" ]]
then
    echo "### running fp32 mode"
elif [[ "$1" == "bf32" ]]
then
    precision="bf32"
    ARGS="$ARGS --bf32 --auto_kernel_selection"
    echo "### running bf32 mode"
elif [[ "$1" == "int8-fp32" ]]
then
    precision="int8-fp32"
    ARGS="$ARGS --int8 --int8_config configure.json"
    echo "### running int8-fp32 mode"
elif [[ "$1" == "int8-bf16" ]]
then
    precision="int8-bf16"
    ARGS="$ARGS --bf16 --int8 --int8_config configure.json"
    echo "### running int8-bf16 mode"
else
    echo "The specified precision '$1' is unsupported."
    echo "Supported precisions are: fp32, bf32, bf16, fp16, int8-fp32, int8-bf16"
    exit 1
fi

if [ -z "${OUTPUT_DIR}" ]; then
  echo "The required environment variable OUTPUT_DIR has not been set, please create the output path and set it to OUTPUT_DIR"
  exit 1
fi

CORES=`lscpu | grep Core | awk '{print $4}'`
BATCH_SIZE=${BATCH_SIZE:-`expr 4 \* $CORES`}
FINETUNED_MODEL=${FINETUNED_MODEL:-"google/vit-base-patch16-224"}
DATASET_DIR=${DATASET_DIR:-"None"}
DATASET_ARGS=""
if [[ "None" == ${DATASET_DIR} ]];then
    DATASET_ARGS="--dataset_name imagenet-1k"
else
    DATASET_ARGS="--train_dir ${DATASET_DIR}/train --validation_dir ${DATASET_DIR}/val"
fi

EVAL_SCRIPT=${EVAL_SCRIPT:-"./transformers/examples/pytorch/image-classification/run_image_classification.py"}
WORK_SPACE=${WORK_SPACE:-${OUTPUT_DIR}}

rm -rf ${OUTPUT_DIR}/throughput_log*
TORCH_INDUCTOR=${TORCH_INDUCTOR:-"0"}
if [[ "0" == ${TORCH_INDUCTOR} ]];then
    path="ipex"
    ARGS="$ARGS --use_ipex"
    echo "### running with intel extension for pytorch"
    mode="jit"
    ARGS="$ARGS --jit_mode_eval"
    echo "### running with jit mode"
    python -m intel_extension_for_pytorch.cpu.launch --throughput-mode --enable_tcmalloc --log_path=${OUTPUT_DIR} --log_file_prefix="./throughput_log_${path}_${precision}_${mode}" \
        ${EVAL_SCRIPT} $ARGS \
        --model_name_or_path   ${FINETUNED_MODEL} \
        --do_eval \
        --output_dir ./tmp \
        --per_device_eval_batch_size $BATCH_SIZE \
        ${DATASET_ARGS} \
        --remove_unused_columns False
else
    echo "Running inference with torch.compile inductor backend."
    export TORCHINDUCTOR_FREEZING=1
    python -m torch.backends.xeon.run_cpu --throughput-mode --enable_tcmalloc --log_path=${OUTPUT_DIR} \
        ${EVAL_SCRIPT} $ARGS \
        --inductor \
        --model_name_or_path   ${FINETUNED_MODEL} \
        --do_eval \
        --output_dir ./tmp \
        --per_device_eval_batch_size $BATCH_SIZE \
        ${DATASET_ARGS} \
        --remove_unused_columns False 2>&1 | tee ${OUTPUT_DIR}/throughput_log_${path}_${precision}_${mode}.log
fi

throughput=$(grep 'Throughput:' ${OUTPUT_DIR}/throughput_log* |sed -e 's/.*Throughput//;s/[^0-9.]//g' |awk '
BEGIN {
        sum = 0;
	i = 0;
      }
      {
        sum = sum + $1;
i++;
      }
END   {
sum = sum / i;
printf("%.3f", sum);
}')
echo "--------------------------------Performance Summary per NUMA Node--------------------------------"
echo ""vit-base";"throughput";${precision};${BATCH_SIZE};${throughput}" | tee -a ${WORK_SPACE}/summary.log
