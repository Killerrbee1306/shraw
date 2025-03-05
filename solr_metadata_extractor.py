import requests
import json
import random
import os
import re

# Function to validate hostname (should start with http:// or https://)
def validate_hostname():
    while True:
        hostname = input("Enter Solr Hostname (default: http://localhost): ") or "http://localhost"
        if hostname.startswith("http://") or hostname.startswith("https://"):
            return hostname
        print("❌ Invalid hostname. Please enter a valid URL starting with http:// or https://.")

# Function to validate port number (should be a number between 1 and 65535)
def validate_port():
    while True:
        port = input("Enter Solr Port (default: 8983): ") or "8983"
        if port.isdigit() and 1 <= int(port) <= 65535:
            return port
        print("❌ Invalid port. Please enter a number between 1 and 65535.")

# Function to validate core name (should contain only alphanumeric characters or underscores)
def validate_core_name():
    while True:
        core_name = input("Enter Solr Core Name (default: mycore): ") or "mycore"
        if re.match(r"^[a-zA-Z0-9_]+$", core_name):
            return core_name
        print("❌ Invalid core name. It should only contain letters, numbers, or underscores.")

# Get validated user inputs
hostname = validate_hostname()
port = validate_port()
core_name = validate_core_name()

# Construct Solr API URLs
base_url = f"{hostname}:{port}/solr/{core_name}"

try:
    # Check if Solr is reachable
    solr_status_url = f"{hostname}:{port}/solr/admin/info/system?wt=json"
    response = requests.get(solr_status_url, timeout=5)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ Error: Could not connect to Solr. Please check the URL and try again.")
    print(f"Details: {e}")
    exit(1)

try:
    # Fetch core metadata
    metadata_url = f"{hostname}:{port}/solr/admin/cores?action=STATUS&core={core_name}&wt=json"
    metadata_response = requests.get(metadata_url, timeout=5)
    metadata_response.raise_for_status()
    metadata = metadata_response.json()

    # Verify if the core exists
    if core_name not in metadata["status"]:
        print(f"❌ Error: Core '{core_name}' does not exist in Solr.")
        exit(1)

    # Extract metadata fields
    index_size = metadata["status"][core_name]["index"].get("sizeInBytes", "Unknown")
    num_docs = metadata["status"][core_name]["index"].get("numDocs", 0)

except requests.exceptions.RequestException as e:
    print(f"❌ Error: Failed to fetch Solr core metadata. Details: {e}")
    exit(1)

try:
    # Fetch documents
    query_url = f"{base_url}/select?q=*:*&rows=100&wt=json"
    query_response = requests.get(query_url, timeout=5)
    query_response.raise_for_status()
    docs = query_response.json().get("response", {}).get("docs", [])

    # Extract 2 random documents (if available)
    random_docs = random.sample(docs, min(2, len(docs)))

    # Process documents to extract only first-level fields
    processed_docs = [
        {key: doc[key] for key in doc if not key.startswith("_")}  # Exclude system fields
        for doc in random_docs
    ]

except requests.exceptions.RequestException as e:
    print(f"❌ Error: Failed to fetch documents from Solr. Details: {e}")
    exit(1)

# Prepare metadata output
output_data = {
    "core_name": core_name,
    "num_documents": num_docs,
    "index_size_bytes": index_size,
    "sample_documents": processed_docs
}

# Dynamically set the file path to the current working directory
output_path = os.path.join(os.getcwd(), "solr_metadata.json")

try:
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"✅ Metadata extraction complete! JSON saved at: {output_path}")
except IOError as e:
    print(f"❌ Error: Failed to save metadata to file. Details: {e}")
    exit(1)
