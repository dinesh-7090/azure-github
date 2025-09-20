import requests
from requests.auth import HTTPBasicAuth

# === Configuration ===
organization = ""
project = ""
pat = ""  # Keep this secure!

# Base URLs
release_base_url = f"https://vsrm.dev.azure.com/{organization}/{project}/_apis/release/definitions"
queue_base_url = f"https://dev.azure.com/{organization}/_apis/distributedtask/queues"

# API versions
release_api_version = "7.1-preview.4"
queue_api_version = "7.1-preview.1"

# Authentication
auth = HTTPBasicAuth('', pat)

# Cache for queueId -> agent pool name
queue_cache = {}

# Helper: Get agent pool name by queueId
def get_agent_pool_name(queue_id):
    if queue_id in queue_cache:
        return queue_cache[queue_id]

    url = f"{queue_base_url}/{queue_id}?api-version={queue_api_version}"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        queue_data = response.json()
        pool_name = queue_data.get("pool", {}).get("name", "Unknown")
        queue_cache[queue_id] = pool_name
        return pool_name
    else:
        return "Unknown or Inaccessible"

# Step 1: Get all release pipelines
def get_release_pipelines():
    url = f"{release_base_url}?api-version={release_api_version}"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json().get("value", [])

# Step 2: Get details of a single pipeline (including stages)
def get_pipeline_details(definition_id):
    url = f"{release_base_url}/{definition_id}?api-version={release_api_version}"
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
    if not environments:
        print("  ⚠️ No stages found.\n")
        continue

    for env in environments:
        stage_name = env.get('name')
        deploy_phases = env.get("deployPhases", [])

        agent_pool_name = "Unknown"
        for phase in deploy_phases:
            deployment_input = phase.get("deploymentInput", {})
            queue_id = deployment_input.get("queueId")
            if queue_id:
                agent_pool_name = get_agent_pool_name(queue_id)
                break  # One agent pool per stage is typical

        print(f"  🔹 Stage: {stage_name}")
        print(f"     🛠 Agent Pool: {agent_pool_name}")

    print()