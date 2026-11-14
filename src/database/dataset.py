from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
from multiprocessing import Value
import sys
from typing import Callable

import requests

from log import log_debug, log_err, log_info, log_ok, log_warn
from database import connection

@dataclass
class DatasetMetadata:
    sync_handler: Callable[[dict, str], None]
    dataset_id: str
    dataset_api: str
    cache_duration: timedelta = timedelta(hours=24)


    @property
    def package_url(self) -> str:
        return self.dataset_api + "action/package_show?id=" + self.dataset_id;

    def get_resource(self):
        log_info(f"Fetching dataset {self.dataset_id}")
        response = requests.get(self.package_url)
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

    def register_cache(self):
        with connection.get_db() as conn:
            expiration = (datetime.now() + self.cache_duration).isoformat()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dataset_metadata (dataset_id, dataset_url, fetched_date, expiration_date)
                VALUES (?, ?, ?, ?) ON CONFLICT(dataset_id) DO UPDATE SET
                    dataset_url = excluded.dataset_url,
                    fetched_date = excluded.fetched_date,
                    expiration_date = excluded.expiration_date
                """,(self.dataset_id, self.package_url, datetime.now().isoformat(), expiration))
            conn.commit()
            log_info(f"Created cache entry for dataset {self.dataset_id}")

    @property
    def cache_expired(self) -> bool:
        with connection.get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT expiration_date FROM dataset_metadata WHERE dataset_id = ?", (self.dataset_id,))
            row = cur.fetchone()

            if not row:
                return True

            return datetime.now() > datetime.fromisoformat(row["expiration_date"])

    def update(self):
        if not self.cache_expired:
            return

        log_info(f"Cache for dataset {self.dataset_id} is expired, updating")
        self.register_cache()
        self.sync_handler(self.get_resource(), self.dataset_id)

    def sync(self):
        self.update()



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


def general_sync_handler(geojson: dict, dataset_id: str):
    with connection.get_db() as conn:
        features = geojson["features"]
        total = len(features) - 1
        cur = conn.cursor()

        for index, feature in enumerate(features):
            properties = feature["properties"]
            price = None
            if properties["cout"].upper() == "GRATUIT": price = 0


            cur.execute(
                """
                INSERT INTO Attraction (
                    NameAttraction, Description, TypeAttraction, date_debut, date_fin,
                    PrixAttraction, Latitude, Longitude, dataset_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(NameAttraction, date_debut, dataset_id) DO UPDATE SET
                    Description = excluded.Description,
                    date_fin = excluded.date_fin,
                    TypeAttraction = excluded.TypeAttraction,
                    PrixAttraction = excluded.PrixAttraction,
                    Latitude = excluded.Latitude,
                    Longitude = excluded.Longitude,
                    dataset_id = excluded.dataset_id
            """,
                (
                    properties["titre"],
                    properties["description"],
                    properties["type_evenement"],
                    properties["date_debut"],
                    properties["date_fin"],
                    price,
                    properties["lat"],
                    properties["long"],
                    dataset_id,
                ),
            )

            log_info(f"Updating dataset {dataset_id}: \033[1m{index}/{total}\033[0m features updated\r", end="")

        sys.stdout.write("\n")
        conn.commit()
        log_ok(f"Dataset \033[1m{dataset_id}\033[0m updated")



datasets = [
    DatasetMetadata(
        dataset_id="6a4cbf2c-c9b7-413a-86b1-e8f7081e2578",
        dataset_api="https://donnees.montreal.ca/api/3/",
        cache_duration=timedelta(days=2),
        sync_handler=general_sync_handler
    ),
]


def sync():
    for dataset in datasets:
        try:
            dataset.sync()
        except ValueError as e:
            log_err(f"Failed to sync {dataset.dataset_id}: {e}")
            log_warn(f"Skipping update for dataset {dataset.dataset_id}")
