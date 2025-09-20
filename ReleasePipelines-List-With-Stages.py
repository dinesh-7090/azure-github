import requests
from requests.auth import HTTPBasicAuth

# === Configuration ===
organization = ""
project = ""
pat = ""  # Keep this secure!


# Base URL
base_url = f"https://vsrm.dev.azure.com/{organization}/{project}/_apis/release/definitions"
api_version = "7.1-preview.4"

# Authentication
auth = HTTPBasicAuth('', pat)

# Step 1: Get all release pipelines
def get_release_pipelines():
    url = f"{base_url}?api-version={api_version}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json().get("value", [])

# Step 2: Get details of a single pipeline (including stages)
def get_pipeline_details(definition_id):
    url = f"{base_url}/{definition_id}?api-version={api_version}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()

# Main
pipelines = get_release_pipelines()

print(f"Found {len(pipelines)} release pipelines.\n")

for pipeline in pipelines:
    pipeline_id = pipeline['id']
    pipeline_name = pipeline['name']
    details = get_pipeline_details(pipeline_id)

    print(f"📦 Pipeline: {pipeline_name} (ID: {pipeline_id})")

    environments = details.get("environments", [])
    if environments:
        for env in environments:
            print(f"  🔹 Stage: {env.get('name')} (ID: {env.get('id')})")
    else:
        print("  ⚠️ No stages found.")

    print()