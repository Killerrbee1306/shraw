import json

# ---- Load the original JSON file ----
input_file = "solr_metadata2.json"  # Change this if needed
output_file = "solr_fixed.json"  # This will be used for indexing

with open(input_file, "r", encoding="utf-8") as file:
    raw_data = json.load(file)

# ---- Extract & Transform Documents ----
documents = []

for index_entry in raw_data.get("data", {}).get("Index", []):
    for doc in index_entry.get("Documents", []):
        processed_doc = {"id": doc["document_id"]}  # Ensure Solr has a unique ID
        
        for field in doc.get("fieldTypes", []):
            field_name = field["fieldName"]
            field_value = field["value"]
            
            # Handle lists of objects (e.g., purchase history)
            if isinstance(field_value, list) and isinstance(field_value[0], dict):
                field_value = [json.dumps(item) for item in field_value]  # Convert to JSON strings
            
            # Handle nested dictionaries (e.g., preferences)
            elif isinstance(field_value, dict):
                field_value = json.dumps(field_value)  # Store entire object as a JSON string

            # Remove sensitive data fields
            if field_name not in ["sensitive_data"]:
                processed_doc[field_name] = field_value
        
        # Append cleaned document
        documents.append(processed_doc)

# ---- Save the transformed JSON ----
with open(output_file, "w", encoding="utf-8") as outfile:
    json.dump(documents, outfile, indent=4)

print(f"✅ JSON transformation complete! Saved as '{output_file}'")
