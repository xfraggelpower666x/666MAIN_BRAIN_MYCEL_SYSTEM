import os, glob
import ijson
import numpy as np

folder_path = r"C:\0\quantum_data\001"
counts = np.zeros(2**24, dtype=np.uint32)

json_files = glob.glob(os.path.join(folder_path, '*.json'))
print(f"DEBUG: Found {len(json_files)} JSON files in {folder_path}")

total_items_processed = 0

for filepath in json_files:
    print(f"Reading: {os.path.basename(filepath)}")

    # ijson requires files to be opened in binary mode ('rb')
    with open(filepath, 'rb') as file:
        # ijson.items streams array elements one by one without loading the whole file
        for item in ijson.items(file, 'item'):
            count = item.get("count", 0)
            bin_str = item.get("dst")
            key_int = int(bin_str, 2)  # e.g., "000000000000000000000101" -> 5
            counts[key_int] = count 
            total_items_processed += 1
           
            # Print the very first item found to prove it's reading correctly
            if total_items_processed == 1:
                print(f"DEBUG: Successfully read first item: {bin_str} -> {count}")

print("-------------------------------------------------")
print(f"Total key-value pairs processed: {total_items_processed}")
print(f"Unique non-zero items in array: {np.count_nonzero(counts)}")

if total_items_processed == 0:
    print("WARNING: No data was extracted! The output file will be empty.")
else:
    np.save('counts_data.npy', counts)
    print("Successfully saved populated counts_data.npy")

"""

import numpy as np

# Loads in ~0.05 seconds, uses 67 MB RAM
# Tip: add mmap_mode='r' to np.load() to use almost 0 MB of RAM and read directly from disk!
counts = np.load('counts_data.npy')

# Lookup count for a binary string:
my_key = "101011001111000010101100"
print(counts[int(my_key, 2)])

# If you need to iterate over non-zero items:
non_zero_indices = np.nonzero(counts)[0]
for idx in non_zero_indices:
    bin_str = f"{idx:024b}" # Convert integer back to 24-bit binary string if needed
    val = counts[idx]

"""