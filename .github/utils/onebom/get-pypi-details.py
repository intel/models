import requests
import pandas as pd
import os

MISSING_LIST = "missingpkgs.csv"
CURRENT_DIR = os.getcwd()

dataframe_missing = pd.read_csv(os.path.join(CURRENT_DIR, MISSING_LIST), index_col=0)

def get_pypi_package_details(package_name):
    """
    Get details of a PyPI package by its name.
    Returns a dictionary with package details or None if not found.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Package '{package_name}' not found on PyPI.")
        return None

def parse_details(package_details):
    """
    Parse and format the package details from the PyPI JSON response.
    Returns a formatted string with relevant package information.
    """
    if not package_details:
        return "No package details available."

    info = package_details.get("info", {})
    name = info.get("name", "Unknown")
    project_url = info.get("project_url", "No Project URL.")
    project_urls = info.get("project_urls", {})
    pURL = "pkg:pypi/" + name
    pURL_version = "pkg:pypi/" + name + "@" + dataframe_missing.loc[name].get("version")

    details = (
        f"Package Name: {name}_pypi\n"
        f"Project URL: {project_url}\n"
        f"pURL: {pURL}\n"
        f"pURL with version: {pURL_version}\n"
        "Project URLs: \n"
    )
    try:
        for url_name, url in project_urls.items():
            details += f"  {url_name}: {url}\n"
    except AttributeError:
        details += "  No additional project URLs available.\n"

    return details


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get PyPI package details")
    parser.add_argument("--package", help="Name of the package to get details for")
    parser.add_argument("--all", action="store_true", help="Get details for all packages in the missing list")

    args = parser.parse_args()

    package_details = get_pypi_package_details(args.package)
    if args.all:
        print("Fetching details for all packages in the missing list...")
        for package in dataframe_missing.index:
            package_details = get_pypi_package_details(package)
            if package_details:
                print(parse_details(package_details))
                with open("pypi_packages.yaml", "a") as yaml_file:
                    yaml_file.write(parse_details(package_details))
            else:
                print(f"No details found for package: {package}")
        exit()
    else:
        print(f"Fetching details for package: {args.package}")
        if package_details:
            print(parse_details(package_details))
        else:
            print("No details found for the specified package.")
