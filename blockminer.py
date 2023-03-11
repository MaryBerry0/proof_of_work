import random
import hashlib
from datetime import datetime
from threading import Thread, Event

# Event to stop threads
blockFoundEvent = Event()

# Store blocks and hexadecimal hashes
blocks = []
block_hashes = []


# Convert hex digest to 256-bit binary string preserving leading zeros
def hextobin(h):
    return bin(int(h, 16))[2:].zfill(256)


# Count the leading zeros in a binary string
def count_leading_zeros(b):
    count = 0
    for digit in b:
        if digit == '0':
            count += 1
        else:
            break

    return count


# The seed will be the current time
def thread_getBlockRandom(d, prev_hex, pseudonym, seed):
    # Create a local PRNG to generate unique nonce values
    rnd = random.Random()
    rnd.seed(seed)

    while True:
        if blockFoundEvent.is_set():
            break

        # Nonce
        nonce_decimal = rnd.random()

        # Propose blocks based on random value with nonce (hash input string)
        block = (prev_hex + pseudonym + str(nonce_decimal))
        block_bytes = block.encode("utf-8")

        # Get the binary hash
        # Preserve leading zeros
        hex_hash = hashlib.sha256(block_bytes).hexdigest()
        bin_hash = hextobin(hex_hash)

        # If the hash is of the required difficulty then
        if bin_hash.startswith("".zfill(d)):
            # Set the block found event to halt other threads
            blockFoundEvent.set()

            # Store the block
            blocks.append(block)
            block_hashes.append(hex_hash)

            return


def mineBlockChain(d, d_target, seed, pseudonym, output_file):
    print("Running 'mineBlockChain()'")
    # The first line of the output file must be the miner pseudonym
    output_file.write(pseudonym + "\n")
    output_file.flush()

    # Previous hash and current difficulty
    # Update parameters during mining
    prev_hash = seed
    difficulty = d

    # Mining algorithm
    # Mine blocks up to the target difficulty d_target
    while difficulty <= d_target:
        # Reset block found event so that it can be triggered again
        blockFoundEvent.clear()
        # Deploy threads to mine the next block
        threads = []
        for i in range(0, 1000):
            t = Thread(target=thread_getBlockRandom, args=(difficulty, prev_hash, pseudonym,
                                                           i,))
            threads.append(t)
            t.start()

        # Join on all threads before continuing (i.e. wait for completion)
        for t in threads:
            t.join()

        # Establish the actual number leading zeros
        # Difficulty must be one greater
        difficulty = (count_leading_zeros(hextobin(block_hashes[-1]))) + 1

        # Block and hash are stored in global list variables
        # Write the next block to the output file
        output_file.write(blocks[-1] + "\n")
        output_file.flush()
        # Update the previous hexadecimal hash value and difficulty
        prev_hash = block_hashes[-1]

        # Print encouraging progress information
        print("Found a hash of difficulty: " + str(difficulty - 1))


def main():
    # *** Clear the blocks/hashes lists
    blocks.clear()
    block_hashes.clear()

    # Create an output file for the block chain
    output_file = open("blockchain.txt", "w")
    # Define seed block
    # This is the hash of Block 1 from the toy chain
    # seed = "00000a2ed46cd277a0edc3f17ff3df541b034345f4696d75744279166e19d8eb"

    # This is version 2 of the code
    # Intended to pick up where version one left off, with the below hash being my last discovered:
    # (Difficulty is 36)
    prev_block = "000000001a2f509945277501dc747dbbadc98ef40be8a9bdcdd1d8183ef28741blocksock0.7951153259716986"
    seed = hashlib.sha256(prev_block.encode("utf-8")).hexdigest()

    # Define a miner pseudonym
    pseudonym = "blocksock"
    # Difficulty start and target
    d_start = 37
    d_target = 40
    # Mine the block chain
    mineBlockChain(d_start, d_target, seed, pseudonym, output_file)

    print("### DONE ###")

    for h in block_hashes:
        print(hextobin(h))


# Call the main function , start program
main()