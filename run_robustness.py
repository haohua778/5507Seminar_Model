"""Run the robustness checks and write the results to Output/robustness/.

Steps:
1. Wild cluster bootstrap p-values for the six frequency coefficients

Requires Output/<stage>/coefficients.csv from run_pipeline.py.
Paper: Table 5, wild cluster bootstrap column.

Run from the project root:
    python run_robustness.py
"""

from Robustness_Pipeline import wild_cluster_bootstrap


def main():
    wild_cluster_bootstrap.main()


if __name__ == "__main__":
    main()
