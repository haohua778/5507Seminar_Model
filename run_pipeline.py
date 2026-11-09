"""Run the whole analysis and write the results to Output/.

Steps: sample funnel -> common sample -> three stages, three specifications
each -> paper-number checks.

The paper-number checks are the Analysis_Pipeline modules that reproduce
numbers quoted in the paper outside the main tables (Table 2 full-sample
column, economy-level composition, cluster sizes, decomposition checks,
power of Stage 2). Each writes its CSV to Output/analysis/ and returns a
comparison with the paper's values; the comparisons are printed and
collected in Output/analysis/paper_number_checks.md.

Input:  DataBase/Data_Source.csv
Output: Output/sample_flow.csv (Table 1), Output/<stage>/ and
        Output/main_results_table.{md,csv} (Table 3), Output/analysis/ CSV
        files of the paper-number checks and paper_number_checks.md
Paper:  Tables 1 and 3; text numbers of Sections 3.4, 3.5, 3.6 and 4.2;
        Appendix A3

Run from the project root:
    python run_pipeline.py
"""

from Analysis_Pipeline import (
    cluster_sizes,
    decomposition_checks,
    descriptives_full_sample,
    economy_composition,
    stage2_power,
)
from Analysis_Pipeline.paper_targets import print_comparison, write_checks
from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.report import (
    OUTPUT_DIR,
    write_main_results,
    write_main_results_table,
    write_sample_flow,
    write_stage_report,
)
from Model_Pipeline.results import estimate_stage, raw_rates
from Model_Pipeline.stages import STAGES

PAPER_CHECKS = [
    descriptives_full_sample,
    economy_composition,
    cluster_sizes,
    decomposition_checks,
    stage2_power,
]


def main():
    common, flow = build_common_sample(load_raw())
    write_sample_flow(flow)
    print(flow.to_string(index=False))
    print()

    summaries = []
    for stage in STAGES:
        sample = stage.build_sample(common)
        summary, coefficients = estimate_stage(sample)
        write_stage_report(stage, sample, summary, coefficients, raw_rates(sample))
        summaries.append(summary)

    print(write_main_results(STAGES, summaries))
    print(write_main_results_table(STAGES, summaries))

    sections = []
    for module in PAPER_CHECKS:
        comparison = module.run(common)
        print_comparison(module.TITLE, comparison)
        sections.append((module.TITLE, comparison))
    checks_path = write_checks(sections)

    print(f"Results written to {OUTPUT_DIR}")
    print(f"Paper-number checks written to {checks_path}")


if __name__ == "__main__":
    main()
