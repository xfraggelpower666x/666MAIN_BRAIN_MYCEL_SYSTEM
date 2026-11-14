import os
import random
from collections import Counter

def Random_Walk(num_items):
    top_signal_final = []

    videos = list(range(num_items))

    # Initial uniform weights
    weights = [5.0] * num_items

    # Track overall frequencies across all iterations for final signal
    overall_freq = Counter()

    # Run 150 iterations (Monte Carlo-like trials)
    for iteration in range(150):
        # Limited run: select 150 videos per iteration using current weights
        selections = random.choices(videos, weights=weights, k=50)
    
        # Update overall frequencies
        overall_freq.update(selections)
    
        # Get frequencies in this run
        run_freq = Counter(selections)
    
        # Increase weights for videos that appeared more than once (threshold for "more often")
        for video, count in run_freq.items():
            if count > 1:
                weights[video] *= 1.3  # Multiplier to boost future probability
    
        # Normalize weights to prevent explosion (optional but stabilizes)
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

    # Identify "signal": top 15% videos by overall frequency
    sorted_videos = overall_freq.most_common()
    top_signal = sorted_videos[:int(0.15 * len(videos))]  # Top 100

    # Print sample results
    print("Sample of top signal videos and their total frequencies:")
    for video, freq in top_signal[:50]:
        print(f"Video {video}: {freq} occurrences")
        top_signal_final.append(video)

    print("\nSample of final weights for top signal videos:")
    for video, _ in top_signal[:50]:
        print(f"Video {video}: weight {weights[video]:.10f}")

    return top_signal_final

def Random_Walk_Final(final_signal_list):
    top_signal_final = []

    videos = final_signal_list
    num_items = len(videos)
    print(f"num_items = {num_items}")

    # Mapping from video ID to its index in videos/weights
    video_to_index = {vid: i for i, vid in enumerate(videos)}

    # Initial uniform weights
    weights = [1.0] * num_items

    # Track overall frequencies across all iterations for final signal
    overall_freq = Counter()

    for iteration in range(200):
        selections = random.choices(videos, weights=weights, k=500)
        print(f"selections: {selections}")
    
        # Update overall frequencies
        overall_freq.update(selections)
    
        # Get frequencies in this run
        run_freq = Counter(selections)
    
        # Increase weights for videos that appeared more than once (threshold for "more often")
        for video, count in run_freq.items():
            if count > 1:
                idx = video_to_index[video]
                weights[idx] *= 1.333  # Multiplier to boost future probability
    
        # Normalize weights to prevent explosion (optional but stabilizes)
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        print(f"Iteration {iteration}: Min weight = {min(weights):.10f}, Max weight = {max(weights):.10f}")

    sorted_videos = overall_freq.most_common()
    top_signal = sorted_videos[:int(1.00 * len(videos))]

    for video, freq in top_signal:
        print(f"Video {video}: {freq} occurrences")
        top_signal_final.append(video)

    return top_signal_final


def Simul_Signal(video_filenames):
    randomized_videofiles = []
    num_videos = len(video_filenames)

    for simul_iter in range(2):
        for i in range(num_videos):
            random.shuffle(video_filenames)
            random_index = random.randint(0, num_videos-1)
            random_videofile = video_filenames[random_index]
            randomized_videofiles.append(random_videofile)

    num_randomized = len(randomized_videofiles)
    print(f"num_randomized = {num_randomized}")

    # Using dict.fromkeys() to remove duplicates while preserving order
    unique_filenames = list(dict.fromkeys(randomized_videofiles))

    num_unique = len(unique_filenames)
    print(f"num_unique = {num_unique}")

    # Now, catch duplicates: Count occurrences and filter for those >1
    filename_counts = Counter(randomized_videofiles)
    duplicates = {filename: count for filename, count in filename_counts.items() if 3 <= count <= 100}

    # Example outputs
    print(f"Total unique filenames: {len(unique_filenames)}")
    print(f"Number of duplicate filenames: {len(duplicates)}")
    print("Duplicates and their counts:")
    for filename, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):  # Sorted by count descending
        print(f"{filename}: {count} times")

    # Modified: List of filtered duplicate filenames, sorted by count descending (most occurrences first)
    duplicate_filenames_list = sorted(duplicates, key=lambda f: duplicates[f], reverse=True)

    num_duplicates = len(duplicate_filenames_list)
    print(f"num_duplicates = {num_duplicates}")
 
    return duplicate_filenames_list


input_filename = f"F:/Deep_Learning_Local/suno/suno_words_all_new.txt"
#input_filename = f"F:/Deep_Learning_Local/suno/montecarlo_words.txt"
with open(input_filename, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()
words = text.split('\n')
random.shuffle(words)


num_words_1 = len(words)
print(f"num_words_1 = {num_words_1}")

##__SIMUL__SIGNAL
#print("SIMUL_SIGNAL #1")
#words_1 = Simul_Signal(words)

#print("SIMUL_SIGNAL #2")
#words_2 = Simul_Signal(words)
#words = words_1 + words_2

#print("SIMUL_SIGNAL #3")
#words = Simul_Signal(words)
#num_words = len(words)
#print(f"num_words = {num_words}")

num_words = len(words)

print("RANDOM_WALK #1")
top_signal_1 = Random_Walk(num_words)
print("RANDOM_WALK #2")
top_signal_2 = Random_Walk(num_words)
print("RANDOM_WALK #3")
top_signal_3 = Random_Walk(num_words)
print("RANDOM_WALK #4")
top_signal_4 = Random_Walk(num_words)
print("RANDOM_WALK #5")
top_signal_5 = Random_Walk(num_words)
print("RANDOM_WALK #6")
top_signal_6 = Random_Walk(num_words)

print(top_signal_1)
print(top_signal_2)
print(top_signal_3)
print(top_signal_4)
print(top_signal_5)
print(top_signal_6)

top_signal_indices = top_signal_1 + top_signal_2 + top_signal_3 + top_signal_4 + top_signal_5 + top_signal_6
print(f"top_signal_indices_len: {len(top_signal_indices)}")

unique_top_signal_indices = list(dict.fromkeys(top_signal_indices))
print(f"unique_top_signal_indices_len: {len(unique_top_signal_indices)}")

print("RANDOM_WALK FINAL")
final_signal_indices = Random_Walk_Final(unique_top_signal_indices)

output_filename = f"F:/Deep_Learning_Local/suno/lyrics/montecarlo_words_5.txt"
with open(output_filename, "a", encoding="utf-8") as f:
    for i in range(10):
        unique_top_signal_words = []
        for index in unique_top_signal_indices:
            unique_top_signal_words.append(words[index])
            print(words[index])
            f.write(f"{words[index]}\n")














