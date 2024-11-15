#!/usr/bin/python3

import os
import glob
import argparse
import json

def generate_list_of_requirements_files(root_directory, output_file):
    requirements_files_list = [x.replace(f"{root_directory}/", '') for x in glob.glob(f"{root_directory}/**/requirements.txt", recursive=True)]
    print(requirements_files_list)
    number_files = len(requirements_files_list)
    print(f"{number_files} requirements.txt files collected")
    with open(output_file, "w") as fh:
        json.dump(requirements_files_list, fh)
        fh.close()
    print(f"Requirements files list saved to '{output_file}'")
    return requirements_files_list

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, default='.', required=False, help='path to root directory for requirements.txt discovery')
    parser.add_argument('-o', '--output', type=str, required=True, help='path to file name data should be written to (existing file will cause a failure)')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = args()
    root_directory = args.directory
    output_file = args.output
    generate_list_of_requirements_files(root_directory, output_file)
