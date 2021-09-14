<!--- 40. Quick Start Scripts -->
## Quick Start Scripts

| Script name | Description |
|-------------|-------------|
| `inference_realtime.sh` | Runs multi instance realtime inference using 4 cores per instance for the specified precision (fp32, int8 or bf16) using the [huggingface pretrained model](https://cdn.huggingface.co/bert-large-uncased-whole-word-masking-finetuned-squad-pytorch_model.bin). |
| `inference_throughput.sh` | Runs multi instance batch inference using 1 instance per socket for the specified precision (fp32, int8 or bf16) using the [huggingface pretrained model](https://cdn.huggingface.co/bert-large-uncased-whole-word-masking-finetuned-squad-pytorch_model.bin). |
| `accuracy.sh` | Measures the inference accuracy for the specified precision (fp32, int8 or bf16) using the [huggingface pretrained model](https://cdn.huggingface.co/bert-large-uncased-whole-word-masking-finetuned-squad-pytorch_model.bin). |