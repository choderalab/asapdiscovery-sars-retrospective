import os
import tempfile
import requests
import json

url = "https://fragalysis.diamond.ac.uk/api/download_structures/"

with open("fragalysis_download_api_call.json", "r") as f:
    data = json.load(f)

# First get the url of the particular file using the copied json
r = requests.post(
    "https://fragalysis.diamond.ac.uk/api/download_structures/", json=data
)
print(r)
if r.ok:
    # Next, use the returned url to download the actual zip file
    file_url = r.json()["file_url"]
    r = requests.get(
        "https://fragalysis.diamond.ac.uk/api/download_structures?file_url=%s"
        % file_url,
        allow_redirects=True,
    )
    print(r)
    if r.ok:
        with open(os.path.basename(file_url), mode="wb") as f:
            f.write(r.content)
