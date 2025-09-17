# ORGANIZATION = "quartz7"
# PROJECTS = ["Quantum"]  # List all 10 projects

# AGENT_POOL = "SelfHosted-Mine"
import requests
import csv
from requests.auth import HTTPBasicAuth

organization = "quartz7"
personal_access_token = 
agent_pool_name = "Azure Pipelines"
api_version = "7.1"

# Base URL for APIs
base_url = f"https://dev.azure.com/{organization}"

# Auth for requests
auth = HTTPBasicAuth('', personal_access_token)

# Step 1: List all projects
projects_url = f"{base_url}/_apis/projects?api-version={api_version}"
projects_response = requests.get(projects_url, auth=auth)
projects_response.raise_for_status()
projects = projects_response.json().get('value', [])

result = []

for project in projects:
    project_name = project['name']

    # Step 2: List build definitions (pipelines) in the project
    defs_url = f"{base_url}/{project_name}/_apis/build/definitions?api-version={api_version}"
    defs_response = requests.get(defs_url, auth=auth)
    defs_response.raise_for_status()
    definitions = defs_response.json().get('value', [])

    for definition in definitions:
        definition_id = definition['id']
        definition_name = definition['name']

        # Step 3: Get full build definition to check agent pool
        def_detail_url = f"{base_url}/{project_name}/_apis/build/definitions/{definition_id}?api-version={api_version}"
        def_detail_response = requests.get(def_detail_url, auth=auth)
        def_detail_response.raise_for_status()
        def_detail = def_detail_response.json()

        # Step 4: Check queue (agent pool) name
        queue_info = def_detail.get("queue")
        if queue_info and queue_info.get("name", "").lower() == agent_pool_name.lower():
            result.append({
                "project": project_name,
                "pipeline": definition_name,
                "agent_pool": queue_info.get("name")
            })

# Step 5: Save results to CSV
csv_file = "pipelines_using_agent_pool_xyz.csv"
csv_columns = ["project", "pipeline", "agent_pool"]

with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_columns)
    writer.writeheader()
    writer.writerows(result)

print(f"Saved {len(result)} pipelines using agent pool '{agent_pool_name}' to {csv_file}")
