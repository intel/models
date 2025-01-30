# Tools and pipelines for CI and automation processes

This directory contains tools and workflows for the automation of Continuous Integration (CI)/ Continuous Deployment (CD) processes of AIRM. 

**IMPORTANT**: This folder (`.github/`) is not and shouldn't be included in the public AIRM mirror.


# Directory Structure

- **.github/**
    - `actions/`: Contains custom GitHub Actions definitions.
    - `config/`: Contains config files used by scripts in `utils` folder.
    - `linters/`: Contains configurations files for the `super-linter` linters.
    - `utils/`: Contains scripts and samples used for CI/CD and SDL tasks.
    - `workflows/`: Contains GitHub Actions workflow files for automating CI/CD processes.
    - `dependabot.yaml`: Configuration file for `dependabot` version updates.
    - `README.md`: This file. Provides an overview of the CI documentation directory.


# Actions

At the moment of this writing (2025.01.28), the only custom action defined in this folder (`check-performance`) is out of date and unusable.


# Config

`MZ-PyTorch.json`: Old config file used to create the list of tests to run for PyTorch models, currently out-of-date.

`MZ-TensorFlow.json`: Old config file used to create the list of tests to run for TensorFlow models, currently out-of-date.

`compliance-config.json`: Config file that contains the valid values for Models V2 compliance. It includes whitelists to skip tests for folder structure, mandatory files and test structure checks. 


# Linters

`super-linter` config files, the main configuration is found in the `airm.yml` workflow file.

| Enabled linter             | Config file          |
|----------------------------|----------------------|
| ENV                        | _default_            |
| GITHUB_ACTIONS             | `actionlint.yml`     |
| GITLEAKS                   | _default_            |
| GIT_MERGE_CONFLICT_MARKERS | _default_            |
| JSON                       | _default_            |
| MARKDOWN                   | `.markdown-lint.yml` |
| YAML                       | `.yaml-lint.yml`     |


# Utils
- **utils/**
    - `aikit/`: TBD
    - `onebom`: TBD
    - `checks-setup.py`: Builds a json table with all the information required for a validation workflow with the tests that it'll execute/
    - `comment-bom-changes.py`: Used to add or update comments to PRs on presense of BoM changes in the PR changed files.
    - `create-md-table.py`: TBD
    - `models_v2-compliance-check.py`: It validates that all the mandatory files are compliant with the configuration set in the config file provided.


### `checks-setup.py`
Script to build a JSON structure to contains all the information needed to run a set of tests on AIRM models.

#### Usage
```
python3 checks-setup.py [-h] [-f <TEST_FILE>] -c <CONFIG_FILE> {health-check,pr-check} ...
```

#### Optional parameters
`-h`, `--help`: Displays help information for the script
`-f, --test_file`: Gets the name of the YAML file in the docker model directory that has the tests to be executed, if not provided the default value is _"tests.yaml"_, the whole suit will take a long time to run, it's recommended to use _"smoke.yaml"_ for a faster functionality valitation.

#### Mandatory parameters
`-c, --config_file`: JSON file that has the configuration to be used.
_`subcommand`_: The scripts require one of the two subcommands to specify the type of tests that will run.

#### Subcommands

#### `health-check`
Creates a table with the test information for the models inside all the container images in the docker directory.

##### Usage
```
python3 checks-setup.py [-h] [-f <TEST_FILE>] -c <CONFIG_FILE> health-check 
```
**Note:** No mandatory parameters are required for this subcommand

##### Optional parameters
`-h`, `--help`: Displays help information for the subcommand

##### Examples
```
python3 .github/utils/checks-setup.py \
  -c .github/config/compliance-config.json \
  health-check

python3 .github/utils/checks-setup.py \
  --test_file smoke.yaml \
  --config_file .github/config/compliance-config.json \
  health-check
```

#### `pr-check`
 Creates a table with the test information for the models added or modified in a specific PR. It gets the information of the files in the PR from GitHub REST API, if the script is manually tested an environment variable `$GITHUB_TOKEN` has to be set with a valid token with PR read permissions in the AIRM repository.

##### Usage
```
python3 checks-setup.py [-h] [-f <TEST_FILE>] -c <CONFIG_FILE> pr-check -u <PR_URL>
```
##### Optional parameters
`-h`, `--help`: Displays help information for the subcommand

##### Mandatory parameters
`-u`,`--pr-url`: PR URL address to request for the PR files information.

##### Examples
```
python3 .github/utils/checks-setup.py \
  -c .github/config/compliance-config.json \
  pr-check \
    -u https://api.github.com/repos/intel-innersource/frameworks.ai.models.intel-models/pulls/2594

python3 .github/utils/checks-setup.py \
  --test_file smoke.yaml \
  --config_file .github/config/compliance-config.json \
  pr-check \
    --pr-url https://api.github.com/repos/intel-innersource/frameworks.ai.models.intel-models/pulls/2594
```


### `comment-bom-changes.py`
Script for adding or updating comments to PRs for reviewers to pay attention given that a PR contains BoM changes.

### Usage
```
python3 comment-bom-changes.py [-h] -u <PR_URL> -j <BOM_FILES_JSON>
```

#### Optional parameters
`-h`, `--help`: Displays help information for the script

#### Mandatory parameters
`-h`, `--help`: Displays help information for the script
`-u`, `--pr-url`: URL address of the PR
`-j`, `--bom-files-json`: JSON scructure with the list of files with BoM changes.

###### Example
```
python3 .github/utils/comment-bom-changes.py \
    -u 'https://api.github.com/repos/intel-innersource/frameworks.ai.models.intel-models/pulls/2592' \
    -j '[
    {
      "filename": "models_v2/tensorflow/3d_unet/inference/cpu/requirements.txt",
      "diff_url": "https://github.com/intel-innersource/frameworks.ai.models.intel-models/pull/2592/files#diff-8af20d165c5e3fa1a96b2dfb3e14565cafd9dd791e5e5e3c197e439a29efc4a0"
    }
  ]'
```


### `models_v2-compliance-check.py`
It checks that the mandatory files are present in all the models under the specified directory and that the test files are compliant with the format required. 

#### Usage
```
python3 models_v2-compliance-check.py [-h] -d <MODELS_DIR> -c <CONFIG_FILE>
```
#### Optional parameters
`-h`, `--help`: Displays help information for the script

#### Mandatory parameters
`-d`, `--models-dir`: The directory where it will validate the compliance of the models.
`-c`, `--config_file`: The JSON config file with the parameters to validate for each model.

#### Example
```
  python3 .github/utils/models_v2-compliance-check.py \
    --models_dir models_v2 \
    --config_file .github/config/compliance-config.json
```


# Workflows
YAML files that define the CI/CD pipelines. These workflows are triggered on-demand or by events such as pushes and pull requests,.

##### Up-to-date workflows
| Filename               | Workflow                   |
|------------------------|----------------------------|
| `airm-lint.yml`        | AIRM Linter                |
| `health-check.yml`     | Health Check               |
| `mirror-sync.yml`      | Mirror sync-up             |
| `models_v2_check.yml`  | Models v2 compliance check |
| `pr-validations.yml`   | PR validations             |
| `unit-test.yml`        | Unit Test                  |
| `Scanner_Coverity.yml` | Scanner-Coverity           |

##### Out-of-date workflows
| Filename                   | Workflow                         |
|----------------------------|----------------------------------|
| `cicd-pipeline.yml`        | CI/CD Pipeline                   |
| `mz-workload-launcher.yml` | Model Zoo Workload Test Launcher |
| `build-workflow.yml`       | Container Build Workflow         |


### AIRM Linter
Workflow that runs `super-linter` on the repository.

###### Triggers
On Pull Request and on Push event.

###### Inputs
None required.


### Health Check
It runs a model validation using the tests defined in each model directory for all the models in `docker` directory in the repository.

###### Triggers
On demand.

###### Inputs
- **Dry Run**: Flag to indicate if the job will only provides a list of tests that will be executed or it will actually run the tests.
- **Test file**: File name to use that should be located in the docker directory where the model is defined. Given that the whole suit using `tests.yaml` files can takes several days it's recommended to use `smoke.yaml` for shorter execution time, it can go up to a couple of days for smoke testing depending on resources available.


### Mirror sync-up
It override anything in [public AIRM](https://github.com/intel/ai-reference-models) repository with the content of `main` branch. It filter out the `.github` directory and all its content.

###### Triggers
On demand and on every commit to main branch.

###### Inputs
None required.


### Models v2 compliance check
Uses a Python script to check that the PRs changes are compliant with the requirements described in the [Contributing](https://github.com/intel-innersource/frameworks.ai.models.intel-models/blob/develop/CONTRIBUTING.md) document.

###### Triggers
On Pull Request.

###### Inputs
None required.


### PR validations
It enable the PR-checks required for a specific PR depending on the added/modified files in it. It focus on changes on models, container images and BoM changes.

###### Triggers
On Pull Request.

###### Inputs
Picks them from GitHub REST API.


### Unit Test
Scan the PR and reports the coverity, current threshold is 80% of coverage.

###### Triggers
On Pull Request.

###### Inputs
None required.


### Scanner-Coverity
Job to run Coverity scanner on the repository, primarily used for SDL/OSPDT requirements.

###### Triggers
On demand.

###### Inputs
- **GitHub organization**: Where the repository to be scanned lives,internal AIRM repos is `intel-ineersource`
- **Repository**: GitHub project address, for AIRM is `frameworks.ai.models.intel-models`
- **Branch** Branch in the project to be analyzed, e.g. `main` or `v3.3`
- **Build Command**: Coverity script or command to use, this is an optional parameter that can be left blank.
- **Project Type**: For AIRM is `python`, other possible values are `java`, `gcc`, etc.
- **Coverity Server URL**: Coverity scanner server URL address, AIRM uses instance 8, `https://coverity.devtools.intel.com/prod8`
- **Coverity Stream Name**: The stream name registered in Coverity service for AIRM project, `model_zoo_first_test`
- **Runners**: List of runner labels to be used for the scanner, currently using `[ 'k8-runners' ]`
