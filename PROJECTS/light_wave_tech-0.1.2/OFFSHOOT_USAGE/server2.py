import os
import json
import random
from collections import Counter
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

def load_neural_indices_json(filepath, ceiling=None):
    try:
        print(f"Loading neural_indices from {filepath}")
        with open(filepath, 'r') as f:
            indices = json.load(f)
            
            # If a ceiling is provided, filter the list
            if ceiling is not None:
                # Keep only the indices that are within the valid range
                filtered_indices = [idx for idx in indices if idx < ceiling]
                
                # Optional: Let the user know how many indices were filtered out
                if len(filtered_indices) < len(indices):
                    print(f"Filtered out {len(indices) - len(filtered_indices)} out-of-bounds indices.")
                    
                return filtered_indices
            
            return indices

    except json.JSONDecodeError as e:
        # This triggers if the file was corrupted on the drive!
        print(f"CORRUPTION DETECTED: The file {filepath} is not valid JSON.")
        print(f"Specific error: {e}")
        return None
    except FileNotFoundError:
        print("File not found.")
        return None

"""def load_neural_indices_json(filepath):
    try:
        print(f"Loading neural_indices from {filepath}")
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # This triggers if the file was corrupted on the drive!
        print(f"CORRUPTION DETECTED: The file {filepath} is not valid JSON.")
        print(f"Specific error: {e}")
        return None
    except FileNotFoundError:
        print("File not found.")
        return None"""

# 1. CREATE A GLOBAL CACHE IN MEMORY
MASTER_FILE_LIST = []

def load_media_files():
    """
    Reads the hard drive ONCE and caches the file paths in memory.
    """
    print("Scanning media folders... Please wait.")
    allowed_extensions = ('.mp4', '.webm', '.ogg', '.jpg', '.jpeg', '.png', '.gif', '.webp')
    files = []
    
    # Helper to safely scan directories without crashing if one is missing
    def scan_dir(directory, prefix):
        try:
            return [f"{prefix}{f}" for f in os.listdir(directory) if f.lower().endswith(allowed_extensions)]
        except FileNotFoundError:
            print(f"[WARNING] Missing Folder: {directory}")
            return []

    # Read the disk
    files.extend(scan_dir('./video_1', 'video_1/'))
    files.extend(scan_dir('./video_1', 'video_1/'))
    files.extend(scan_dir('./video_1', 'video_1/'))
    #files.extend(scan_dir('./video_2', 'video_2/'))
    #files.extend(scan_dir('./video_3', 'video_3/'))
    #files.extend(scan_dir('./image', 'image/'))

    random.shuffle(files)
    
    print(f"Scan complete! Cached {len(files)} media files in memory.")
    return files

def load_neural_json_list():
    """
    Reads the hard drive ONCE and caches the file paths in memory.
    """
    print("Scanning neural folder... Please wait.")
    allowed_extensions = ('.json')
    files = []
    
    # Helper to safely scan directories without crashing if one is missing
    def scan_dir(directory, prefix):
        try:
            return [f"{prefix}{f}" for f in os.listdir(directory) if f.lower().endswith(allowed_extensions)]
        except FileNotFoundError:
            print(f"[WARNING] Missing Folder: {directory}")
            return []

    # Read the disk
    files.extend(scan_dir('./neural_indices_json', 'neural_indices_json/'))
    
    print(f"Scan complete! Cached {len(files)} neural files in memory.")
    return files

def load_neural_indices(neural_json_filepaths, num_media_items):
    neural_indices = []
    random.shuffle(neural_json_filepaths)

    for json_filepath in neural_json_filepaths:
        neural_indices.extend(load_neural_indices_json(json_filepath, ceiling=num_media_items)) #ceiling=None)) 
    print(f"neural_indices: {len(neural_indices)}")

    counts = Counter(neural_indices)
    #sorted_list = sorted(neural_indices, key=lambda x: counts[x])
    sorted_list = sorted(neural_indices, key=lambda x: -counts[x])
    #sorted_list = sorted(neural_indices, key=lambda x: x % 10)
    deduplicated = list(dict.fromkeys(sorted_list))
    print(f"deduplicated: {len(deduplicated)}")

    #top_10_million = deduplicated[:10_000_000]
    #with open("top_indices.json", "w") as f:
    #    json.dump(deduplicated, f)

    return deduplicated

    #neural_indices = list(dict.fromkeys(neural_indices))
    #return neural_indices

MASTER_NEURAL_INDEX_COUNTER = 0

def get_neural_index(neural_indices_list):
    global MASTER_NEURAL_INDEX_COUNTER
    print(f"{MASTER_NEURAL_INDEX_COUNTER}/{len(neural_indices_list)}")
    MASTER_NEURAL_INDEX_COUNTER += 1
    if MASTER_NEURAL_INDEX_COUNTER > len(neural_indices_list)-1:
        MASTER_NEURAL_INDEX_COUNTER = 0
    return neural_indices_list[MASTER_NEURAL_INDEX_COUNTER]

#    return random.choice(neural_indices_list)

class MediaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global MASTER_FILE_LIST
        global MASTER_NEURAL_INDICES

        try:
            # 1. Parse the path BEFORE checking the routes
            parsed_path = urlparse(self.path)
            print(f"parsed_path: {parsed_path}")

            if parsed_path.path == '/api/media':
                query = parse_qs(parsed_path.query)
                print(f"query: {query}")                

                limit = int(query.get('limit', ['50'])[0]) # Defaults to 50 items
                print(f"limit: {limit}")
                
                files_to_send = []
                num_total_files = len(MASTER_FILE_LIST)-1
                print(f"num_total_files = {num_total_files}")

                # Only generate the requested chunk
                for _ in range(limit): 
                    index = get_neural_index(MASTER_NEURAL_INDICES)
                    if index > num_total_files:
                        index = random.randint(1, num_total_files-1)
                    print(f"index: {index}")                    
                    files_to_send.append(MASTER_FILE_LIST[index])
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(files_to_send).encode('utf-8'))

            elif self.path == '/api/refresh':
                # 3. OPTIONAL: A way to force the server to re-scan folders dynamically
                MASTER_FILE_LIST = load_media_files()
            
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "Folders rescanned successfully!", 
                    "total_files": len(MASTER_FILE_LIST)
                }).encode('utf-8'))
            else:
                super().do_GET()
                
        except ConnectionError:
            # Ignore browser cancellation errors during fast scrolling
            pass
        except FileNotFoundError as e:
            # Safety check: If a folder is missing, print it in the console instead of crashing
            print(f"\n[ERROR] Missing Folder: {e}")
            self.send_response(500)
            self.end_headers()

if __name__ == '__main__':
    PORT = 8001
    MASTER_FILE_LIST = load_media_files()
    MASTER_NEURAL_JSON_LIST = load_neural_json_list()
    MASTER_NEURAL_INDICES = load_neural_indices(MASTER_NEURAL_JSON_LIST, len(MASTER_FILE_LIST))

    print(f"Serving local media at http://localhost:{PORT}")
    print("Make sure you have a 'video' folder and an 'image' folder in this directory!")
    print("Press Ctrl+C to stop.")
    ThreadingHTTPServer(('', PORT), MediaHandler).serve_forever()