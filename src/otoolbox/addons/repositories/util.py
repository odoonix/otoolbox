import json
import csv



# Define CSV columns
columns = [
    "organization",
    "repository",
    "branch",
    "title",
    "is_shielded",
    "linked_shielded_repo",
    "enable_in_runtime",
    "tags",
    "description"
]



def repository_list_josn_to_csv(csv_file_path=None, json_file_path=None):

    # Load JSON from file or directly
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)



    # Write CSV
    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        for item in data:
            writer.writerow({
                "organization": item.get("organization", ""),
                "repository": item.get("repository", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "tags": ",".join(item.get("tags", [])),
                "is_shielded": item.get("is_shielded", False),
                "linked_shielded_repo": item.get("linked_shielded_repo", ""),
                "enable_in_runtime": item.get("enable_in_runtime", False),
            })





def repository_list_csv_to_json(csv_file_path=None, json_file_path=None):
    """Convert CSV file to JSON file."""
    data = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert tags string to list
            tags = [tag.strip() for tag in row.get("tags", "").split(",") if tag.strip()]
            
            # Convert boolean fields
            is_shielded = row.get("is_shielded", "").strip().lower() == "true"
            enable_in_runtime = row.get("enable_in_runtime", "").strip().lower() == "true"
            
            # Build JSON object
            item = {
                "organization": row.get("organization", ""),
                "repository": row.get("repository", ""),
                "branch": row.get("branch", "") or None,
                "title": row.get("title", "") or None,
                "is_shielded": is_shielded,
                "linked_shielded_repo": row.get("linked_shielded_repo", "") or None,
                "enable_in_runtime": enable_in_runtime,
                "tags": tags,
                "description": row.get("description", "") or None
            }
            data.append(item)

    # Write JSON to file
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)







# repository_list_josn_to_csv(
#     csv_file_path="/home/maso/Projects/My/otoolbox/src/otoolbox/addons/repositories/repositories.csv",
#     json_file_path="/home/maso/Projects/My/otoolbox/src/otoolbox/addons/repositories/repositories.json"
# )


# repository_list_csv_to_json(
#     csv_file_path="/home/maso/Projects/My/otoolbox/src/otoolbox/addons/repositories/repositories.csv",
#     json_file_path="/home/maso/Projects/My/otoolbox/src/otoolbox/addons/repositories/repositories.json"
# )

