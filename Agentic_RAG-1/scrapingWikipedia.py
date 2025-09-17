import glob
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

from constants import SNAPSHOT_STATUS_READY

pd.options.mode.chained_assignment = None

load_dotenv()

postMethodHeaders = {
    "Authorization": "Bearer " + os.getenv("BRIGHTDATA_API_KEY"),
    "Content-Type": "application/json",
}

getMethodHeaders = {
    "Authorization": "Bearer " + os.getenv("BRIGHTDATA_API_KEY"),
}

keywords = pd.read_excel("keywords.xlsx")

fileExists = os.path.isfile(os.getenv("SNAPSHOT_STORAGE_FILE"))

if not fileExists:
    params = {
        "dataset_id": "gd_lr9978962kkjr3nx49",
        "include_errors": "true",
        "type": "discover_new",  # what does it truly mean is the type of scraoing operation to perform.
        "discover_by": "keyword",
    }

    jsonData = []

    for index in keywords.index:
        jsonData.append(
            {
                "keyword": keywords.loc[index, "Keyword"],
                "pages_load": str(keywords.loc[index, "Pages"]),
            }
        )

    response = requests.post(
        "https://api.brightdata.com/datasets/v3/trigger",
        json=jsonData,
        params=params,
        headers=postMethodHeaders,
    )

    result = json.loads(response.content)
    # print(f"debug: {result}")

    with open(os.getenv("SNAPSHOT_STORAGE_FILE"), "a") as f:
        f.write(str(result["snapshot_id"]))

else:
    files = glob.glob(os.getenv("DATASET_STORAGE_FOLDER") + "*")
    for f in files:
        os.remove(f)

    f = open(os.getenv("SNAPSHOT_STORAGE_FILE"), "r")
    snapshot_id = f.read()

    response = requests.get(
        "https://api.brightdata.com/datasets/v3/progress/" + snapshot_id,
        headers=getMethodHeaders,
    )
    status = response.json()["status"]

    print(f"status: {status}")

    isSnapshotReady = False

    if status == SNAPSHOT_STATUS_READY:
        isSnapshotReady = True
        print("Snapshot is ready...")
    else:
        print("Snapshot is not ready...")

    print("")

    if isSnapshotReady:
        print("== > All articles are ready - start writing data to datasets directory")

        response = requests.get(
            "https://api.brightdata.com/datasets/v3/snapshot/" + snapshot_id,
            headers=postMethodHeaders,
        )

        if not os.path.exists(os.getenv("DATASET_STORAGE_FOLDER")):
            os.makedirs(os.getenv("DATASET_STORAGE_FOLDER"))

        with open(os.getenv("DATASET_STORAGE_FOLDER") + "data.txt", "wb") as f:
            f.write(response.content)
    else:
        print("== > Not all articles are scraped yet - try again in a few minutes")
