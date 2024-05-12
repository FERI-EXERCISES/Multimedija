import numpy as np
from scipy.io import wavfile
import math


def read_wav(file_path):
    sample_rate, audio_data = wavfile.read(file_path)
    return sample_rate, audio_data


def write_wav(file_path, sample_rate, audio_data):
    wavfile.write(file_path, sample_rate, audio_data)


def EncodeUnsigned(B, g, value):
    bit_array = [(int(value) >> bit) & 1 for bit in range(int(g) - 1, -1, -1)]
    B.extend(bit_array)
    return B


def DecodeUnsigned(B, g):
    value = sum(B[i] << (int(g) - 1 - i) for i in range(int(g)))
    del B[:g]

    return value


def EncodeSigned(B, g, value):
    # Determine the sign bit (0 for non-negative, 1 for negative)
    sign_bit = 1 if value < 0 else 0

    # Create the bit array with the sign bit at the start
    bit_array = [sign_bit] + [(abs(int(value)) >> bit) & 1 for bit in range(int(g) - 1, -1, -1)]

    B.extend(bit_array)
    return B


def DecodeSigned(B, g):
    # Extract the sign bit and remove it from B
    sign_bit = B[0]
    del B[0]

    # Decode the magnitude
    value = sum(B[i] << (int(g) - 1 - i) for i in range(int(g)))

    # Apply the sign
    if sign_bit == 1:
        value = -value

    # Remove the processed bits from B
    del B[:g]

    return value


def WindowFunction(data):
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            data[i, j] *= math.sin((math.pi / (data.shape[1])) * (j + 0.5))
    return data


def PopulateBlocks(audio_data, param_N):
    # pad 0 to the end of the audio data
    if len(audio_data) % param_N != 0:
        audio_data = np.pad(audio_data, (0, param_N - len(audio_data) % param_N), 'constant', constant_values=(0, 0))

    # get block info
    block_size = param_N * 2
    num_blocks = math.ceil(len(audio_data) / param_N) + 1

    # razdelitev v bloke
    blocks = np.zeros((num_blocks, block_size), dtype=np.float32)

    for i in range(num_blocks):
        if i == 0:
            # Fill the first half of the first block with zeros
            pass
        else:
            # Copy the last half of the previous block to the first half of the current block
            blocks[i, :param_N] = blocks[i - 1, param_N:]

        if i < num_blocks - 1:
            # Fill the second half of the current block with audio data
            start_idx = i * param_N
            end_idx = start_idx + param_N
            blocks[i, param_N:] = audio_data[start_idx:end_idx]

    return blocks


def MDCT(blocks):
    mdct = np.zeros((blocks.shape[0], (blocks.shape[1] // 2)), dtype=np.float32)

    for i in range(blocks.shape[0]):
        for k in range((blocks.shape[1] // 2)):
            for n in range(blocks.shape[1]):
                mdct[i, k] += blocks[i, n] * np.cos(
                    (math.pi / (blocks.shape[1] // 2)) * (n + 0.5 + ((blocks.shape[1] // 2) / 2)) * (k + 0.5))

    mdct = np.round(mdct, 6)

    return mdct


def IMDCT(blocks):
    MDCT = np.zeros((blocks.shape[0], (blocks.shape[1] * 2)), dtype=np.float32)

    for i in range(blocks.shape[0]):
        for n in range((blocks.shape[1] * 2)):
            for k in range(blocks.shape[1]):
                MDCT[i, n] += blocks[i, k] * np.cos(
                    (math.pi / blocks.shape[1]) * (n + 0.5 + (blocks.shape[1] / 2)) * (k + 0.5))
            MDCT[i, n] *= 2 / blocks.shape[1]

    MDCT = np.round(MDCT, 6)

    return MDCT


def Reconstruction(imdct):
    audio_data = np.zeros((imdct.shape[0] - 1) * (imdct.shape[1] // 2), dtype=np.float32)

    for i in range(imdct.shape[0] - 1):
        for j in range((imdct.shape[1] // 2)):
            audio_data[i * (imdct.shape[1] // 2) + j] = imdct[i, j + (imdct.shape[1] // 2)] + imdct[i + 1, j]

    audio_data = np.round(audio_data)

    return audio_data


def CompressChannel(channel, param_N, param_M):
    blocks = PopulateBlocks(channel, param_N)
    print("Blocks:\n", blocks)

    # get block info
    num_blocks = blocks.shape[0]

    blocks = WindowFunction(blocks)
    print("Windowed blocks:\n", blocks)

    mdct = MDCT(blocks)
    print("MDCT:\n", mdct)

    # zaokrozimo na cela stevila
    mdct = np.trunc(mdct)
    print("Trunc MDCT:\n", mdct)

    # erase for param_M values from the end of each block
    new_blocks = np.zeros((num_blocks, param_N - param_M), dtype=np.int32)
    for i in range(num_blocks):
        new_blocks[i] = mdct[i, :param_N - param_M]
    print("New blocks:\n", new_blocks)

    compressed_channel = new_blocks.flatten()
    print("Compressed channel:\n", compressed_channel)

    return compressed_channel


def DecompressChannel(channel, param_N, param_M):
    new_block_size = param_N - param_M
    num_blocks = math.ceil(channel.shape[0] / new_block_size)

    if channel.shape[0] % new_block_size != 0:
        channel = np.pad(channel, (0, new_block_size - channel.shape[0] % new_block_size), 'constant', constant_values=(0, 0))

    compr_M = channel.reshape((num_blocks, new_block_size))
    print("Blocks:\n", compr_M)

    padded_blocks = np.pad(compr_M, ((0, 0), (0, param_M)), mode='constant')
    print("Padded blocks:\n", padded_blocks)

    imdct = IMDCT(padded_blocks)
    print("IMDCT:\n", imdct)

    imdct = WindowFunction(imdct)
    print("Windowed IMDCT:\n", imdct)

    # reconstruct audio data
    channel_data = Reconstruction(imdct)
    print("Reconstructed:\n", channel_data)

    return channel_data


def compress(audio_data, param_N, param_M, sample_rate):
    # warning factor must be <= block_size
    if param_M > param_N:
        raise ValueError("M <= N")

    # CHANGE IF TESTCASE 2
    M = (audio_data[:, 0] + audio_data[:, 1]) / 2
    S = (audio_data[:, 0] - audio_data[:, 1]) / 2

    # M = audio_data[:, 0]
    # S = audio_data[:, 1]
    # CHANGE IF TESTCASE 2

    compr_M = CompressChannel(M, param_N, param_M)
    compr_S = CompressChannel(S, param_N, param_M)

    if compr_M.shape[0] != compr_S.shape[0]:
        raise ValueError("M and S must have same length")

    len = compr_M.shape[0]

    B = list()

    B = EncodeUnsigned(B, 8, len)
    B = EncodeUnsigned(B, 4, param_N)
    B = EncodeUnsigned(B, 16, sample_rate)
    B = EncodeUnsigned(B, 4, param_M)

    print("Len: ", len)
    print("Param_N: ", param_N)
    print("Sample_rate: ", sample_rate)
    print("Param_M: ", param_M)

    print("B: ", B)

    for i in range(len):
        B = EncodeUnsigned(B, 6, CalcBitsSigned(compr_M[i]))
        B = EncodeSigned(B, CalcBitsSigned(compr_M[i]), compr_M[i])

    for i in range(len):
        B = EncodeUnsigned(B, 6, CalcBitsSigned(compr_S[i]))
        B = EncodeSigned(B, CalcBitsSigned(compr_S[i]), compr_S[i])

    # Backfill 0
    B += [0] * (8 - B.__len__() % 8)

    # Convert to byte array (!!!)
    byte_array = bytearray()
    for i in range(0, B.__len__(), 8):
        bit_chunk = B[i:i + 8]
        byte = int("".join(str(bit) for bit in bit_chunk), 2)
        byte_array.append(byte)

    return byte_array


def decompress(byte_array):
    # Get bit array
    B = list()
    for byte in byte_array:
        bits = [int(bit) for bit in '{:08b}'.format(byte)]
        B.extend(bits)

    len = DecodeUnsigned(B, 8)
    param_N = DecodeUnsigned(B, 4)
    sample_rate = DecodeUnsigned(B, 16)
    param_M = DecodeUnsigned(B, 4)

    print("Len: ", len)
    print("Param_N: ", param_N)
    print("Sample_rate: ", sample_rate)
    print("Param_M: ", param_M)

    compr_M = np.zeros(len, dtype=np.int32)
    compr_S = np.zeros(len, dtype=np.int32)

    for i in range(len):
        bits = DecodeUnsigned(B, 6)
        compr_M[i] = DecodeSigned(B, bits)

    for i in range(len):
        bits = DecodeUnsigned(B, 6)
        compr_S[i] = DecodeSigned(B, bits)

    decompr_M = DecompressChannel(compr_M, param_N, param_M)
    decompr_S = DecompressChannel(compr_S, param_N, param_M)

    if decompr_M.shape[0] != decompr_S.shape[0]:
        raise ValueError("M and S must have same length")

    audio_data = np.zeros((decompr_M.shape[0], 2), dtype=np.int32)

    # CHANGE IF TESTCASE 2
    audio_data[:, 0] = decompr_M + decompr_S
    audio_data[:, 1] = decompr_M - decompr_S

    # audio_data[:, 0] = decompr_M
    # audio_data[:, 1] = decompr_S
    # CHANGE IF TESTCASE 2

    return sample_rate, audio_data


def CalcBitsSigned(number):
    return 1 + math.ceil(math.log2(max(abs(number), 1)))


def main():
    input_wav = "stereo.wav"
    compressed_file = "compressed.bin"
    output_wav = "output.wav"

    param_M = 0
    param_N = 5

    # Read WAV file
    sample_rate, audio_data = read_wav(input_wav)
    print("Audio data shape:", audio_data.shape)
    print("Sample rate:", sample_rate)

    # Compress audio data
    output_data = compress(audio_data, param_N, param_M, sample_rate)

    # Save compressed audio data
    binary_file = open(compressed_file, "wb")
    binary_file.write(output_data)
    binary_file.close()

    print("Decompressing...")

    # Read compressed file
    file = open(compressed_file, 'rb')
    compressed_bytes = file.read()
    file.close()
    byte_array = bytearray(compressed_bytes)

    # Decompress audio data
    sample_rate, decompressed = decompress(byte_array)

    # Write WAV file
    write_wav(output_wav, sample_rate, decompressed)


def TestCase():
    param_N = 3

    M = list(range(1, 13))
    print("Original:\n", M)

    blocks = PopulateBlocks(M, param_N)
    print("Blocks:\n", blocks)

    blocks = WindowFunction(blocks)
    print("Windowed blocks:\n", blocks)

    mdct = MDCT(blocks)
    print("MDCT:\n", mdct)

    imdct = IMDCT(mdct)
    print("IMDCT:\n", imdct)

    new_blocks = WindowFunction(imdct)
    print("Windowed blocks:\n", new_blocks)

    audio_data = Reconstruction(new_blocks)
    print("Reconstructed:\n", audio_data)


def TestCase2():
    param_N = 3
    param_M = 2

    M = list(range(1, 13))
    S = list(range(1, 13))

    audio_data = np.zeros((len(M), 2), dtype=np.int32)
    audio_data[:, 0] = M
    audio_data[:, 1] = S

    print("Original:\n", audio_data)

    compressed = compress(audio_data, param_N, param_M, 44100)

    print("Compressed:\n", compressed)

    sample_rate, decompressed = decompress(compressed)

    print("Decompressed:\n", decompressed)


if __name__ == "__main__":
    TestCase()
