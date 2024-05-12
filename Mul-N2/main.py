import numpy as np
from PIL import Image
import math
import time
import os


def Predict(P, X, Y):
    P = P.astype(np.int16)

    E = np.zeros(P.size, dtype="int16")

    for x in range(X):
        for y in range(Y):
            current_ix = y * X + x

            if y == 0 and x == 0:
                E[current_ix] = P[0, 0]
            elif y == 0:
                E[current_ix] = P[x - 1, 0] - P[x, 0]
            elif x == 0:
                E[current_ix] = P[0, y - 1] - P[0, y]
            else:
                if P[x - 1, y - 1] >= max(P[x - 1, y], P[x, y - 1]):
                    E[current_ix] = min(P[x - 1, y], P[x, y - 1]) - P[x, y]
                elif P[x - 1, y - 1] <= min(P[x - 1, y], P[x, y - 1]):
                    E[current_ix] = max(P[x - 1, y], P[x, y - 1]) - P[x, y]
                else:
                    E[current_ix] = P[x - 1, y] + P[x, y - 1] - P[x - 1, y - 1] - P[x, y]

    return E


def PredictInverse(E, X, Y):
    P = np.zeros((X, Y), dtype="int16")

    for x in range(X):
        for y in range(Y):
            current_ix = y * X + x

            if y == 0 and x == 0:
                P[x, y] = E[current_ix]
            elif y == 0:
                P[x, y] = P[x - 1, y] - E[current_ix]
            elif x == 0:
                P[x, y] = P[x, y - 1] - E[current_ix]
            else:
                if P[x - 1, y - 1] >= max(P[x - 1, y], P[x, y - 1]):
                    P[x, y] = min(P[x - 1, y], P[x, y - 1]) - E[current_ix]
                elif P[x - 1, y - 1] <= min(P[x - 1, y], P[x, y - 1]):
                    P[x, y] = max(P[x - 1, y], P[x, y - 1]) - E[current_ix]
                else:
                    P[x, y] = P[x - 1, y] + P[x, y - 1] - P[x - 1, y - 1] - E[current_ix]

    return P.astype(np.uint8)


def IC(B, C, L, H):
    if H - L > 1:
        if C[H] != C[L]:
            m = math.floor(0.5 * (H + L))
            g = math.ceil(math.log2(C[H] - C[L] + 1))
            B = encode(B, g, C[m] - C[L])

            if L < m:
                B = IC(B, C, L, m)
            if m < H:
                B = IC(B, C, m, H)
    return B


def DeIC(B, C, L, H):
    if H - L > 1:
        if C[L] == C[H]:
            # for i in range(L + 1, H):
                # C[i] = C[L]
            C[L+1:H] = C[L]

        else:
            m = math.floor(0.5 * (H + L))
            g = math.ceil(math.log2(C[H] - C[L] + 1))

            value = decode(B, g)
            C[m] = C[L] + value

            if L < m:
                DeIC(B, C, L, m)
            if m < H:
                DeIC(B, C, m, H)

    #return C


def encode(B, g, value):
    bit_array = [(int(value) >> bit) & 1 for bit in range(int(g) - 1, -1, -1)]
    B.extend(bit_array)
    return B


def decode(B, g):
    value = sum(B[i] << (int(g) - 1 - i) for i in range(int(g)))
    del B[:g]

    return value


def SetHeader(X, C0, Cn, n):
    B = list()

    B = encode(B, 12, X)
    B = encode(B, 8, C0)
    B = encode(B, 32, Cn)
    B = encode(B, 24, n)

    return B


def DecodeHeader(B):
    X = decode(B, 12)
    C0 = decode(B, 8)
    Cn = decode(B, 32)
    n = decode(B, 24)

    return X, C0, Cn, n


def compress(P, X, Y):
    E = Predict(P, X, Y)

    n = X * Y

    N = np.zeros(n, dtype="int16")
    N[0] = E[0]

    for i in range(1, n):
        if E[i] >= 0:
            N[i] = 2 * E[i]
        else:
            N[i] = 2 * abs(E[i]) - 1

    C = np.zeros(n, dtype="int32")
    C[0] = N[0]
    for i in range(1, n):
        C[i] = C[i - 1] + N[i]

    # Encode header
    B = SetHeader(X, C[0], C[n - 1], n)

    B = IC(B, C, 0, n - 1)

    # Backfill 0
    B += [0] * (8 - len(B) % 8)

    # Convert to byte array (!!!)
    byte_array = bytearray()
    for i in range(0, len(B), 8):
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

    X, C0, Cn, n = DecodeHeader(B)

    Y = n // X

    C = np.zeros(n, dtype="int32")
    C[0] = C0
    C[n - 1] = Cn

    start_time = time.time()
    #C = DeIC(B, C, 0, n - 1)
    DeIC(B, C, 0, n - 1)
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    print(f"DeIC took {duration} seconds to run.")

    N = np.zeros(n, dtype="int16")
    N[0] = C[0]

    for i in range(1, n):
        N[i] = C[i] - C[i - 1]

    E = np.zeros(n, dtype="int16")
    E[0] = N[0]

    for i in range(1, n):
        if N[i] % 2 == 0:
            E[i] = N[i] // 2
        else:
            E[i] = -(N[i] + 1) // 2

    P = PredictInverse(E, X, Y)

    return P

def ProcessImage(filename):
    # Set paths
    path = os.path.join("Slike", filename)
    output_path_bmp = os.path.join("Compressed", filename)
    only_filename = os.path.splitext(filename)[0]
    output_path_bin = os.path.join("Compressed", only_filename + ".bin")

    # Read image file
    img = Image.open(path)
    img_array = np.array(img)
    img.close()

    # Get dimensions
    X, Y = img_array.shape

    # Compress image
    start_time = time.time()
    array = compress(img_array, X, Y)
    end_time = time.time()
    duration = round(end_time - start_time, 2)

    # Save compressed image
    binary_file = open(output_path_bin, "wb")

    binary_file.write(array)
    binary_file.close()

    print(f"Compression took {duration} seconds to run.")

    # Read image file
    file = open(output_path_bin, 'rb')
    compressed_bytes = file.read()
    file.close()
    byte_array = bytearray(compressed_bytes)

    # Decompress image
    decompressed = decompress(byte_array)

    # Save decompressed image
    image = Image.fromarray(decompressed)
    image.save(output_path_bmp)
    image.close()

    print(f"Decompression took {duration} seconds to run.")

    # Get compression ratio
    original_size = os.path.getsize(path)
    compressed_size = os.path.getsize(output_path_bin)
    ratio = round(original_size / compressed_size, 2)

    # Print results
    print(f"Original size: {original_size} bytes")
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {ratio}")


if __name__ == "__main__":
    # Test case 1
    P = np.array([[23, 21, 21, 23, 23],
                  [24, 22, 22, 20, 24],
                  [23, 22, 22, 19, 23],
                  [26, 25, 21, 19, 22]])
    print(P)

    B = compress(P, 4, 5)

    print(decompress(B))

    # Test case 2
    file = "Mosaic.bmp"
    ProcessImage(file)

    # Test case 3
    # files = os.listdir("Slike")[:10]
    # for file in files:
    #     print(f"Working on {file}:")
    #     ProcessImage(file)


