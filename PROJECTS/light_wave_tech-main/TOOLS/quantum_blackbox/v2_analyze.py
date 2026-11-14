import os
import glob
import ijson
import ahocorasick

def main():
    # ---------------------------------------------------------
    # 1. LOAD THE 5 MILLION SOURCES EFFICIENTLY
    # ---------------------------------------------------------
    print("Loading 5 million source strings from text file...")
    
    # We use a dictionary to store the counts for each source
    src_counts = {}
    
    # Automaton is a highly optimized structure for substring searching millions of words
    A = ahocorasick.Automaton()
    
    with open('qbit_strings_data.txt', 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            src = line.strip()
            if src:
                src_counts[src] = 0
                # Add the word to our search engine. (Key, Value returned on match)
                A.add_word(src, src)

    print("Building the search automaton (this may take a minute)...")
    A.make_automaton()
    print(f"Loaded {len(src_counts)} unique sources into the search engine.")

    # ---------------------------------------------------------
    # 2. STREAM THE JSON FILES (Prevents 32GB+ OOM errors)
    # ---------------------------------------------------------
    folder_path = "./001__2nd_consolidation"
    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    print(f"Found {len(json_files)} JSON files. Processing...")

    for filepath in json_files:
        print(f" -> Streaming file: {filepath}")
        
        # ijson requires the file to be opened in binary mode ('rb')
        with open(filepath, 'rb') as file:
            
            # ijson.items streams the array '[{...}, {...}]' one object at a time.
            # This completely bypasses loading the 5GB file into RAM.
            for item in ijson.items(file, 'item'):
                dst_str = item.get("dst", "")
                count = item.get("count", 0)
                
                if not dst_str:
                    continue

                # --- SUBSTRING MATCHING ---
                # A.iter() instantly finds any of the 5 million sources hiding inside dst_str
                for end_index, found_src in A.iter(dst_str):
                    src_counts[found_src] += count
                    
                # --- EXACT MATCHING ---
                # If you ONLY wanted an EXACT match (dst == src) and NOT a substring, 
                # you can delete the A.iter() loop above and just use this:
                # if dst_str in src_counts:
                #     src_counts[dst_str] += count

    # ---------------------------------------------------------
    # 3. WRITE RESULTS TO A TEXT FILE
    # ---------------------------------------------------------
    output_filename = "analysis_results.txt"
    print(f"Processing complete! Filtering and writing results to {output_filename}...")

    # Filter out sources that were never found to save space
    found_sources = {src: count for src, count in src_counts.items() if count > 0}
    
    # Sort by highest count first
    sorted_results = sorted(found_sources.items(), key=lambda x: x[1], reverse=True)

    with open(output_filename, 'w', encoding='utf-8') as out_f:
        out_f.write(f"Total unique sources found in dst: {len(sorted_results)}\n")
        out_f.write("=" * 60 + "\n")
        
        for src, total_count in sorted_results:
            out_f.write(f"Count: {total_count:<10} | Source: '{src}'\n")

    print(f"Success! {len(sorted_results)} unique sources matched. Results saved to {output_filename}.")

if __name__ == "__main__":
    main()
