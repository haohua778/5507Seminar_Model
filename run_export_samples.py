"""Write the derived analysis samples to CSV files.

The common sample and the three estimation samples are built in memory by
every entry script; this script writes them out so that the derived data
can be shipped next to the code. The files hold the recoded model variables
plus the identifiers and raw answers that build_sample.py reads, one row
per respondent, in the order of the raw file.

Input:  DataBase/Data_Source.csv
Output: Output/derived_samples/common_sample.csv       16,251 respondents
        Output/derived_samples/stage1_contact.csv      16,251
        Output/derived_samples/stage2_send.csv          4,768
        Output/derived_samples/stage3_joint.csv        16,249
        Each stage file is the common sample restricted to the stage's
        respondents, with the stage outcome added as the column `outcome`.
Paper:  the samples behind Tables 1 to 5 and Figures 1 and 2

Run from the project root:
    python run_export_samples.py
"""

from DataClean_Pipeline.build_sample import PROJECT_ROOT, build_common_sample, load_raw
from Model_Pipeline.stages import STAGES

OUTPUT_DIR = PROJECT_ROOT / "Output" / "derived_samples"


def main():
    common, _ = build_common_sample(load_raw())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    common.to_csv(OUTPUT_DIR / "common_sample.csv", index=False)
    print(f"common_sample.csv: {len(common):,} respondents, {common['economycode'].nunique()} economies")
    for stage in STAGES:
        sample = stage.build_sample(common)
        sample.to_csv(OUTPUT_DIR / f"{stage.key}.csv", index=False)
        print(f"{stage.key}.csv: {len(sample):,} respondents")
    print(f"Written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
