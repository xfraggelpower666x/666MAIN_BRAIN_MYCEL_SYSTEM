import numpy as np

counts = np.load('counts_data.npy')

# 1. Get the integer indexes of strings that actually exist
valid_indexes = np.nonzero(counts)[0]

# 2. Make a random draw (without providing probabilities, they are treated equally)
drawn_index = np.random.choice(valid_indexes)

# 3. Convert back to string
drawn_string = f"{drawn_index:024b}"

print(f"Randomly picked an existing item: {drawn_string}")
print(f"This item had a count of: {counts[drawn_index]}")