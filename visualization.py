import matplotlib.pyplot as plt
import pandas as pd

# Define your cache configurations
configs = [(4, 16), (8, 16), (16, 16), (32, 16),
           (4, 32), (8, 32), (16, 32), (32, 32),
           (4, 64), (8, 64), (16, 64), (32, 64)]

# Define your benchmark names
benchmarks = ["load_heavy", "jump_heavy", "mixed"]

# Each row is a (L1, L2) config; each column is a benchmark's cost
cost_matrix = [
    [15.0, 7.5, 9.0],
    [10.0, 7.5, 8.0],
    [7.5, 7.5, 7.5],
    [4.5, 4.5, 4.5],
    [13.0, 5.5, 7.0],
    [8.0, 5.5, 6.0],
    [5.5, 5.5, 5.5],
    [4.5, 4.5, 4.5],
    [12.0, 4.5, 6.0],
    [7.0, 4.5, 5.0],
    [4.5, 4.5, 4.5],
    [3.5, 3.5, 3.5],
]

df = pd.DataFrame(cost_matrix, columns=benchmarks,
                  index=[f"L1={l1}/L2={l2}" for l1, l2 in configs])

# Plotting the graph
plt.figure(figsize=(12, 6))
for benchmark in benchmarks:
    plt.plot(df.index, df[benchmark], marker='o', label=benchmark)

plt.xticks(rotation=45, ha='right')
plt.title("Cost per Cache Configuration for Each Benchmark")
plt.ylabel("Cost (0.5 × L1 Miss + L2 Miss + Writebacks)")
plt.xlabel("Cache Configuration")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# Save and show
plt.savefig("full_cost_comparison.png")
plt.show()

