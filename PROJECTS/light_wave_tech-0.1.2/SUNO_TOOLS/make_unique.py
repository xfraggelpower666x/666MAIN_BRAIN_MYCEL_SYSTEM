import re

input_file_path  = 'F:/Deep_Learning_Local/suno/lyrics/combine/foo2.txt'
output_file_path = 'F:/Deep_Learning_Local/suno/lyrics/words_all_new___.txt'

#try:
#    with open(input_file_path, 'r', encoding='utf-8', errors='replace') as file:
#        lines = file.readlines()        
#        
#        # Using dict.fromkeys() to remove duplicates while preserving order
#        unique_lines = list(dict.fromkeys(lines))
#        
#    with open(output_file_path, 'w', encoding="utf-8") as writer:
#        writer.writelines(unique_lines)
#
#except FileNotFoundError:
#    print(f"Error: The file at {file_path} was not found.")





try:
    with open(input_file_path, 'r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines() 
        
        words_all = []
        for line in lines:
            words = re.findall(r'\b\w+\b', line)
            print(f"words_in_line: {len(words)}")
            
            for word in words:
                words_all.append(word)
          
        print(f"words_all: {len(words_all)}")
        
        # Using dict.fromkeys() to remove duplicates while preserving order
        unique_words = list(dict.fromkeys(words_all))
        unique_words = sorted(unique_words, key=len)

        print(f"unique_words: {len(unique_words)}")


    new_unique_words = []
    for word in unique_words:
        print(word)
        with open(output_file_path, "a", encoding="utf-8") as f:
           f.write(f"{word}\n")

except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")
