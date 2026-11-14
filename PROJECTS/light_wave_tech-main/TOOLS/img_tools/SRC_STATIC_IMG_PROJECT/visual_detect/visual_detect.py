# pip install ImageHash

import os
import shutil
from PIL import Image
import imagehash

# Folders to use
source_folder     = "./my_images"
duplicates_folder = "./my_images/duplicates"

# Create the duplicates folder if it doesn't exist
os.makedirs(duplicates_folder, exist_ok=True)

# Dictionary to store the hashes we've already seen
# Format: { hash_object: "filename.jpg" }
seen_hashes = {}

# Threshold for similarity. 
# 0 = exact match. 
# 1 to 4 = minor changes (like JPG compression or slight resize)
THRESHOLD = 10

for filename in os.listdir(source_folder):
    file_path = os.path.join(source_folder, filename)
    
    # Skip folders and non-images
    if not os.path.isfile(file_path) or not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        continue

    try:
        # Open image and compute the perceptual hash
        img = Image.open(file_path)
        current_hash = imagehash.phash(img)
        
        is_duplicate = False
        
        # Compare current_hash to all previously seen hashes
        for seen_hash, original_file in seen_hashes.items():
            # Subtracting two hashes gives the "Hamming Distance" (number of differences)
            distance = current_hash - seen_hash
            print(f"DISTANCE: {distance}")
            
            if distance <= THRESHOLD:
                print(f"Duplicate found: {filename} is similar to {original_file} (Distance: {distance})")
                is_duplicate = True
                break
                
        if is_duplicate:
            # Move the duplicate file
            #shutil.move(file_path, os.path.join(duplicates_folder, filename))
            #shutil.move(file_path, os.path.join(duplicates_folder, filename))

            original_file_full_path = os.path.join(source_folder, original_file)
            print(f"IS_DUPLICATE: {file_path} | {original_file_full_path}")
            duplicate_file = f"{original_file}_{filename}"
            shutil.move(file_path, os.path.join(duplicates_folder, duplicate_file))
            shutil.move(original_file_full_path, os.path.join(duplicates_folder, original_file))

#            shutil.copy2(file_path, os.path.join(duplicates_folder, filename))
#            shutil.copy2(original_file_full_path, os.path.join(duplicates_folder, original_file))
        else:
            # First time seeing this image structure, save its hash
            seen_hashes[current_hash] = filename

    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("Done scanning!")