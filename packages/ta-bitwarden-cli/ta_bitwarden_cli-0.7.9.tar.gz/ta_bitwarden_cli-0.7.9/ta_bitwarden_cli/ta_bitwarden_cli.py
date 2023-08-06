import os
import subprocess
import json
import logging
import re

from subprocess import TimeoutExpired
from typing import List
from retry import retry
from .download_bitwarden import DownloadBitwarden


class BitwardenServerException(Exception):
    pass


class Bitwarden(object):
    """
    Main class that does all work
    """

    def __init__(self, bitwarden_credentials=None):
        """
        bitwarden_credentials - dict with 'password' / 'client_id' / 'client_secret' keys
        'bw' binary should be already in PATH
        """
        self.data = {}
        self.path_to_exe_file = "bw"
        self.bitwarden_credentials = bitwarden_credentials
        self.session_key = ""

    def bitwarden_exe(self, *command):
        """
        Provide coma-separated command line arguments that you want to provide to bw CLI binary
        Searches binary in PATH. If fails tries to run it from current working directory
        Examples:
          - bw.bitwarden_exe('logout')
          - bw.bitwarden_exe(
            "unlock",
            self.bitwarden_credentials["password"],
            "--raw",
            )
        """
        env = {
            **os.environ,
        }

        if self.bitwarden_credentials["client_id"] and self.bitwarden_credentials["client_secret"]:
            env["BW_CLIENTID"] = str(self.bitwarden_credentials["client_id"])
            env["BW_CLIENTSECRET"] = str(self.bitwarden_credentials["client_secret"])
            logging.info("Using provided client_id and client_secret")
        else:
            logging.info("Using client_id and client_secret from env vars")

        try:
            if not env["BW_CLIENTID"] or not env["BW_CLIENTSECRET"]:
                raise ValueError("Empty client_id or client_secret!")
        except KeyError as e:
            raise ValueError("Empty client_id or client_secret!") from e

        try:
            return subprocess.run(
                [
                    self.path_to_exe_file,
                    *command,
                ],
                capture_output=True,
                text=True,
                timeout=180,
                env=env,
            )
        except FileNotFoundError:
            self.path_to_exe_file = DownloadBitwarden.download_bitwarden()
            return subprocess.run(
                [
                    self.path_to_exe_file,
                    *command,
                ],
                capture_output=True,
                text=True,
                timeout=180,
                env=env,
            )

    @retry((TimeoutExpired, BitwardenServerException), delay=5, tries=3)
    def bitwarden_login(self):
        """
        Performs login opeartion via BitWarden CLI
        Requires password / client_id / client_secret already set when creation Bitwarden instance
        """
        self.bitwarden_exe("logout")

        bitwarden_app = self.bitwarden_exe(
            "login",
            "--apikey",
        )

        if "You are logged in!" in bitwarden_app.stdout:
            bitwarden_app = self.bitwarden_exe(
                "unlock",
                self.bitwarden_credentials["password"],
                "--raw",
            )

            if "Invalid master password" in bitwarden_app.stderr:
                logging.error(f"STDOUT: {bitwarden_app.stdout}")
                logging.error(f"STDERR: {bitwarden_app.stderr}")
                raise ValueError("Invalid master password!")

            if not re.search(r".{80,}", bitwarden_app.stdout):
                logging.error(f"STDOUT: {bitwarden_app.stdout}")
                logging.error(f"STDERR: {bitwarden_app.stderr}")
                raise RuntimeError("No session key returned after login!")

            self.session_key = bitwarden_app.stdout
        else:
            logging.error(f"STDOUT: {bitwarden_app.stdout}")
            logging.error(f"STDERR: {bitwarden_app.stderr}")

            if "invalid_client" in bitwarden_app.stderr:
                raise ValueError("Invalid bitwarden client_id or client_secret!")

            raise BitwardenServerException("Bitwarden Server error during login! Retrying...")

    def get_credentials(self, user_credentials_name):
        """
        This method is for backward compatibility
        """
        self.bitwarden_login()
        self.get_data(user_credentials_name)
        return self.data

    @retry((TimeoutExpired, BitwardenServerException), delay=5, tries=3)
    def get_data(self, data):
        """
        Core method
        Obtaining of data from bitwarden vault for provided Key Name
        Saves dict with results to self.data variable
        Each key in dict is your custom name
        Each value in dict is another dict with data from bitwarden vault

        Example:

          items = {
              "unicourt_api": "UniCourt API",
              "unicourt_alpha_api": "UniCourt Alpha API Dev Portal",
              "aws": "AWS Access Key & S3 Bucket",
          }
          bw.get_data(items)
          assert isinstance(bw.data['aws'],dict)
        """
        print("Syncing bitwarden data...")
        bitwarden_app = self.bitwarden_exe(
            "sync",
            "--session",
            self.session_key,
        )

        print("Getting bitwarden data...")
        bitwarden_app = self.bitwarden_exe(
            "list",
            "items",
            "--session",
            self.session_key,
        )

        if not bitwarden_app.stdout:
            logging.error(f"STDERR: {bitwarden_app.stderr}")
            raise RuntimeError("Empty result for 'bw list items' command! This user has no items associated")

        bitwarden_items = json.loads(bitwarden_app.stdout)
        items_not_found: List[str] = []
        for credentials_key, credentials_name in data.items():
            for bw_item in bitwarden_items:
                if credentials_name == bw_item["name"]:
                    self.data[credentials_key] = {
                        "login": bw_item["login"]["username"],
                        "password": bw_item["login"]["password"],
                        "url": bw_item["login"]["uris"][0]["uri"] if "uris" in bw_item["login"] else "",
                    }

                    if bw_item["login"]["totp"] is None:
                        self.data[credentials_key]["otp"] = ""
                    else:
                        bitwarden_app = self.bitwarden_exe(
                            "get",
                            "totp",
                            bw_item["id"],
                            "--session",
                            self.session_key,
                        )
                        self.data[credentials_key]["otp"] = bitwarden_app.stdout
                    if "fields" in bw_item:
                        for field in bw_item["fields"]:
                            self.data[credentials_key][field["name"]] = field["value"]

                    break
            else:
                items_not_found.append(credentials_name)

        if items_not_found:
            logging.error(f"STDOUT: {bitwarden_app.stdout}")
            logging.error(f"STDERR: {bitwarden_app.stderr}")
            raise BitwardenServerException(
                "Invalid bitwarden collection or key name or no access to collection for this user! Items not found "
                f"include {', '.join(items_not_found)}"
            )

    @retry((TimeoutExpired, BitwardenServerException), delay=5, tries=3)
    def get_attachment(self, item_name, file_name, output_folder=os.getcwd()):
        """
        Downloads attachment file from particular item to current working directory
        Item name should be unique
        File name should be unique
        Output folder path is absolute

        Example:

            items = {
                "test": "pypi.org",
            }
            self.bw.bitwarden_login()
            self.bw.get_attachment(items["test"], "att.txt")
            f = open("att.txt", "r")
            assert f.read() == "secret text\n"
        """
        if not isinstance(item_name, str) or not isinstance(file_name, str) or not isinstance(output_folder, str):
            raise TypeError("item_name / file_name / output_folder should be strings!")

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        print("Syncing bitwarden data...")
        bitwarden_app = self.bitwarden_exe(
            "sync",
            "--session",
            self.session_key,
        )

        # Get item ID
        bitwarden_app = self.bitwarden_exe(
            "get",
            "item",
            item_name,
            "--session",
            self.session_key,
        )

        if bitwarden_app.stderr:
            logging.error(f"STDOUT: {bitwarden_app.stdout}")
            logging.error(f"STDERR: {bitwarden_app.stderr}")
            if "A 404 error occurred while downloading the attachment" in bitwarden_app.stderr:
                raise BitwardenServerException("404 HTTP from bitwarden server occurred!")
            if "More than one result was found" in bitwarden_app.stderr:
                raise ValueError("More than one result for item name was found! Name should be unique!")
            if "Not found" in bitwarden_app.stderr:
                raise ValueError(f"Cannot find bitwarden item '{str(item_name)}'! Check the name")
            raise RuntimeError("Unknown error during items obtaining!")

        bitwarden_items = json.loads(bitwarden_app.stdout)
        item_id = str(bitwarden_items["id"])

        bitwarden_app = self.bitwarden_exe(
            "get",
            "attachment",
            file_name,
            "--itemid",
            item_id,
            "--session",
            self.session_key,
            "--output",
            os.path.join(output_folder, file_name),
        )

        if bitwarden_app.stderr:
            logging.error(f"STDOUT: {bitwarden_app.stdout}")
            logging.error(f"STDERR: {bitwarden_app.stderr}")

            if "was not found" in bitwarden_app.stderr:
                raise ValueError("Attachment was not found!")

            raise RuntimeError("Unknown error during attachment downloading!")

        print(f"Attachment '{file_name}' downloaded sucessfully!")
