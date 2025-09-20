import requests
from requests.auth import HTTPBasicAuth

# === Configuration ===
organization = ""
project = ""
pat = ""  # Keep this secure!

# Azure DevOps API endpoint
url = f"https://vsrm.dev.azure.com/{organization}/{project}/_apis/release/definitions?api-version=7.1-preview.4"

# Setup authentication
auth = HTTPBasicAuth('', pat)  # Username is blank, PAT is the password

# Make the request
response = requests.get(url, auth=auth)

# Check the response
if response.status_code == 200:
    data = response.json()
    release_definitions = data.get('value', [])
    
    print(f"\nFound {len(release_definitions)} release pipelines:\n")
    for rd in release_definitions:
        print(f"- ID: {rd['id']}, Name: {rd['name']}")
else:
    print(f"Failed to fetch release pipelines: {response.status_code}")
    print(response.text)
