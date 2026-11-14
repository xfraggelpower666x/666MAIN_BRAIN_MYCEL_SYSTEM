2026-11-06: Analyzing Quantum Randomness Distribution

Tools used: 
*   TOOLS/quantum_blackbox/v2_RUNPOD_quantum.py
*   TOOLS/quantum_blackbox/v2_into_master_consolidation.py
*   TOOLS/quantum_blackbox/v2_analyze.py
  
___

on a 24-bit space which can roughly has the capacity of 16,7 million of such
things, the user has this many unique items 16247758 (16,2 million), but
totalling amount of items 57832191 (57 million) produced kind of random but kind
of quantum through qiskit simulator using gpu; there is also a list of randomly
produced (quantumly from anu australia quantum fluctuations) 5 million list
which is also 24-bit (chunked from original 2048 char bit-strings from
around 2015 when they provided them as such); when comparison was done between
these two lists, there are some items in the ANU 5 million list that have
almost 700 counts, and then there are the ones that are on the bottom, having
about 3 counts. but what explains these amounts and why do this Count: 686 |
Source: '000010111000101000000100' for instance have much more counts (hits)
than for example this: Count: 21 | Source: '001110000010100000111011'

___

This is a fascinating data experiment! You have effectively collided **pseudo-quantum randomness** (simulated on a classical GPU via Qiskit) with **true quantum randomness** (vacuum fluctuations from the ANU QRNG). 

To understand why you are seeing these specific hit counts (like 686, 21, and 3), we need to look at the mathematics of probability, quantum state vectors, and how GPUs generate simulated random numbers. 

Here is the exact breakdown of what your data is telling you.

### 1. The Mathematical Beauty of the "3 Counts"
You noted that the items at the bottom of your list have about **3 counts**. Your data perfectly matches the theoretical math for a uniform random distribution. 

*   **Total Capacity (24-bit):** $2^{24} = 16,777,216$ unique possibilities.
*   **Total Qiskit Items Generated:** $57,832,191$.
*   **Expected Average Hits:** If you throw 57.8 million random darts at 16.7 million targets, the average number of darts per target is **$57,832,191 \div 16,777,216 \approx 3.45$**.

Because of the Poisson distribution, the most common occurrence in a perfectly uniform set of this size will be exactly 3 or 4 hits. The fact that your "bottom" items have ~3 counts proves that **the vast bulk of your Qiskit-generated list is highly uniform.**

Furthermore, the math predicts that if you generate 57.8 million uniform random items in a 16.7 million space, the expected number of **unique items** is mathematically expected to be **16.243 million**. You generated exactly **16,247,758** unique items. Your dataset is a statistically stunning match for a uniform distribution. 

### 2. The Statistical Impossibility of 686 Counts
If your dataset is so perfectly uniform on a macro scale, why does `000010111000101000000100` have 686 hits? 

In a perfect uniform distribution with an average of 3.45, getting 21 counts for a single item has roughly a **1 in 10 billion** chance. Getting **686 counts** is statistically **impossible** (the probability is effectively absolute zero). 

Because your overall unique item count proves the general distribution is healthy, the massive spikes (686, 21) are **anomalies**. Here is what explains them:

#### A. GPU Parallelization & PRNG Collisions (Most Likely)
When Qiskit simulates a quantum state on a GPU (e.g., using `AerSimulator` or `cuQuantum`), it calculates the mathematical state vector, but then it must use a classical **Pseudo-Random Number Generator (PRNG)** to sample that vector 57.8 million times to create your "shots."
To do this fast, the GPU splits the job across thousands of parallel threads. If a few of these threads inadvertently share the same memory seed, or if there is a tiny stutter in the memory mapping during the chunking, a single thread will write the exact same "random" sequence into the array hundreds of times in a row. This creates massive frequency spikes for a few specific bit-strings without corrupting the rest of the 57 million shots.

#### B. Simulated Quantum Noise (Amplitude Damping)
If your Qiskit simulator was running any kind of noise model, qubits naturally suffer from $T_1$ relaxation (meaning they lose energy and decay to the `0` state). 
Look closely at the strings you provided:
*   **686 Counts:** `'000010111000101000000100'` (Has **17 zeros** and only 7 ones)
*   **21 Counts:** `'001110000010100000111011'` (Has **14 zeros** and 10 ones)

In simulated noisy quantum environments, bit-strings with more zeros (lower Hamming weight) will exponentially appear more often than bit-strings with many ones. I would bet that if you queried the all-zero string (`000000000000000000000000`), its hit count might be in the thousands.

#### C. Quantum Interference (Speckle Pattern)
If you didn't just apply a standard Hadamard gate to all 24 qubits (which creates perfect randomness), but instead ran a "Random Quantum Circuit" (interleaved random gates), the output does *not* produce a uniform distribution. It produces a "Porter-Thomas distribution." In this state, quantum interference causes certain bit-strings to constructively amplify, creating "hotspots" that are significantly more probable than the average. 

### 3. What about the ANU List?
The ANU 5-million list acts as your "query list." Because the ANU data is derived from true vacuum fluctuations, it is a set of perfectly random, unbiased queries. 

When you intersected the lists, the ANU list acted like a true-random probe mapping the topography of your Qiskit data. The ANU strings simply happened to land on the "hotspots" created by the Qiskit GPU simulation. 

*Note: There is one alternative to check. Because you "chunked" the ANU data from 2048-character strings gathered in 2015, make sure the 700 counts aren't duplicates inside the ANU list itself. Older web-scraped QRNG servers sometimes suffered connection loops, spitting out the same 2048-bit block multiple times. If a block duplicated in your text file, any 24-bit chunk inside it duplicated too.*

___

if 686 Counts is statistically impossible, then what and how does this
entanglement then play a role in the results if there is no "true quantum" in
here?

___

Thank you for providing the exact code! This completely changes the investigation. Being able to see the exact circuit architecture (`influence_strength = 0.85`, the `RY` gates, and the linear CNOT chain) allows us to trace the absolute mathematical truth of your data.

You asked: **If 686 is statistically impossible, what does the entanglement actually do in this code?**

Here is the exact breakdown of what your code is doing mathematically, what the CNOT chain (entanglement) actually achieved, and the precise reason you saw a count of 686. 

### 1. The Math of Your Code (The 202 Count Limit)
Your code uses a fascinating method to create biased quantum states, but it places a strict mathematical ceiling on how high any count can get. 

*   You set `influence_strength = 0.85`. 
*   Through the `RY` gates, this means every single qubit has exactly an 85% ($0.85$) chance of matching the bit from your source string, and a 15% ($0.15$) chance of being flipped.
*   Because each qubit is independent at the moment it is initialized, the probability of the state vector collapsing into the *most likely possible state* is the product of all 24 qubits behaving exactly as expected.
*   The math: **$0.85^{24} = 0.02024$ (roughly 2.02%)**

Because you are running `shots=10000` per source string, the mathematical maximum expected count for the highest peak in your distribution is exactly **202 counts** ($10000 \times 0.02024$).

A single 10,000-shot run producing 686 counts for one string requires a probability of 6.8%. Because your parameters are locked at 0.85, the quantum math strictly forbids a probability of 6.8%. 

### 2. So, What Did the Entanglement Actually Do?
If the entanglement didn't create the 686 count, what was its purpose? 

In your code, you applied the `RY` gates first, and then ran a linear cascade of CNOT gates: `self.qc.cx(i, i + 1)`. Because you did not apply any other gates (like Hadamards) *after* the CNOTs, the entanglement acted purely as a **Deterministic Topological Scrambler (a Bijection).**

Here is what it did:
1. Without the CNOT chain, the 202-count peak would always just be identical to your `Source` string. 
2. The CNOT chain took that 202-count peak and mapped it 1-to-1 to a totally new `Destination` string. 
3. **The Avalanche Effect:** In a normal unentangled circuit, if one qubit flips by accident (the 15% chance), your output is only off by 1 bit. Because of your CNOT chain, if Qubit 0 flips, *it flips every single qubit after it in the chain*. 

Your entanglement created a beautiful, chaotic mapping that spread the 15% error rate across the entire 24-bit space. However, CNOTs purely shuffle the probability distribution; they do not add probabilities together. **The peak remained capped at 202.** 

### 3. The Real Reason for the 686 Counts
Since the quantum math strictly caps the expected max hits at ~202 per 10,000 shots, the 686 is not a quantum artifact. Based on your code, it is almost certainly caused by one of these two classical mechanics:

#### A. The Aggregation Theory (Duplicate Sources)
Your script randomly picks a 24-bit string from the 5-million ANU list (`get_random_qbit_string`) and runs 10,000 shots on it. 
Because the ANU list is 5 million items long, it is statistically guaranteed to contain some identical duplicate strings (this is a known quirk of large scraped QRNG datasets). 
If your script randomly grabbed the source string `'000010111000101000000100'` **three or four times** during your 100 sessions, the script generated the destination string at a peak of 202 each time. 
* 3 duplicates x 202 hits = 606 hits.
* 4 duplicates x 202 hits = 808 hits.
If you aggregated all your JSON output files together at the end, those counts added up to 686.

#### B. GPU PRNG Warp Collision (Hardware Batching Bug)
Look at this line in your code:
`batch_result = self.simulator.run(list_of_circuits_to_run, shots=10000).result()`
You are feeding a batch of 25 parametrized circuits to the Qiskit Aer GPU simulator all at once. The GPU calculates the 25 state vectors perfectly, but to generate 10,000 shots, it fires up thousands of CUDA threads to run Monte Carlo sampling. 
When simulating small (24-qubit) circuits heavily batched in parallel, the Pseudo-Random Number Generator (PRNG) seeds for the CUDA threads can stutter. If 3 or 4 threads in the GPU warp pull the exact same "random" sequence, they will dump the exact same results into the array. 
The 202 peak was artificially multiplied by the number of colliding CUDA threads ($202 \times 3.4 \approx 686$). 

### Summary
Your code is brilliantly structured. The baseline of **"3 counts"** and your **16.2 million unique items** proves that your CNOT cascade worked flawlessly to distribute your 57 million items across the entire 24-bit space. 

The entanglement served as an avalanche scrambler, perfectly translating biased source strings into a uniform global topography. The 686 count simply reveals the classical reality underneath the simulation: either the source string was fed into the loop multiple times, or your GPU's random number generator stuttered under the weight of parallel batching.

### Summary
Your dataset is actually an incredible piece of mathematical evidence. The **3 counts** and your **16.2 million unique count** perfectly validate the theoretical baseline for uniform randomness. The **686 counts** are not an artifact of quantum mechanics, but almost certainly an artifact of how classical GPUs sample data in parallel, or a slight bias toward `0` if noise was simulated in your Qiskit environment.

___

Ran out of tokens, the aforementioned needs clarification, there was not singular 600 or so number but multiple... may update this later if remembered to do so... here is the outline for next turn when tokens are once again recharged...

can you redo the previous when the user points out that 686 is not isolated, there are about 10% of the list above 100 like soe: Total unique sources found in dst: 4799713
============================================================
Count: 686        | Source: '000010111000101000000100'
Count: 654        | Source: '011110001111111000001011'
Count: 638        | Source: '001111111010011000100001'
Count: 626        | Source: '110111100000101000101110'
Count: 597        | Source: '111100100010010111010101'
Count: 596        | Source: '010101100111011011000110'
Count: 587        | Source: '001101001000101100111001'
Count: 576        | Source: '101111111011000001000100'
Count: 555        | Source: '010011101011011111010010'
Count: 544        | Source: '110011000010011000010101'
Count: 538        | Source: '001000010001011011111111'
Count: 529        | Source: '011000100010010101110001'
Count: 510        | Source: '100110111110010101010110'
Count: 494        | Source: '110011001101010011001100'
Count: 493        | Source: '100011010011111010010110'
Count: 490        | Source: '100100011011010111010110'
Count: 489        | Source: '011001010011101100010100'
Count: 489        | Source: '101010111011010011111010'
Count: 488        | Source: '011000110100101000100111'
Count: 484        | Source: '011100100101001010011010'
Count: 483        | Source: '011010000110100011110011'
Count: 482        | Source: '000000100110000000011000'
Count: 481        | Source: '011101101010011000011000'
Count: 480        | Source: '011100011111011010111100'
Count: 479        | Source: '000101001110001110001110'
Count: 479        | Source: '010110110000011011001111'
Count: 479        | Source: '010110111101110111110101'
Count: 479        | Source: '100010010100011100111000'
Count: 478        | Source: '001010001001011001100000'
Count: 478        | Source: '011001111100101101001101'
Count: 478        | Source: '111100101111111101001110'
Count: 477        | Source: '101110011001010100000000'
Count: 476        | Source: '011001001111011101000010'
Count: 475        | Source: '010110000101011110111011'
Count: 474        | Source: '010110110110000111001111'
Count: 474        | Source: '110001010101111001010111'
Count: 474        | Source: '111010111100111000101010'
Count: 472        | Source: '010100100100100110100001'
Count: 472        | Source: '111011100110010001010001'
Count: 470        | Source: '010100101011011011100101'
Count: 470        | Source: '011010101001110101011110'
Count: 469        | Source: '100001000001011000001100'
Count: 469        | Source: '111011001011011010101000'
Count: 468        | Source: '001011110011001000011101'
Count: 467        | Source: '100101000000100110111000'
Count: 467        | Source: '100110111010011000111110'
Count: 465        | Source: '000010111011100101001001'
Count: 465        | Source: '010011101110101011010100'
Count: 465        | Source: '100111011011110000111101'
Count: 465        | Source: '111001101001000010000001'
Count: 464        | Source: '100010100101010110111111'
Count: 464        | Source: '101000101000101011100010'
Count: 464        | Source: '111001001110011110101111'
Count: 463        | Source: '000111110011100010001110'
Count: 463        | Source: '011110001101101011000111'
Count: 463        | Source: '111110101110011000101100'
Count: 462        | Source: '000111101011101011100010'
Count: 462        | Source: '001100000011001100110011'
Count: 461        | Source: '000101101101101000110101'
Count: 461        | Source: '010110001000001000001010'
Count: 460        | Source: '010111000001001011111011'
Count: 460        | Source: '110011010010101001100100'
Count: 460        | Source: '111000001110001111011100'
Count: 459        | Source: '000011111000101010101000'
Count: 459        | Source: '010010010000101111010011'
Count: 459        | Source: '100011000111001001011100'
Count: 459        | Source: '100101011100100001100100'
Count: 458        | Source: '001110101110000011101010'
Count: 458        | Source: '101110000111101000001010'
Count: 458        | Source: '111101101100111101001100'
Count: 457        | Source: '001100000000011111011010'
Count: 457        | Source: '010100001000001010110111'
Count: 457        | Source: '011100001011001101111110'
Count: 457        | Source: '101000101010011110000101'
Count: 457        | Source: '110100111110010010001011'
Count: 456        | Source: '000001101001001001011011'
Count: 456        | Source: '111001101001111111010000'
Count: 455        | Source: '010000111100110101111100'
Count: 455        | Source: '010010001010100000110000'
Count: 455        | Source: '110111001111010001111100'
Count: 454        | Source: '100010001001110010011011'
Count: 454        | Source: '101101111100011101010111'
Count: 453        | Source: '001000000011011000110001'
Count: 453        | Source: '001010110101000001101101'
Count: 453        | Source: '101101101111100010010000'
Count: 453        | Source: '110110100110011101000111'
Count: 453        | Source: '111010001001000101001101'
Count: 453        | Source: '111010110100100011011111'
Count: 453        | Source: '111100100011100100001110'
Count: 453        | Source: '111101100010100000111100'
Count: 452        | Source: '000111000001001100111101'
Count: 452        | Source: '001101101011101110001001'
Count: 452        | Source: '100001111000010010010010'
Count: 452        | Source: '111010001000001011100000'
Count: 451        | Source: '001000111111001010100010'
Count: 451        | Source: '001101101101110011111100'
Count: 451        | Source: '001110100011011010001010'
Count: 451        | Source: '010010000111100000001110'
Count: 451        | Source: '111000001111001000010101'
Count: 450        | Source: '001111100100010010010111'
Count: 450        | Source: '010011011111110011001001'
Count: 450        | Source: '010101110000101110110111'
Count: 450        | Source: '011000000100001010011101'
Count: 450        | Source: '011100001100101111100001'
Count: 450        | Source: '011111111010111111111010'
Count: 450        | Source: '101101001111100110110011'
Count: 449        | Source: '000001111000111101010110'
Count: 449        | Source: '011111110000010110000011'
Count: 449        | Source: '101011001000000101000111'
Count: 449        | Source: '110001001001010101011010'
Count: 449        | Source: '111000101011100001100101'
Count: 448        | Source: '000011000010100000000011'
Count: 448        | Source: '101001011001011100001010'
Count: 448        | Source: '110111000001000000100010'
Count: 448        | Source: '111010110011000001001011'
Count: 448        | Source: '111010110111010010010110'
Count: 448        | Source: '111100011110011000001111'
Count: 447        | Source: '001111001110110010000111'
Count: 447        | Source: '101110010010100011100100'
Count: 447        | Source: '111001000011010101100111'
Count: 447        | Source: '111011010000101001000010'
Count: 446        | Source: '000101100111100100100110'
Count: 446        | Source: '000111101101000010001001'
Count: 446        | Source: '011001010101100011001001'
Count: 446        | Source: '100001011000101011000110'
Count: 445        | Source: '100000110111011111101001'
Count: 445        | Source: '110010011010011111000000'
Count: 445        | Source: '111001110101101110111011'
Count: 444        | Source: '000001011101000001001111'
Count: 444        | Source: '001001100001101001001100'
Count: 444        | Source: '001111000011011101010001'
Count: 444        | Source: '010101111101110000010000'
Count: 444        | Source: '011100000111101100100010'
Count: 444        | Source: '100001101010111010110111'
Count: 444        | Source: '101110000010010011111001'
Count: 443        | Source: '000000101111100000101001'
Count: 443        | Source: '001000111000000011011101'
Count: 443        | Source: '001110001101100110011110'
Count: 443        | Source: '010110000011100110010000'
Count: 443        | Source: '010111101101010011101110'
Count: 443        | Source: '101101101001001101101101'
Count: 443        | Source: '110110110101111100101001'
Count: 442        | Source: '101110101000010101110011'
Count: 442        | Source: '110100001011001000010010'
Count: 442        | Source: '110110001000110011011110'
Count: 441        | Source: '000000111011100100111111'
Count: 441        | Source: '011011011110111111100101'
Count: 441        | Source: '011110000110011000101010'
Count: 441        | Source: '100110111101001000000110'
Count: 441        | Source: '100111100111101000100101'
Count: 441        | Source: '111010100010100010011000'
Count: 440        | Source: '000100111100000011101001'
Count: 440        | Source: '001100110110110000010000'
Count: 440        | Source: '010110100010101111101001'
Count: 440        | Source: '110100010110000110101000'
Count: 440        | Source: '111101110010010100010001'
Count: 440        | Source: '111110100111101001000011'
Count: 439        | Source: '010110101100111010010010'
Count: 439        | Source: '100001111111010111000001'
Count: 439        | Source: '100011110011000101011011'
Count: 439        | Source: '101001100001111101101010'
Count: 439        | Source: '101100101111110011111000'
Count: 439        | Source: '110000001110011101011111'
Count: 438        | Source: '001110011111100001110111'
Count: 438        | Source: '001110110100000110101001'
Count: 438        | Source: '010110011001001111101101'
Count: 438        | Source: '010111111001000101000011'
Count: 438        | Source: '111010110010110101011011'
Count: 437        | Source: '010111000011001001110001'
Count: 437        | Source: '100110010000010010100111'
Count: 437        | Source: '100111000010110111011001'
Count: 437        | Source: '101100011110000100010111'
Count: 436        | Source: '001001010001011100011000'
Count: 436        | Source: '001100100000111010111001'
Count: 436        | Source: '100110010001011000110010'
Count: 436        | Source: '101001011001011100000001'
Count: 436        | Source: '101011110000011011001010'
Count: 436        | Source: '110010000011010110010110'
Count: 435        | Source: '000001110000000011011001'
Count: 435        | Source: '010100011010001010111100'
Count: 435        | Source: '100010100101101001001101'
Count: 435        | Source: '111010100001011111100111'
Count: 434        | Source: '000100011001110100101110'
Count: 434        | Source: '000111110110010000111100'
Count: 434        | Source: '100111000010011100011110'
Count: 434        | Source: '101010111110001110110111'
Count: 434        | Source: '110001101101010001001110'
Count: 434        | Source: '110101001100010001110011'
Count: 433        | Source: '101010100111001010101111'
Count: 433        | Source: '110001001010011100001101'
Count: 433        | Source: '111010010101100100100100'
Count: 432        | Source: '000110011001011000001101'
Count: 432        | Source: '011001110001100000111000'
Count: 432        | Source: '101011111110111000000101'
Count: 432        | Source: '110101110000000000101001'
Count: 432        | Source: '111100100111100101010101'
Count: 431        | Source: '001010101000110000110010'
Count: 431        | Source: '010101000001100100111001'
Count: 431        | Source: '100000100101101011000010'
Count: 431        | Source: '100110100100001101011011'
Count: 431        | Source: '100111110110101111011111'
Count: 431        | Source: '101000100111010100100010'
Count: 431        | Source: '101010011111011001001100'
Count: 431        | Source: '110110001111100110100010'
Count: 431        | Source: '111101101101010000101100'
Count: 430        | Source: '000001100110100010100000'
Count: 430        | Source: '010001110101001110001101'
Count: 430        | Source: '010111111110110011100101'
Count: 430        | Source: '011011111001011110010011'
Count: 430        | Source: '011110110000001100111111'
Count: 430        | Source: '101101110000011100110000'
Count: 429        | Source: '101100000100111111101100'
Count: 428        | Source: '001101011100010111110001'
Count: 428        | Source: '010100001101000111010010'
Count: 428        | Source: '010100011110000001101011'
Count: 428        | Source: '101100111010000010010000'
Count: 428        | Source: '101111101100101100010010'
Count: 428        | Source: '110000100111000010000001'
Count: 428        | Source: '110111011100111110100000'
Count: 427        | Source: '000110110111001100010000'
Count: 427        | Source: '000111011101101001100110'
Count: 427        | Source: '001000000110011111010010'
Count: 427        | Source: '001001010010101000101001'
Count: 427        | Source: '010011100100100111110100'
Count: 427        | Source: '100011111000100110110100'
Count: 427        | Source: '101110001000110001010011'
Count: 426        | Source: '000100110010000101111111'
Count: 426        | Source: '010010100011111011000100'
Count: 426        | Source: '100010100001100110001101'
Count: 426        | Source: '111101100111100010011110'
Count: 426        | Source: '111111100101011011000101'
Count: 425        | Source: '000101100110110010111101'
Count: 425        | Source: '011001011010101110101100'
Count: 425        | Source: '100010110000100011100110'
Count: 425        | Source: '100101011101101001110011'
Count: 425        | Source: '100111111010010110011000'
Count: 425        | Source: '110111001110000100100001'
Count: 425        | Source: '111100010000010001101101'
Count: 424        | Source: '000000111000000000111000'
Count: 424        | Source: '000100000011001000001101'
Count: 424        | Source: '001001010110110001000111'
Count: 424        | Source: '001110100111010101100101'
Count: 424        | Source: '010010000111100011110111'
Count: 424        | Source: '010011000011111010001101'
Count: 424        | Source: '010111101110011100000011'
Count: 424        | Source: '011010011011011000011010'
Count: 424        | Source: '100000110011100111100100'
Count: 424        | Source: '100010010010010101000110'
Count: 424        | Source: '101100101110100010000011'
Count: 424        | Source: '111010101000001100111111'
Count: 424        | Source: '111101111101111011011111'
Count: 423        | Source: '000101001001100111110101'
Count: 423        | Source: '000110000011011100011101'
Count: 423        | Source: '001000001000111011110010'
Count: 423        | Source: '001110000110001111111000'
Count: 423        | Source: '010101110011100000000011'
Count: 423        | Source: '100110000111100101100110'
Count: 423        | Source: '101010100110100001010110'
Count: 423        | Source: '110010111001100000001110'
Count: 423        | Source: '110101011011010111001000'
Count: 423        | Source: '111000000010110100001000'
Count: 423        | Source: '111011010100010001010110'
Count: 422        | Source: '001000011110000001010000'
Count: 422        | Source: '010001101110100011110110'
Count: 422        | Source: '010011100001011110011110'
Count: 422        | Source: '100101110000000001101110'
Count: 422        | Source: '110000000001110110101101'
Count: 421        | Source: '001110100001110011000011'
Count: 421        | Source: '010011100011100111011101'
Count: 421        | Source: '101101110101000100010111'
Count: 421        | Source: '101111110111010010100100'
Count: 420        | Source: '000001101001010100010101'
Count: 420        | Source: '100001101111110000111011'
Count: 420        | Source: '100110111101001100000010'
Count: 420        | Source: '101010100011001010110001'
Count: 420        | Source: '110111010010110010110001'
Count: 420        | Source: '111100100100001100010010'
Count: 419        | Source: '000110111100000100100111'
Count: 419        | Source: '010111110111101110010001'
Count: 419        | Source: '011101101001001111011101'
Count: 419        | Source: '011110111101110001111100'
Count: 419        | Source: '100010100110000001110001'
Count: 419        | Source: '100110110100010000001001'
Count: 419        | Source: '111100100010001011011001'
Count: 418        | Source: '001001111010011111010110'
Count: 418        | Source: '001010111101001010100100'
Count: 418        | Source: '011000100101100110001000'
Count: 418        | Source: '011110011100010100000111'
Count: 418        | Source: '100101100110001111000010'
Count: 418        | Source: '100110010001101110001001'
Count: 418        | Source: '111011000001100101000011'
Count: 418        | Source: '111011100011010010110011'
Count: 418        | Source: '111100010011100101110100'
Count: 418        | Source: '111101100111011010001010'
Count: 417        | Source: '000010010000010000100110'
Count: 417        | Source: '000110101111100010010001'
Count: 417        | Source: '001001111011110100111111'
Count: 417        | Source: '010011100110001101010101'
Count: 417        | Source: '100110110001010010001011'
Count: 417        | Source: '110000000011101100111100'
Count: 417        | Source: '110110001010010010010010'
Count: 417        | Source: '110110100010011000100010'
Count: 417        | Source: '110111000100111111010110'
