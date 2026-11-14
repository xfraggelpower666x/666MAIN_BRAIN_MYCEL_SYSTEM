import os
import glob
import json
import sqlite3
import ijson  # You must install this: pip install ijson
from collections import defaultdict

# 1. Define the folder where your JSON files are saved
folder_path = r"C:\0\quantum_data\001"
output_file = 'master_consolidated_results.json'
db_path = 'temp_aggregation.db'

# 2. Setup SQLite Database for zero-memory disk aggregation
# This allows us to handle infinite unique string counts without crashing RAM
if os.path.exists(db_path):
    os.remove(db_path) # Start fresh

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS unique_pairs 
                  (dst TEXT PRIMARY KEY, count INTEGER)''')

# Optimizations to make SQLite run blazing fast
cursor.execute('PRAGMA synchronous = OFF')
cursor.execute('PRAGMA journal_mode = MEMORY')

# 3. Find all JSON files
file_pattern = os.path.join(folder_path, '*.json')
json_files = glob.glob(file_pattern)
print(f"Found {len(json_files)} files. Processing stream...")

batch_size = 100000  # How many records to hold in memory before flushing to disk
local_buffer = defaultdict(int)
num_orig_items = 0

def flush_buffer_to_db():
    """Flushes the local Python memory dictionary into the SQLite database."""
    if not local_buffer: return
    
    # Upsert logic: If the binary string 'dst' already exists, add to its total count
    cursor.executemany('''
        INSERT INTO unique_pairs (dst, count) 
        VALUES (?, ?)
        ON CONFLICT(dst) DO UPDATE SET count = count + excluded.count
    ''', local_buffer.items())
    conn.commit()
    local_buffer.clear()

# 4. Stream and read files
for filepath in json_files:
    print(f"Streaming {os.path.basename(filepath)}...")
    
    # ijson requires files to be opened in binary mode ('rb')
    with open(filepath, 'rb') as file:
        # ijson.items streams array elements one by one without loading the whole file
        for item in ijson.items(file, 'item'):
            count = item.get("count", 0)
            
            if count > 2:
                dst_str = item.get("dst")
                local_buffer[dst_str] += count
                num_orig_items += 1
                
                # Flush to disk when batch size is reached to save memory
                if len(local_buffer) >= batch_size:
                    flush_buffer_to_db()

# Flush any remaining items in the buffer at the end
flush_buffer_to_db()
print(f"Processed {num_orig_items} matching items across all files.")

# 5. Stream results to output file
# Instead of holding a giant list and using json.dump(), we manually write 
# the JSON structure line by line.
print("Writing optimized data to master file...")
cursor.execute("SELECT COUNT(*) FROM unique_pairs")
total_unique = cursor.fetchone()[0]

with open(output_file, 'w', encoding='utf-8') as out_file:
    out_file.write("[\n")
    
    cursor.execute("SELECT dst, count FROM unique_pairs")
    first_item = True
    
    # Fetch rows iteratively and write
    for row in cursor:
        if not first_item:
            out_file.write(",\n")
            
        # Write compactly without indent=4 to drastically save file space
        out_file.write(json.dumps({"dst": row[0], "count": row[1]}))
        first_item = False
        
    out_file.write("\n]\n")

print(f"Done! Reduced massive raw data down to {total_unique} unique pairs.")

# Cleanup
conn.close()
if os.path.exists(db_path):
    os.remove(db_path) # Delete temporary database to free space