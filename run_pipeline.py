"""Run the whole analysis and write the results to Output/.

Steps: sample funnel -> common sample -> three stages, three specifications each.

Run from the project root:
    python run_pipeline.py
"""

from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.report import (
    OUTPUT_DIR,
    write_main_results,
    write_sample_flow,
    write_stage_report,
)
from Model_Pipeline.results import estimate_stage, raw_rates
from Model_Pipeline.stages import STAGES


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
    print(f"Results written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
