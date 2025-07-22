#!/usr/bin/env python

import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oneBOM")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("get_info_packages.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

CURRENT_DIR = os.getcwd()
DB_FILE = "third_party_version_listing.csv"
IT_FILE = "Third_Party_Request_3.xlsx"
BASE_DIR = os.getenv("LOCAL_DISK", "/localdisk")

# This is the dataframe that holds the whole DB for the packages available in the platform
dataframe_db = pd.read_csv(
    os.path.join(BASE_DIR, DB_FILE), index_col=0, low_memory=False
)
# This dataframe holds the base file with the requirements for IT to fill the packages information in bulk
dataframe_it = pd.read_excel(
    os.path.join(BASE_DIR, IT_FILE),
    index_col=0,
    sheet_name="Third_Party_Version_Request",
)


lookup_packages = dataframe_it[
    "name"
].tolist()  # Change this to use pURL instead of name
wanted_columns = [
    "FullyQualifiedIpTxt",
    "FullyQualifiedVersionNbr",
    "PurlTxt",
    "RelatedHomepageUrlTxt",
    "VersionExternalTxt",
    "RepositoryPathTxt",
    "ParentComponentItemId",
]


def all_packages_info():
    """
    Get information about all packages in the dataframe.
    If a package is not found, it will perform a partial search.
    It will create three CSV files:
    - final_dataframe.csv: Contains the latest version of each package.
    - existing_dataframe.csv: Contains packages that already exist with the same version.
    - partial_results.csv: Contains results from partial searches for packages not found.

    """
    final_dataframe = pd.DataFrame()
    existing_dataframe = pd.DataFrame()
    # partial_results = pd.DataFrame()
    missing_packages = []
    already_existing_packages = []
    logger.info("Looking for packages in the IT file: %s", lookup_packages)

    for package in lookup_packages:
        wanted_version = dataframe_it.query("name == @package").filter(
            items=["version_external"]
        )
        logger.info(
            "Wanted version for package %s: %s",
            package,
            wanted_version["version_external"].values[0],
        )

        found_package = individual_package_info(package)

        if found_package.empty:
            logger.info(
                "No data found for the specified package.: %s",
                package,
            )

            missing_packages.append(package)
            missing_row = pd.DataFrame(
                {
                    "FullyQualifiedIpTxt": [package],
                    "FullyQualifiedVersionNbr": [""],
                    "PurlTxt": [""],
                    "RelatedHomepageUrlTxt": [""],
                    "VersionExternalTxt": [""],
                    "RepositoryPathTxt": [""],
                    "ParentComponentItemId": [""],
                }
            )
            final_dataframe = pd.concat(
                [final_dataframe, missing_row], ignore_index=True
            )
        else:
            logger.info("Found package: %s", package)
            if str(wanted_version["version_external"].values[0]) == str(
                found_package["VersionExternalTxt"].values[0]
            ):
                print(f"Package {package} exists already.")
                already_existing_packages.append(package)
                existing_dataframe = pd.concat(
                    [existing_dataframe, found_package], ignore_index=True
                )
            else:
                final_dataframe = pd.concat(
                    [final_dataframe, found_package], ignore_index=True
                )

    logger.info("Missing packages: %s", missing_packages)
    with open(os.path.join(CURRENT_DIR, "pkg_list.txt"), "w") as f:
        for package in missing_packages:
            f.write(f"{package[:-5]}\n")

    logger.info("Already existing packages: %s", already_existing_packages)

    final_dataframe.to_csv(
        os.path.join(CURRENT_DIR, "final_dataframe.csv"), index=False
    )
    existing_dataframe.to_csv(
        os.path.join(CURRENT_DIR, "existing_dataframe.csv"), index=False
    )
    # partial_results.to_csv(
    #     os.path.join(CURRENT_DIR, "partial_results.csv"), index=False
    # )


def get_latest_version_information(df):
    """
    Get the latest version details from the search
    """
    latest_version = df.sort_values("FullyQualifiedVersionNbr").nlargest(
        1, "FullyQualifiedVersionNbr"
    )
    return latest_version


def get_base_version_information(df):
    """
    Get the base version details from the search
    """
    base_version = df.sort_values("FullyQualifiedVersionNbr").nsmallest(
        1, "FullyQualifiedVersionNbr"
    )
    return base_version


def search_package(package):
    """
    Search for a package in the dataframe.
    Returns the matching packages.
    """
    matches = dataframe_db[
        dataframe_db["PurlTxt"].str.contains(package, case=False, na=False)
    ].filter(items=wanted_columns)
    return matches if not matches.empty else pd.DataFrame()


def individual_package_info(package):
    """
    Get information about a specific package.
    If the package is not found, it will perform a partial search.
    """
    logger.info(
        "Searching for package: %s",
        dataframe_it.query("name == @package")["pURL"].values,
    )
    purl_from_package = dataframe_it.query("name == @package")["pURL"].values[0]
    # logger.info(type(purl_from_package))
    logger.info("PURL from package: %s", purl_from_package)

    match_purl = dataframe_db.query("PurlTxt == @package").filter(items=wanted_columns)
    if match_purl.empty:
        logger.error("Package %s not found in the database file.", package)
        logger.info(
            "Performing partial search for package: %s without version", package
        )
        no_version_purl = purl_from_package.split("@")[0] + "@"
        logger.info("Looking for pURL: %s", no_version_purl)
        match_purl = partial_package_search(no_version_purl)
        if match_purl.empty:
            logger.error("No partial search results found for package: %s", package)
            return pd.DataFrame()
        logger.info("Partial search results: %s", match_purl)
        match_purl = get_latest_version_information(match_purl)
    else:
        logger.info("Match PURL: %s", match_purl)

        match_purl = get_latest_version_information(match_purl)
    return match_purl


def partial_package_search(package, regex=False):
    """
    Perform a partial search for the package in the dataframe.
    Returns the matching packages.
    """
    if regex:
        package = r"^" + package + r"$"
    matches = dataframe_db[
        dataframe_db["PurlTxt"].str.contains(package, case=False, na=False, regex=regex)
    ].filter(items=wanted_columns)
    return matches if not matches.empty else pd.DataFrame()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Get information about a specific package."
    )
    parser.add_argument(
        "--package", type=str, help="The name of the package to get information for."
    )
    parser.add_argument(
        "--all", action="store_true", help="Get information for all packages."
    )

    args = parser.parse_args()

    if args.all:
        all_packages_info()
    else:
        logger.info("Searching for package: %s", args.package)
        search_results = search_package(args.package)
        logger.info("Search results for package %s: %s", args.package, search_results)
        # individual_package_info(args.package)
