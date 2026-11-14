from collections import defaultdict
import json
import glob
import os

folder_path = "./001"

# Find and loop through all JSON files in the folder
file_pattern = os.path.join(folder_path, '*.json')
json_files = glob.glob(file_pattern)

print(f"Found {len(json_files)} files. Processing...")

num_orig_items = 0
for filepath in json_files:
    with open(filepath, 'r') as file:
        json_data = json.load(file)
        
unique_dst = defaultdict(int)

# Process the data
for item in json_data:
    dst_str = item["dst"]
    count = item["count"]
    unique_dst[dst_str] += count

#    if count <= 8:
#        unique_dst[dst_str] += count
    
# ==========================================
# PRINTING THE RESULTS
# ==========================================

print(f"Total unique dst_str: {len(unique_dst)}")
for dst, total_count in sorted(unique_dst.items(), key=lambda x: x[1], reverse=True)[:500]:
    print(f"    - dst: '{dst}' | Total count: {total_count}")
print("\n" + "-"*40 + "\n")

