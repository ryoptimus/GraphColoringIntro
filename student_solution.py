import os
import random
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class AdjNode:
    def __init__(self, vertex):
        self.vertex = vertex
        self.next = None

@dataclass
class Graph:
    def __init__(self, n: int, k: int):
        self.n = n
        self.k = k
        self.graph = [None] * n
        self.edges = []

    def add_edge(self, u: int, v: int):
        # Add v to u's adjacency list
        new_node = AdjNode(v)
        new_node.next = self.graph[u]
        self.graph[u] = new_node

        # Add u to v's adjacency list
        new_node = AdjNode(u)
        new_node.next = self.graph[v]
        self.graph[v] = new_node

        # Store edge
        self.edges.append((u, v))

def init_graph(fp):
    lines = []
    with open(fp, "r", encoding="utf-8") as f:
        for l in f:
            lines.append(l)

    n = int(lines[0])
    k = int(lines[1])

    g = Graph(n, k)

    for line in lines[2:]:
        u, v = line.split(" ")
        g.add_edge(int(u), int(v))

    return g


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
    b_l = max(1, (graph.k - 1).bit_length())
    return b_l

# Returns dict with node-color mapping
def decode_individual(graph, individual):
    width = get_color_len(graph)

    if len(individual) != graph.n * width:
        return None

    dmap = []
    for node in range(graph.n):
        start = node * width

        # Extract color bits
        bits = individual[start:start + width]

        color = 0

        for bit in bits:
            if bit not in (0, 1):
                return None

            color = (color << 1) | bit

        # Reject invalid color values
        if color >= graph.k:
            return None

        dmap.append(color)
    return dmap

def eval_graph(graph, individual):
    dmap = decode_individual(graph, individual)

    if dmap is None:
        return (0.0,)

    satisfied = 0

    for u, v in graph.edges:
        if dmap[u] != dmap[v]:
            satisfied += 1

    total_edges = len(graph.edges)

    if total_edges == 0:
        return (1.0,)

    fitness = satisfied / total_edges

    return (fitness,)

def run_ga(fp, population_size=300, ngen=200, cxpb=0.8, mutpb=0.3):
    from deap import algorithms, base, creator, tools

    graph = init_graph(fp)
    width = get_color_len(graph)

    if not hasattr(creator, "GraphColorFitnessMax"):
        creator.create("GraphColorFitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "GraphColorIndividual"):
        creator.create("GraphColorIndividual", list, fitness=creator.GraphColorFitnessMax)

    def make_individual():
        genome = []
        for _ in range(graph.n):
            genome.extend(encode_color(random.randrange(graph.k), width))
        return creator.GraphColorIndividual(genome)

    def encode_color(color, width):
        return [int(bit)for bit in format(color, f"0{width}b")]

    def mate_by_node(ind1, ind2):
        # Swap complete color genes
        for node in range(graph.n):
            if random.random() < 0.5:
                start = node * width
                end = start + width
                ind1[start:end], ind2[start:end] = ind2[start:end], ind1[start:end]
        return ind1, ind2

    def mutate_color(individual):
        # Mutate one node per selected individual
        for node in range(graph.n):
            if random.random() < 1 / graph.n:
                start = node * width
                individual[start:start + width] = encode_color(random.randrange(graph.k), width)
        return (individual,)

    toolbox = base.Toolbox()
    toolbox.register("individual", make_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", eval_graph, graph)
    toolbox.register("mate", mate_by_node)
    toolbox.register("mutate", mutate_color)
    toolbox.register("select", tools.selTournament, tournsize=3)

    population = toolbox.population(n=population_size)
    best_ever = tools.HallOfFame(1)

    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, halloffame=best_ever, verbose=False,)

    best_individual = best_ever[0]
    coloring = decode_individual(graph, best_individual)
    fitness = eval_graph(graph, best_individual)

    print(f"Best fitness: {fitness[0]}")
    print(f"Color assignment: {coloring}")

    return fitness[0]

def main():
    gdir = Path("graphs")
    gpath = os.getcwd() / gdir
    for f in gpath.iterdir():
        run_ga(f)

if __name__ == "__main__":
    main()
