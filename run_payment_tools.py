"""Run Task 7: python run_payment_tools.py [--data PATH] [--output PATH]."""

import argparse
import hashlib
import importlib.metadata
import platform
from datetime import datetime, timezone
from pathlib import Path

from DataClean_Pipeline.build_sample import DATA_PATH, PROJECT_ROOT
from DataClean_Pipeline.payment_tools import load_payment_raw
from Model_Pipeline.payment_tools import run_payment_analysis, supplemental_specs
from Model_Pipeline.payment_tools_report import write_payment_report
from Model_Pipeline.report import OUTPUT_DIR


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "payment_tools")
    args = parser.parse_args()
    raw = load_payment_raw(args.data)
    tables = run_payment_analysis(raw)
    code_paths = [PROJECT_ROOT / name for name in (
        "run_payment_tools.py", "run_payment_checks.py", "run_checks.py",
        "tests/test_payment_tools.py", "DataClean_Pipeline/build_sample.py",
        "DataClean_Pipeline/payment_tools.py", "Model_Pipeline/stages.py",
        "Model_Pipeline/lpm.py", "Model_Pipeline/results.py", "Model_Pipeline/report.py",
        "Model_Pipeline/payment_tools.py", "Model_Pipeline/payment_tools_report.py",
    )]
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "data_filename": args.data.name, "data_sha256": sha256(args.data), "raw_N": len(raw),
        "python": platform.python_version(),
        "packages": {name: importlib.metadata.version(name) for name in ("numpy", "pandas", "statsmodels", "scipy")},
        "definitions": "User-approved supplement: A/B/C = original (1)/(2)/(3) plus usual_digital_payment; not an upstream definition.",
        "fin25e1_mapping": {"1": 1, "2": 0, "3/4/missing": "excluded from matched comparisons"},
        "specifications": supplemental_specs(),
        "age_policies": {"legacy": "main pipeline unchanged", "exclude_100": "100 treated as missing; main specification only"},
        "code_sha256": {str(path.relative_to(PROJECT_ROOT)): sha256(path) for path in code_paths},
    }
    source_manifest = PROJECT_ROOT / "Docs" / "task7" / "sources.json"
    if source_manifest.exists():
        manifest["source_manifest_sha256"] = sha256(source_manifest)
    write_payment_report(tables, args.output, manifest)
    print(f"Task 7 results written to {args.output}")


if __name__ == "__main__":
    main()
