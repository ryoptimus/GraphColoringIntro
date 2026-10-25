import os
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Graph:
    n_ct: int
    c_ct: int
    adj_l: dict = field(init=False)
    edges: set = field(default_factory=set)

    def __init__(self, n_ct: int, c_ct: int):
        self.n_ct = n_ct
        self.c_ct = c_ct
        self.adj_l = {}
        for i in range(self.n_ct):
            self.adj_l[i] = set()
        self.edges = set()

    def add_edge(self, u: int, v: int):
        self.adj_l[u].add(v)
        self.adj_l[v].add(u)
        self.edges.add((min(u, v), max(u, v)))

def init_graph(fp):
    lines = []
    with open(fp, "r", encoding="utf-8") as f:
        for l in f:
            lines.append(l)

    n_ct = int(lines[0])
    c_ct = int(lines[1])

    g = Graph(n_ct, c_ct)

    for line in lines[2:]:
        u, v = line.split(" ")
        g.add_edge(int(u), int(v))

    print(f"{fp.name} initialized")

def encode_color(color, width):
    gray_value = bin_to_gray(color)

    # Convert Gray-coded integer into a list of bits
    gray_bits = format(gray_value, f"0{width}b")

    return [int(bit) for bit in gray_bits]

# individual should be size n
# return dict with node-color mapping
def decode_individual(graph, individual):
    print("I'm decoding 0_0")
    width = bits_per_color(graph)

    dmap = {}
    for node in range(graph.num_nodes):
        start = node * width

        # Extract color bits
        bits = individual[start:start + width]

        if any(bit not in (0, 1) for bit in bits):
            return None

        # Convert list of bits into integer
        gray_value = int("".join(map(str, bits)), 2)

        # Convert Gray-coded integer to color number
        color = gray_to_bin(gray_value)

        # Reject invalid color values
        if color >= graph.num_colors:
            return None

        dmap[node] = color
    return dmap

# Dec number (from bin) -> gray code
def bin_to_gray(n):
    # Right shift n (1bit)
    res = n >> 1

    # XOR with original number
    return n ^ res

# Gray code -> binary code
def gray_to_bin(n):
    b = 0
    # Traverse all bits of Gray code
    while n > 0:
        # Build binary number step by step using XOR
        b ^= n
        # Next bit
        n = n >> 1

    return b

# Retrieve bit count for color
def get_color_len(graph):
    b_l = max(1, (graph.c_ct - 1).bit_length())
    return b_l

def main():
    gdir = Path("graphs")
    gpath = os.getcwd() / gdir
    for f in gpath.iterdir():
        init_graph(f)

if __name__ == "__main__":
    main()
