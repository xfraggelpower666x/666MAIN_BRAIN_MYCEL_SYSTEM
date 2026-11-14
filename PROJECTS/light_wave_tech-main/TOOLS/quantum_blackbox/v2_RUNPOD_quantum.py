# quantum.py
# https://aistudio.google.com/app/prompts/16p8mZyZbbjcR9CtoJyGWfa3CkalS8Kab

# colab works with #!pip install qiskit-aer-gpu-cu11
# Tesla T4
# NVIDIA-SMI 580.82.07              
# Driver Version: 580.82.07      
# CUDA Version: 13.0

# RUNPOD WORKS RTX 3070 8GB
# NVIDIA-SMI 595.99.02              
# Driver Version: 595.99.02
# CUDA Version: 13.0
# TEMPLATE: PyTorch 2.13.0 on CUDA 13.0.0 and Ubuntu 24.04.

# pip install qiskit qiskit-aer qiskit-aer-gpu
# pip install qiskit-aer-gpu

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.circuit import ParameterVector

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import random
import time
import json

class QuantumBlackBox:
    def __init__(self, filepath, num_qubits=24):
        self.qbit_string_list = self._get_qbit_strings(filepath)

        self.num_qubits = num_qubits
        #self.simulator = AerSimulator()
        self.simulator = AerSimulator(method='statevector', device='GPU')
        
        # 1. Create the circuit ONCE
        self.qc = QuantumCircuit(num_qubits, num_qubits)
        
        # 2. Create Placeholders for our angles
        self.angles = ParameterVector('theta', num_qubits)
        
        # 3. INITIAL STATE: Add the RY gates (this maps your input data to waves)
        for i in range(num_qubits):
            self.qc.ry(self.angles[i], i)

        # ---------------------------------------------------------
        # NEW STEP: Add Entanglement!
        # We will chain them together: 0 entangles 1, 1 entangles 2, etc.
        # ---------------------------------------------------------
        for i in range(num_qubits - 1):
            self.qc.cx(i, i + 1)

        # Optional: You can also close the loop by entangling the last with the first
        # self.qc.cx(num_qubits - 1, 0)
        # ---------------------------------------------------------
            
        # 4. MEASUREMENT: This collapses the entangled waves into your 'dst' string
        self.qc.measure(range(num_qubits), range(num_qubits))
        
        # Now, self.qc is locked in.

    def _get_qbit_strings(self, filepath):
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        strings = text.split('\n')
        random.shuffle(strings)
        print(f"num_strings: {len(strings)}")
        return strings

    def get_random_qbit_string(self):
        return random.choice(self.qbit_string_list)

    def get_influenced_binary_string(self, outside_data: list, influence_strength: float = 0.8):
        list_of_circuits_to_run = []
        for i, data_string in enumerate(outside_data):
            #print(f"{i}/{len(outside_data)}")
            # Generate the bound angles for this string
            # Calculate the math
            angle_1 = 2 * np.arcsin(np.sqrt(influence_strength))
            angle_0 = 2 * np.arcsin(np.sqrt(1 - influence_strength))
        
            # Create a list of the actual angles we want for this specific run
            bound_angles = []
            for bit in reversed(data_string):
                if bit == '1':
                    bound_angles.append(angle_1)
                else:
                    bound_angles.append(angle_0)

            # Assign parameters and ADD TO LIST
            # Inject the real angles into our placeholder circuit
            # (This creates a temporary ready-to-run circuit without mutating self.qc)
            list_of_circuits_to_run.append( self.qc.assign_parameters(bound_angles) )

        print(f"LIST_OF_CIRCUITS_TO_RUN: {len(list_of_circuits_to_run)}")

        # Run it: the simulator will chew through all circuits in C++ very fast
        batch_result_list = []
        batch_result = self.simulator.run(list_of_circuits_to_run, shots=10000).result()
        for i in range(len(list_of_circuits_to_run)):
            counts = batch_result.get_counts(i)
            tmp_vals = list(counts.items())
            #print(f"--- LEN: {len(tmp_vals)}")

            for index, item in enumerate(tmp_vals):
                quantum_binary_str, amount = list(counts.items())[index]

                if amount > 1: 
                    print(f"       AMOUNT: {amount}")
                    orig_bit_str = outside_data[i]
                    batch_result_list.append((orig_bit_str, quantum_binary_str, amount))
        
        print(f"--- TOTAL LEN: {len(batch_result_list)}")
        return batch_result_list

    def xor_parity_check(self, binary_string):
        """True if odd number of 1s, False if even."""
        #print(f"# of 1's: {binary_string.count('1')}")
        return binary_string.count('1') % 2 != 0

def chunk_generator(data, size):
    for i in range(0, len(data), size):
        yield data[i : i + size]

#quantum_black_box = QuantumBlackBox("../../DATA/qbit_strings_data.txt")
quantum_black_box = QuantumBlackBox("qbit_strings_data.txt")


def filter_through_quantum_black_box(num_quantum_items=500):
    random_qbit_str_list = []
    for i in range(num_quantum_items):
        #print(f"{i}/{num_quantum_items}")
        random_qbit_str = quantum_black_box.get_random_qbit_string()
        #print(f"random_qbit_str: {random_qbit_str}")
        random_qbit_str_list.append(random_qbit_str)

    # Generate a string where there is an 85% chance each qubit matches the outside data
    batch_size = 25
    time_start = time.time()
    total_iterations = int(len(random_qbit_str_list)/batch_size)
    quantum_results_list = []

    for i, batch in enumerate(chunk_generator(random_qbit_str_list, batch_size)):
        #print(f"{i}: {batch}")

        # ---------- ETA CALCULATION ----------
        iters_done = i + 1
        elapsed_time = time.time() - time_start
        time_per_iter = elapsed_time / iters_done
        iters_left = total_iterations - iters_done
        eta_seconds = int(iters_left * time_per_iter)
                    
        m, s = divmod(eta_seconds, 60)
        h, m = divmod(m, 60)
        eta_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

        # Print the progress
        print(f"Quantum_Black_Box Iteration: {iters_done}/{total_iterations} | ETA: {eta_str}", end='\r', flush=True)
        # -------------------------------------

        batch_results = quantum_black_box.get_influenced_binary_string(batch, influence_strength=0.85)
        quantum_results_list.extend(batch_results)

    print(f"LEN_random_qbit_str_list: {len(quantum_results_list)}")
    return quantum_results_list

def run_single_session(session_id):
    """
    This is the worker function. It runs in an isolated process.
    Everything inside here runs in parallel with other workers.
    """

    all_quantum_pairs = []

    qbit_str_list_grouped = filter_through_quantum_black_box(num_quantum_items=100)
    #print(f"qbit_str_list_grouped: {qbit_str_list_grouped}")

    for src_val, dst_val, count in qbit_str_list_grouped:
        all_quantum_pairs.append({
            "src": src_val,
            "dst": dst_val,
            "count": count
        })

    print(f"Gathered {len(all_quantum_pairs)} pairs.")

    # ---------------------------------------------------------
    # 2. SAVING TO JSON
    # ---------------------------------------------------------
    with open(f"output_data/{session_id:03d}_quantum_pairs.json", "w") as f:
        json.dump(all_quantum_pairs, f, indent=4)

    # Return basic info to the main thread for our progress printout
    return session_id, len(all_quantum_pairs)

if __name__ == '__main__':

    # CRITICAL: For CUDA/GPU operations, force Python to 'spawn' new processes.
    # This ensures each worker gets a fresh, clean connection to the GPU driver.
    mp.set_start_method('spawn', force=True)

    #NUM_SESSIONS = 1
    NUM_SESSIONS = 100
    NUM_WORKERS = 12

    print(f"Starting {NUM_SESSIONS} sessions using {NUM_WORKERS} parallel workers...")
    
    time_start = time.time()
    iters_done = 0

    # Create a pool of 12 independent processes
    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        
        # Submit all 100 sessions to the worker pool. 
        # The executor will automatically keep exactly 12 running at all times.
        futures = {executor.submit(run_single_session, i): i for i in range(NUM_SESSIONS)}

        # as_completed() yields futures the moment they finish their calculations.
        for future in as_completed(futures):
            session_id = futures[future]
            try:
                # Retrieve the return values from the worker
                completed_id, pairs_count = future.result()
                
                # Increment our done counter
                iters_done += 1

                # ---------- ASYNC ETA CALCULATION ----------
                # ETA calculation needs slight adjustment because workers finish out of order
                elapsed_time = time.time() - time_start
                time_per_iter = elapsed_time / iters_done
                iters_left = NUM_SESSIONS - iters_done
                eta_seconds = int(iters_left * time_per_iter)
                            
                m, s = divmod(eta_seconds, 60)
                h, m = divmod(m, 60)
                eta_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"

                # Print the progress
                print(f"[Finished Session {completed_id:03d}] "
                      f"OVERALL PROGRESS: {iters_done}/{NUM_SESSIONS} | "
                      f"ETA: {eta_str} | Gathered {pairs_count} pairs.")
                # -------------------------------------------

            except Exception as exc:
                print(f"Session {session_id} generated an exception: {exc}")
