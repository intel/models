#!/usr/bin/python

import filecmp
import os
import shutil
import argparse

def check_file_diff(file1, file2):
    outcome = filecmp.cmp(file1, file2, shallow=False)
    return outcome

def digest_app_collections(path_to_directory):
    # in the current format, the collections are numbered by the strategy.job-index to make sure there are unique numbers.
    # the file structure of the artifacts is as follows:
    # <number>:
    #   | map.txt # maps the job index number to the app path (ex. models/tensorflow/gpu/...)
    #   | requirements.orig.txt # original requirements.txt file before pinning
    #   | requirements.txt # requirements file after version pinning
    #   | requirements.frozen.txt # entire dump of library versions from pip freeze
    #   | trivy-scan-spdx.json # trivy scan of requirements.txt (post version pinning)
    collection = dict()
    for root, dirs, files in os.walk(path_to_directory):
        if root == path_to_directory:
            continue
        app_metadata = dict()
        print(root)
        app_metadata["path_to_metadata"] = f"{root}"
        with open(f"{root}/map.txt", "r") as fh:
            mapdata = fh.read().rstrip()
            app_metadata["app_path"] = mapdata.split(':')[1]
            app_metadata["index"] = mapdata.split(':')[0]
        fh.close()
        collection.update({app_metadata["app_path"]: app_metadata})
    if len(collection) <= 0:
        print(f"Collection for {path_to_directory} is unexpectedly empty")
    return collection

def generate_app_lists(new_collection, old_collection, pinned_file_name="requirements.txt"):
    # for now a naive x * y check
    # two checks:
    # does x[app1] exist for y[app1]?
    # are their locked versions the same?
    apps_needing_created = list()
    apps_needing_updated = list()
    apps_needing_disabled = list() # this will NOT be automatic without specific approval - for now it just collects for artifacts
    for x in new_collection.items():
        itemx = x[1]
        itemy = old_collection.get(x[0], None)
        if itemy is None:
            # app x does not exist in previous release, so needs to be created
            apps_needing_created.append(itemx)
        else:
            pathx = itemx["path_to_metadata"] + "/" + pinned_file_name
            pathy = itemy["path_to_metadata"] + "/" + pinned_file_name
            diff = check_file_diff(pathx, pathy)
            if not diff:
                apps_needing_updated.append(itemx)
            del old_collection[x[0]]
    for y in old_collection.items():
        # everything in old release that is NOT in new release is (in theory) to be EOLd.
        apps_needing_disabled.append(y[1])
    return apps_needing_created, apps_needing_updated, apps_needing_disabled

def package_app_lists_for_artifacting(collection, path_to_package_directory):
    # just organizes the files, since Github's upload-artifact will do the rest
    for item in collection:
        # copy the whole directory to the new location
        shutil.copytree(item["path_to_metadata"], f"{path_to_package_directory}/" + item["index"], dirs_exist_ok=True)

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--previous-release', type=str, required=True, help='path to root directory for previous release metadata')
    parser.add_argument('-n', '--next-release', type=str, required=True, help='path to root directory for next release metadata')
    parser.add_argument('-o', '--output', type=str, required=True, help='path to output directory packages should be collected (directory structure should exist)')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = args()
    previous_root_directory = args.previous_release
    next_root_directory = args.next_release
    output_dir = args.output
    #print(digest_app_collections("/tmp/bomtest"))
    previous_release_metadata = digest_app_collections(previous_root_directory)
    next_release_metadata = digest_app_collections(next_root_directory)
    (apps_needing_created, apps_needing_updated, apps_needing_disabled) = generate_app_lists(next_release_metadata, \
        previous_release_metadata, "requirements.txt")
    package_app_lists_for_artifacting(apps_needing_created, f"{output_dir}/apps-needing-create")
    package_app_lists_for_artifacting(apps_needing_updated, f"{output_dir}/apps-needing-update")
    package_app_lists_for_artifacting(apps_needing_disabled, f"{output_dir}/apps-needing-disable")
