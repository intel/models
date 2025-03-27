#!/usr/bin/python

# The purpose of this script is to create a new top-level requirements file list to be digested by trivy scans,
# and then to run trivy scans on the pinned requirements.
# The reason we don't run Trivy directly on the requirements.freeze is that the list bloats and will make any
# manual work for BOM to create/update components exhausting, and not necessary when BOM uses a top/sub assembly
# structure.
# ex: matplotlib is dependent on fakelib1 and fakelib2 and will install them
# but BOM only requires us to list the top level requirements (3PSW) that are directly required
# assembly structure means that IPX "knows" matplotlib at v3.x.x requires fakelib1=v1.y.y and fakelib2=v1.z.z

import argparse
import re
from importlib.metadata import metadata

# global regex splitter for pip package notation
# IGNORING git / git+ / git@ - hardcoded edge case in the routines
regex_pattern = r"[;\|~=!<>\[]+"


# cases like DLLogger being installed via git won't mean anything to Trivy so we are use pkg_resources
# to get the actual library name that pip understands (ex. git+.../dllogger -> DLLogger==1.0.0)
def get_package_data(package_name):
    # data = pkg_resources.get_distribution(package_name)
    data = metadata(package_name).json
    return data


def generate_raw_requirements_map(path_to_requirements_file):
    raw_data_map = dict()
    with open(path_to_requirements_file, "r") as fh:
        raw_data = fh.read().splitlines()
        for item in raw_data:
            if "@" in item:
                requirement = item.split("@")[0].rstrip()
                raw_data_map.update({requirement: item})
                continue
            requirements_version = list(
                filter(None, re.split(regex_pattern, item))
            )  # search for two characters to split on
            requirement = requirements_version[0]
            version = requirements_version[1]
            raw_data_map.update({requirement: version})
        fh.close()
    return raw_data_map


def generate_pinned_replacement_list(raw_requirements_map, original_requirements_list):
    new_requirements_list = list()
    for item in original_requirements_list:
        print(item)
        if item == "" or item[0] == "#":
            continue
        # check for unusual invocations, ex. 'git DLLlogger@...'
        elif "git+" in item:
            article = item.split("/")[-1]  # get egg name from git URL
            if "#egg=" in article:  # then egg is being specified, so use that instead
                article = article.split("#egg=")[1]
            if ".git" in item:
                article = article.replace(".git", "")
            article = article.rstrip('"').lstrip('"')
            print(article)
            data = get_package_data(article)
            print(data)
            name = data.get("name")
            print(name)
            version = raw_requirements_map.get(name)
            print(version)
            print(raw_requirements_map)
            if version is None or "@" in version:
                # try to use the version as it appears in importlib metadata:
                version = data.get("version")
            new_requirements_list.append(f"{name}=={version}")
        elif "==" in item:
            new_requirements_list.append(item)
        # most general case: a requirement without specific version
        elif re.search(regex_pattern, item):
            requirement = re.split(regex_pattern, item)[0]
            version = raw_requirements_map.get(requirement)
            new_requirements_list.append(f"{requirement}=={version}")
        else:
            version = raw_requirements_map.get(item)
            if version is None:
                continue
            new_requirements_list.append(f"{item}=={version}")
    return new_requirements_list


def generate_frozen_master_dependencies(
    path_to_requirements, path_to_frozen, output_file
):
    raw_map = generate_raw_requirements_map(path_to_frozen)
    old_requirements = list()
    with open(path_to_requirements, "r") as fh:
        old_requirements.extend(fh.read().splitlines())
        fh.close()
    new_requirements = generate_pinned_replacement_list(raw_map, old_requirements)
    with open(output_file, "w") as fh:
        for item in new_requirements:
            fh.write(f"{item}\n")
        fh.close()


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--requirements",
        type=str,
        required=True,
        help="path to root requirements file (pre-pip-freeze)",
    )
    parser.add_argument(
        "-f",
        "--frozen",
        type=str,
        required=True,
        help="path to frozen requirements file (post-pip-freeze)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="path to file name data should be written to (existing file will cause a failure)",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = args()
    requirements = args.requirements
    frozen = args.frozen
    output_file = args.output
    generate_frozen_master_dependencies(requirements, frozen, output_file)
