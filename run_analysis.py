"""Run the additional analyses and write the results to Output/analysis/.

Steps, in order (Figure 2 reads the outputs of Figure 1 and the decomposition):
1. Descriptive statistics by payment frequency
2. Figure 1: between versus within economies
3. Decomposition of the joint difference into the contact and sending margins
4. Figure 2: predicted probabilities by stage

Requires Output/<stage>/summary.csv from run_pipeline.py.
Paper: Table 2 (step 1), Figure 1 (step 2), Table 4 (step 3), Figure 2 (step 4).

Run from the project root:
    python run_analysis.py
"""

from Analysis_Pipeline import (
    descriptives_by_frequency,
    figure1_between_within,
    figure2_predicted_probabilities,
    joint_decomposition,
)


def main():
    for step in (descriptives_by_frequency, figure1_between_within,
                 joint_decomposition, figure2_predicted_probabilities):
        print("=" * 78)
        print(step.__name__)
        print("=" * 78)
        step.main()
        print()


if __name__ == "__main__":
    main()
