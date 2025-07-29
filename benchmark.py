from ARMSimulator import ARMSimulator

configs = [
    (4, 16), (8, 16), (16, 16), (32, 16),
    (4, 32), (8, 32), (16, 32), (32, 32),
    (4, 64), (8, 64), (16, 64), (32, 64)
]

benchmarks = ["test_load_heavy.txt"]

for bench in benchmarks:
    print(f"\n--- Benchmark: {bench} ---")
    best_cost = float('inf')
    best_config = None
    for l1, l2 in configs:
        sim = ARMSimulator(blocksize=l1, unified_size=l2)
        instructions = sim.load_binary(bench)
        sim.run(instructions)
        cost = sim.cache.get_cost()
        print(f"L1={l1} | L2={l2} → Cost={cost:.2f}")
        if cost < best_cost:
            best_cost = cost
            best_config = (l1, l2)
    print(f"> Best config for {bench}: L1={best_config[0]}, L2={best_config[1]}, Cost={best_cost:.2f}")