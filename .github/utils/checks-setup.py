import sys
import os
import re
import json
import argparse
import requests
import hashlib

def main(args):
    with open(args.config_file, "r") as config_file:
        config = json.load(config_file)
    
    if args.subcommand == "pr-check":
        url = args.pr_url + "/files"
        heads = {
            "Authorization": "Bearer {}".format(os.getenv("GITHUB_TOKEN")),
            "X-GitHub-Api-Version": "2022-11-28",
            'Accept': 'application/vnd.github+json' }
        pr_info = json.loads(requests.get(url, headers=heads).text)
        print(json.dumps(build_pr_checks_json(pr_info, config, url, args.test_file)))
    elif args.subcommand == "health-check":
        print(json.dumps(build_health_check_json(config, args.test_file)))
    else:
        print("Invalid subcommand provided. Use pr-check|health-check subcommands. Exiting...")

def setup_checks_json():
    # structure to store the checks to run and related information
    checks_json = {
        "flags": {
            "is_bom_change": False,
            "is_model_change": False,
            "is_container_change": False,
            "is_health_check": False
        },
        "files": {"pr": [], "bom": []},
        "dirs": {"workloads": set(), "containers": set()},
        "services": list()
    }

    return checks_json

def setup_runners():
    # dictionary for runner labels
    runner = {
      "cpu": "k8-runners",
      "gpu": "pvc"
    }

    return runner
    
def build_pr_checks_json(pr_info, config, api_url, test_file):
    PIPE = "|"
    checks_json = setup_checks_json()
    runner = setup_runners()
    url = api_url.replace("api.", "").replace("repos/", "").replace("pulls", "pull")

    # directory structure for models dir
    valid_model_dir = re.compile(
        "^models_v2/"
        + f'({PIPE.join(config["frameworks"])})/[\w-]+/({PIPE.join(config["mode"])})/({PIPE.join(config["platform"])})/[\w/.-]+$'
    )

    # directory structure for containers dir
    valid_container_dir = re.compile(
        "^docker/"
        + f'({PIPE.join(config["frameworks"])})/[\w-]+/({PIPE.join(config["mode"])})/({PIPE.join(config["platform"])})/[\w/.-]+$'
    )

    # review changed files in the PR and activate check to run accordingly 
    for file in pr_info[:]:
        if file["status"] in ["added", "modified", "renamed", "copied", "changed"]:
            checks_json["files"]["pr"].append(f'{file["filename"]} [{file["status"]}]')
            # bom change
            if (
                file["filename"].split("/")[0] in ["models_v2", "docker"]
                and "requirements.txt" in file["filename"].split("/")[:]
            ):
                checks_json["flags"]["is_bom_change"] = True
                checks_json["files"]["bom"].append(build_filename_diff_url(file["filename"], url))
            # model change
            if valid_model_dir.match(file["filename"]):
                model_root = "/".join(file["filename"].split("/")[0:5])
                container_root = "/".join(file["filename"].split("/")[0:5]).replace(
                    "models_v2", "docker"
                )
                checks_json["flags"]["is_model_change"] = True
                checks_json["dirs"]["workloads"].add(model_root)
                # add check for dependent containers
                if os.path.exists(container_root):
                    checks_json["flags"]["is_container_change"] = True
                    checks_json["dirs"]["containers"].add(container_root)
            # container change
            if valid_container_dir.match(file["filename"]):
                container_root = "/".join(file["filename"].split("/")[0:5]).replace(
                    "models_v2", "docker"
                )
                checks_json["flags"]["is_container_change"] = True
                checks_json["dirs"]["containers"].add(container_root)

    for container in checks_json["dirs"]["containers"]:
        composefile = "/".join(container.split("/")[0:2]) # docker/<framework>
        service = "-".join(container.split("/")[2:5]) # <framework>-<mode>-<platform>
        platform = container.split("/")[4] # cpu/gpu
        checks_json["services"].append(
            {
                "service": service,
                "project": f"{os.getenv('GITHUB_RUN_NUMBER', default='0')}-{composefile.split('/')[1]}",
                "file": f"{composefile}/docker-compose.yml",
                "runner": f"{runner[platform]}",
                "smoke": f"{container}/{test_file}"
            }
        )

    checks_json["dirs"]["workloads"] = list(checks_json["dirs"]["workloads"])
    checks_json["dirs"]["containers"] = list(checks_json["dirs"]["containers"])

    return checks_json

def build_health_check_json(config, test_file):
    PIPE = "|"
    checks_json = setup_checks_json()
    checks_json["flags"]["is_health_check"] = True
    runner = setup_runners()

    # directory structure for containers dir
    valid_container_dir = re.compile(
        "^docker/"
        + f'({PIPE.join(config["frameworks"])})/[\w-]+/({PIPE.join(config["mode"])})/({PIPE.join(config["platform"])})$'
    )

    # create a list of the models in the repository to run the tests
    for directory in [x[0] for x in os.walk('docker')]:
        if valid_container_dir.match(directory):
            checks_json["dirs"]["containers"].add(directory)

    for container in checks_json["dirs"]["containers"]:
        composefile = "/".join(container.split("/")[0:2]) # docker/<framework>
        service = "-".join(container.split("/")[2:5]) # <framework>-<mode>-<platform>
        platform = container.split("/")[4] # cpu/gpu
        checks_json["services"].append(
            {
                "service": service,
                "project": f"{os.getenv('GITHUB_RUN_NUMBER', default='0')}-{composefile.split('/')[1]}",
                "file": f"{composefile}/docker-compose.yml",
                "runner": f"{runner[platform]}",
                "smoke": f"{container}/{test_file}"
            }
        )

    checks_json["dirs"]["workloads"] = list(checks_json["dirs"]["workloads"])
    checks_json["dirs"]["containers"] = list(checks_json["dirs"]["containers"])

    return checks_json


def build_filename_diff_url(filename, url): 
    file_info = {
        'filename': f'{filename}',
        'diff_url': ''
    }
    
    filename_hash = hashlib.sha256(filename.encode()).hexdigest()
    file_info['diff_url'] =  url + '#diff-' + filename_hash
    
    return file_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(sys.argv)
    parser.add_argument("-f", "--test_file", help="Yaml file name that contains the tests for the models", default="tests.yaml")
    parser.add_argument("-c", "--config_file", help="Config file in YAML format.", required=True)

    subparsers = parser.add_subparsers(dest="subcommand")
    hchk_parser = subparsers.add_parser("health-check", help='Create the JSON checks config for health check on the repository')
    prchk_parser = subparsers.add_parser("pr-check", help='Create the JSON checks config for PR check workflow')
    prchk_parser.add_argument("-u", "--pr_url", help="Pull request URL endpoint for REST calls", required=True)

    args = parser.parse_args()

    main(args)
