import zipfile
import platform
import os
import requests
import subprocess
import re

from pathlib import Path


class DownloadBitwarden(object):
    """
    Purpose of this class is only downloading of BitWarden CLI
    """

    @staticmethod
    def download_bitwarden():
        """
        Static method that does downloading of CLI corresponding to execution env
        Available environments:
          - linux
          - macos
          - windows
        """
        platforms = {"linux": "linux", "darwin": "macos", "windows": "windows"}
        p = platforms[platform.system().lower()]
        bitwarden_url = f"https://vault.bitwarden.com/download/?app=cli&platform={p}"
        cwd = os.getcwd()
        path_to_exe_file = ""
        moved = False

        print("\nDownloading BitWarden binary for {}...\n".format(p))

        path_to_zip_file = os.path.join(cwd, "bitwarden.zip")
        r = requests.get(
            bitwarden_url,
            allow_redirects=True,
        )

        # check for return status code
        if r.status_code != 200:
            # setup for alternative download url
            # Step 1: make a request to get a current CLI tool version
            fetch_url = "https://github.com/bitwarden/clients/releases?page="
            link_pattern = r"<a href=\"(\/bitwarden/[a-z\/]+/cli-v[\d\.]+\/bw-{}-\d+\.\d+\.\d+\.zip)\"".format(p)
            i = 1
            downloaded = False
            while not downloaded and i < 5:
                r0 = requests.get(fetch_url + str(i), allow_redirects=True)
                direct_link = re.search(link_pattern, r0.text, re.IGNORECASE | re.MULTILINE)
                if len(direct_link.groups()) == 1:
                    alternate_download_link = f"https://github.com{direct_link.groups()[0]}"
                    print(f"\nDownloading Bitwarden CLI '{direct_link.groups()[0].split('/')[-1]}'")
                    r = requests.get(
                        alternate_download_link,
                        allow_redirects=True,
                    )
                    downloaded = True
                i += 1
            if not downloaded:
                raise Exception("Failed to download Bitwarden CLI client.")

        open(path_to_zip_file, "wb").write(r.content)
        with zipfile.ZipFile(path_to_zip_file, "r") as zip_ref:
            zip_ref.extract(zip_ref.namelist()[0], cwd)
            path_to_exe_file = os.path.join(cwd, zip_ref.namelist()[0])

        print("\nSuccessfully extracted BitWarden binary to {}\n".format(path_to_exe_file))

        if platform.system().lower() == "windows":
            environment_path_var: list = os.getenv("PATH").split(";")
            file_name_with_extension: str = "bw.exe"
        else:
            environment_path_var: list = os.getenv("PATH").split(":")[1:]
            file_name_with_extension: str = "bw"

        # Try to move CLI binary to PATH
        for path_dir in environment_path_var:
            try:
                Path(path_to_exe_file).rename(os.path.join(path_dir, file_name_with_extension))
                path_to_exe_file = os.path.join(path_dir, file_name_with_extension)
                moved = True
                break
            except Exception:
                continue

        if moved:
            print("\nSuccessfully moved BitWarden binary to {}\n".format(path_to_exe_file))
        else:
            print("\nFailed to move BitWarden binary. Current path is {}\n".format(path_to_exe_file))

        if platform.system().lower() != "windows":
            subprocess.run(["chmod", "+x", path_to_exe_file], capture_output=True, text=True)

        return path_to_exe_file
