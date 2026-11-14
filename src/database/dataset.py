from dataclasses import dataclass
import json
from multiprocessing import Value
import sys

import requests

from log import log_debug, log_err, log_info, log_ok, log_warn
from database import connection

@dataclass
class DatasetMetadata:
    dataset_id: str
    dataset_api: str

    def get_resource(self):
        log_info(f"Fetching dataset {self.dataset_id}")
        response = requests.get(
            self.dataset_api + "action/package_show?id=" + self.dataset_id
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise ValueError(f"{e}") from e

        package = response.json()["result"]
        log_debug(
            f"Using package \033[1m{package['name']}\033[0m from {package['author']}"
        )
        resources = package["resources"]

        geojson_url = None
        for resource in resources:
            if resource["format"].upper() == "GEOJSON":
                geojson_url = resource["url"]
                log_debug(
                    f"Downloading resource \033[1m{resource['name']}\033[1m ({resource['package_id']})"
                )
                break

        if not geojson_url:
            raise ValueError("No valid resource format found in dataset (Required: GEOJSON)")

        geojson_response = requests.get(geojson_url, stream=True)
        data = download_with_progress(geojson_response, package["name"])

        try:
            geojson_response.raise_for_status()
            log_ok(f"Download complete for \033[1m{package["name"]}\033[0m")
            return json.loads(data)
        except requests.HTTPError as e:
            raise ValueError(f"{e}") from e
        except json.JSONDecodeError as e:
            raise ValueError(e) from e

    def update(self):
        connection.get_db()


def download_with_progress(response, name) -> bytes:
    """ adds a download progress for debugging"""
    downloaded_size = 0
    chunks = []

    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
          chunks.append(chunk)
          downloaded_size += len(chunk)
          downloaded_mb = downloaded_size / (1024 * 1024)
          log_debug(f"Downloading \033[1m{name}\033[0m: \033[1m{downloaded_mb:.2f}\033[0m MB received\r", end="")

    sys.stdout.write("\n")

    return b"".join(chunks)


datasets = [
    DatasetMetadata(
        dataset_id="6a4cbf2c-c9b7-413a-86b1-e8f7081e2578",
        dataset_api="https://donnees.montreal.ca/api/3/",
    ),
]

def sync():
    for dataset in datasets:
        try:
            dataset.get_resource()
        except ValueError as e:
            log_err(f"Failed to sync {dataset.dataset_id}: {e}")
            log_warn(f"Skipping update for dataset {dataset.dataset_id}")
