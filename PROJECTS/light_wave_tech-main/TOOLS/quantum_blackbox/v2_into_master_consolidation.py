import os
import glob
import json
import sqlite3
import ijson  # pip install ijson
from collections import defaultdict

# 1. Define the folder where your JSON files are saved
folder_path = r"C:\0\quantum_data\001__2nd_consolidation"
output_file = 'master_consolidated_results.json'
db_path = 'temp_aggregation.db'

if os.path.exists(db_path):
    os.remove(db_path) # Start fresh

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Setup SQLite Database with a COMPOSITE Primary Key
# By combining (src, dst) as the primary key, we allow multiple identical 'src' strings, 
# as long as the 'dst' strings paired with them are different.
cursor.execute('''CREATE TABLE IF NOT EXISTS unique_pairs 
                  (src TEXT, dst TEXT, count INTEGER, PRIMARY KEY (src, dst))''')

# Optimizations to make SQLite run blazing fast
cursor.execute('PRAGMA synchronous = OFF')
cursor.execute('PRAGMA journal_mode = MEMORY')

# 3. Find all JSON files
file_pattern = os.path.join(folder_path, '*.json')
json_files = glob.glob(file_pattern)
print(f"Found {len(json_files)} files. Processing stream...")

batch_size = 100000
# The dictionary key will now be a tuple: (src, dst)
local_buffer = defaultdict(int)
num_orig_items = 0

def flush_buffer_to_db():
    """Flushes the local Python memory dictionary into the SQLite database."""
    if not local_buffer: return
    
    # Flatten our dictionary items from ((src, dst), count) into a list of tuples: (src, dst, count)
    data_to_insert = [(src, dst, count) for (src, dst), count in local_buffer.items()]
    
    # Upsert logic: If the exact COMBINATION of src and dst already exists, add the counts together
    cursor.executemany('''
        INSERT INTO unique_pairs (src, dst, count) 
        VALUES (?, ?, ?)
        ON CONFLICT(src, dst) DO UPDATE SET count = count + excluded.count
    ''', data_to_insert)
    
    conn.commit()
    local_buffer.clear()

# 4. Stream and read files
for filepath in json_files:
    print(f"Streaming {os.path.basename(filepath)}...")
    
    with open(filepath, 'rb') as file:
        for item in ijson.items(file, 'item'):
            count = item.get("count", 0)
            
            if count > 2:  # Keeping your original filter logic
                src_str = item.get("src")
                dst_str = item.get("dst")
                
                # Use a tuple (src_str, dst_str) as the dictionary key
                local_buffer[(src_str, dst_str)] += count
                num_orig_items += 1
                
                # Flush to disk when batch size is reached to save memory
                if len(local_buffer) >= batch_size:
                    flush_buffer_to_db()

# Flush any remaining items in the buffer at the end
flush_buffer_to_db()
print(f"Processed {num_orig_items} matching items across all files.")

# 5. Stream results to output file
print("Writing optimized data to master file...")
cursor.execute("SELECT COUNT(*) FROM unique_pairs")
total_unique = cursor.fetchone()[0]

with open(output_file, 'w', encoding='utf-8') as out_file:
    out_file.write("[\n")
    
    # Select all three columns from our database
    cursor.execute("SELECT src, dst, count FROM unique_pairs")
    first_item = True
    
    # Fetch rows iteratively and write
    for row in cursor:
        if not first_item:
            out_file.write(",\n")
            
        # row[0] is src, row[1] is dst, row[2] is count
        out_file.write(json.dumps({
            "src": row[0], 
            "dst": row[1], 
            "count": row[2]
        }))
        first_item = False
        
    out_file.write("\n]\n")

print(f"Done! Reduced massive raw data down to {total_unique} unique (src, dst) pairs.")

# Cleanup
conn.close()
if os.path.exists(db_path):
    os.remove(db_path)
