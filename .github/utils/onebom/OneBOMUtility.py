import OneBOMGlobals
import argparse
import os


class OneBOMUtility:
    """Utility class for OneBOM"""

    def __init__(self):
        # Create the parser
        parser = argparse.ArgumentParser(description="Utility class for OneBoM.")
        # Add the arguments
        parser.add_argument(
            "-l",
            "--log-level",
            type=str,
            default=None,
            help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        )
        parser.add_argument(
            "-g",
            "--get-guid",
            action="store_true",
            help="Pass this flag to get the GUIDs for the given IPX names",
        )
        parser.add_argument(
            "-r",
            "--requirements",
            required=True,
            type=str,
            default=None,
            help="Path to the file with a list of requirements files",
        )
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            default=None,
            help="Output file to write the results to",
        )
        self.args = None
        self.parse_and_validate_args(parser)

    def ipx_ip_name_from_requirements_path(self, req_path):
        # Extract the IPX name from the requirements path
        # The requirements path is of the form:
        # ./AIRM/APP/PATH/requirements.txt
        # The IPX name is the APP/PATH part

        # Remove the leading "./" and trailing "/requirements.txt"
        app_name = req_path[
            OneBOMGlobals.ROOT_STR_LEN : -OneBOMGlobals.REQUIREMENTS_STR_LEN
        ]

        # Replace the "/" with "_"
        if len(app_name) > 0:
            ip_name = (
                f"{OneBOMGlobals.AIRM_IPX_PREFIX}-{app_name.replace('/', '-')}_src"
            )
        else:
            ip_name = f"{OneBOMGlobals.AIRM_IPX_PREFIX}_src"

        OneBOMGlobals.debug(
            f"ipx_ip_name_from_requirements_path: {req_path} -> {ip_name}"
        )
        return ip_name

    def load_requirements_files(self) -> list:
        with open(OneBOMGlobals.AIRM_REQUIREMENTS_FILE, "r") as fh:
            return fh.read().splitlines()

    def parse_and_validate_args(self, parser):
        # Parse the arguments
        self.args = parser.parse_args()
        if self.args.log_level:
            # If they put anything here, just debug
            OneBOMGlobals.DEBUG = True
        if not self.args.requirements or not os.path.exists(self.args.requirements):
            OneBOMGlobals.error(
                f"List of reuirements.txt files in {self.args.requirements} does not exist."
            )

    def run(self):
        requirements = self.load_requirements_files()
        lines = list()
        try:
            from scripts import IPXUtils
        except ImportError as e:
            import sys

            OneBOMGlobals.error(
                f"IPXUtils not found. Please make sure the IPXUtils module is available: {e.msg}. Current PYTHONPATH: {sys.path}"
            )
        ipxUtils = IPXUtils.IPXUtils("PROD")
        for file in requirements:
            name = self.ipx_ip_name_from_requirements_path(file)
            OneBOMGlobals.info(f"IPX name for {file} is {name}")
            line = f"{name}"
            if self.args.get_guid:
                guid = ipxUtils.get_guid_of_latest_version(
                    OneBOMGlobals.AIRM_IP_LIBRARY, name
                )
                OneBOMGlobals.info(f"GUID for {name} is {guid}")
                line += f",{guid}"
            OneBOMGlobals.debug(f"Adding line: {line}")
            lines.append(line)

        if self.args.output:
            with open(self.args.output, "w") as fh:
                fh.write("\n".join(lines))


if __name__ == "__main__":
    oneBoMUtil = OneBOMUtility()
    oneBoMUtil.run()
