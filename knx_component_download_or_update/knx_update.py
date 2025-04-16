from io import BytesIO
import requests
import os
import zipfile
import json
import argparse

TOKEN = '<SECRET>'
URL = '<SECRET>'

OWNER = "home-assistant"
REPO = "core"
FOLDER = "homeassistant/components/knx"
FILE_TO_EDIT = "const.py"

def get_ha_version() -> str:
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.get(f'{URL}/api/config', headers=headers)
    response.raise_for_status()

    data = response.json()
    version = data.get("version")

    if not version:
        raise ValueError("Key 'version' not found in response JSON")

    return version


def download_folder(version: str, output_dir: str):
    zip_url = f"https://github.com/{OWNER}/{REPO}/archive/refs/tags/{version}.zip"

    print(f"Downloading ZIP for version {version}...")
    response = requests.get(zip_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download ZIP file: {response.status_code} {response.text}")

    print("Extracting required folder...")
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        for member in zip_file.namelist():
            if member.startswith(f"{REPO}-{version}/{FOLDER}"):
                relative_path = os.path.relpath(member, f"{REPO}-{version}/{FOLDER}")
                target_path = os.path.join(output_dir, relative_path)
                if member.endswith("/"):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "wb") as f:
                        f.write(zip_file.read(member))

    print(f"Folder '{FOLDER}' extracted to '{output_dir}'.")


def replace_string_in_file(file_path: str, search: str, replacement: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.readlines()

    with open(file_path, "w", encoding="utf-8") as file:
        for line in content:
            if search in line:
                line = line.replace(search, replacement)
            file.write(line)

    print(f"String '{search}' replaced with '{replacement}' in '{file_path}'.")


def prepare_manifest_file(file_path: str, domain: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    with open(file_path, "r", encoding="utf-8") as file:
        content = json.load(file)

    content["domain"] = domain
    content["name"] = domain.upper()
    content["version"] = "1.0.0"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=4)

    print(f"Manifest file {file_path} prepared.")


def main():
    parser = argparse.ArgumentParser(description="Clone and modify Home Assistant KNX component.")
    parser.add_argument("--domain", required=True, help="New domain name (e.g., 'knx2')")
    args = parser.parse_args()

    domain = args.domain
    search_string = 'DOMAIN: Final = "knx"'
    replacement_string = f'DOMAIN: Final = "{domain}"'

    version = get_ha_version()

    try:
        download_folder(version, domain)
        print(f"KNX folder for version {version} downloaded successfully.")

        const_path = os.path.join(domain, FILE_TO_EDIT)
        replace_string_in_file(const_path, search_string, replacement_string)

        manifest_path = os.path.join(domain, "manifest.json")
        prepare_manifest_file(manifest_path, domain)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
