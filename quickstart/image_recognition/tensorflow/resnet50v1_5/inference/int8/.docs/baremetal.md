<!--- 50. Bare Metal -->
## Bare Metal

To run on bare metal, the following prerequisites must be installed in your environment:
* Python 3
* [intel-tensorflow==2.1.0](https://pypi.org/project/intel-tensorflow/)
* numactl

After installing the prerequisites, download and untar the model package.
Set environment variables for the path to your `DATASET_DIR` and an
`OUTPUT_DIR` where log files will be written, then run a 
[quickstart script](#quick-start-scripts).

For accuracy, `DATASET_DIR` is required to be set. For inference,
just to evaluate performance on sythetic data, the `DATASET_DIR` is not needed.
Otherwise `DATASET_DIR` needs to be set:

```
DATASET_DIR=<path to the dataset>
OUTPUT_DIR=<directory where log files will be written>

wget https://ubit-artifactory-or.intel.com/artifactory/list/cicd-or-local/model-zoo/<model-precision-mode>.tar.gz
tar -xzf <model-precision-mode>.tar.gz
cd <model-precision-mode>

quickstart/<script name>.sh
```