from ARMSimulator import ARMSimulator

# Cache configurations to test
configs = [
    (4, 16), (8, 16), (16, 16), (32, 16),
    (4, 32), (8, 32), (16, 32), (32, 32),
    (4, 64), (8, 64), (16, 64), (32, 64)
]

# Benchmark binary files
benchmarks = [
    "test_load_heavy.txt",
    "test_jump_heavy.txt",
    "test_mixed.txt"
]

# Collect cost matrix
cost_matrix = []

for l1, l2 in configs:
    row = []
    print(f"\nTesting config: L1={l1}, L2={l2}")
    for bench in benchmarks:
        sim = ARMSimulator(blocksize=l1, unified_size=l2)
        instructions = sim.load_binary(bench)
        sim.run(instructions)
        cost = sim.cache.get_cost()
        print(f"  {bench}: Cost = {cost}")
        row.append(round(cost, 2))  
    cost_matrix.append(row)

print("\nFinal cost_matrix:")
for row in cost_matrix:
    print(row)
