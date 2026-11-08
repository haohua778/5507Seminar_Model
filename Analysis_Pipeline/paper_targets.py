"""Compare numbers computed by the pipeline with the numbers written in the paper.

Several modules in Analysis_Pipeline/ reproduce numbers that were first
computed by hand for the paper. Each of them lists its paper values as
targets, computes the same quantities from the data, and returns a
comparison table built with the helpers here. run_pipeline.py prints the
tables and writes them all to Output/analysis/paper_number_checks.md.

Nothing is tuned to hit a target. A row that does not match points to a
number in the paper, or a definition, that needs a second look.
"""

import numpy as np
import pandas as pd

from DataClean_Pipeline.build_sample import PROJECT_ROOT

CHECKS_PATH = PROJECT_ROOT / "Output" / "analysis" / "paper_number_checks.md"
COLUMNS = ["quantity", "computed", "target", "difference", "matches"]


def decimals_of(target):
    """Number of decimals the paper reports, read from the target itself."""
    text = repr(target)
    return len(text.split(".")[1]) if "." in text else 0


def compare(quantity, computed, target):
    """One comparison row. `target` is the number (or text) as it appears in the paper.

    A numeric target matches when the computed value rounds to it at the
    paper's precision. A text target (for example a list of economies)
    matches when the text is identical.
    """
    if isinstance(target, str):
        return {"quantity": quantity, "computed": computed, "target": target,
                "difference": "", "matches": computed == target}
    return {"quantity": quantity, "computed": computed, "target": target,
            "difference": computed - target,
            "matches": round(float(computed), decimals_of(target)) == target}


def comparison_table(rows):
    # dtype=object keeps integer counts as integers next to floats.
    return pd.DataFrame(rows, columns=COLUMNS, dtype=object)


def format_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    return f"{value:.4f}"


def markdown_comparison(title, table):
    header = ["Quantity", "Computed", "Paper", "Computed - paper", "Matches"]
    lines = [f"## {title}", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for _, row in table.iterrows():
        cells = [row["quantity"], format_value(row["computed"]), format_value(row["target"]),
                 format_value(row["difference"]), "yes" if row["matches"] else "NO"]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def print_comparison(title, table):
    print(markdown_comparison(title, table))
    print()


def write_checks(sections):
    """`sections` is a list of (title, comparison table). Writes one Markdown file."""
    intro = (
        "# Paper numbers reproduced by the pipeline\n\n"
        "Written by `run_pipeline.py`. Each table lists a quantity the paper reports, the value "
        "computed from the data by the module named in the section title, the value written in "
        "the paper, and whether the computed value rounds to the paper's value at the paper's "
        "precision. Full-precision values are in the CSV files of `Output/analysis/`.\n\n"
    )
    body = "\n\n".join(markdown_comparison(title, table) for title, table in sections)
    CHECKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHECKS_PATH.write_text(intro + body + "\n", encoding="utf-8")
    return CHECKS_PATH
