"""What is estimated: three stages and three specifications.

Each stage takes the common sample, keeps the respondents it needs, and adds
its outcome as the column `outcome`. The three specifications add controls
step by step and are the same for every stage.
"""

from dataclasses import dataclass
from typing import Callable

from DataClean_Pipeline.build_sample import DEMOGRAPHICS, DIGITAL, FREQUENCY

OUTCOME = "outcome"

SPECS = {
    "(1)": FREQUENCY,
    "(2)": FREQUENCY + DEMOGRAPHICS,
    "(3)": FREQUENCY + DEMOGRAPHICS + DIGITAL,
}
SPEC_LABELS = {
    "(1)": "Country FE only",
    "(2)": "Main: demographics",
    "(3)": "Plus digital engagement",
}
MAIN_SPEC = "(2)"


def stage1_contact(common):
    """Stage 1: reported scam contact. Uses the whole common sample."""
    sample = common.copy()
    sample[OUTCOME] = (sample["con21"] == 1).astype(float)
    return sample


def stage2_send(common):
    """Stage 2: sending money, conditional on reported contact."""
    contacted = common["con21"] == 1
    answered = common["con22"].isin([1, 2])

    sample = common[contacted & answered].copy()
    sample[OUTCOME] = (sample["con22"] == 1).astype(float)
    return sample


def stage3_joint(common):
    """Stage 3: reported contact and sending money, as one joint event.

    Contacted respondents who answered con22 with 8 or 9 are dropped,
    because it is unknown whether they sent money.
    """
    contacted = common["con21"] == 1
    answered = common["con22"].isin([1, 2])
    outcome_unknown = contacted & ~answered

    sample = common[~outcome_unknown].copy()
    sent_money = (sample["con21"] == 1) & (sample["con22"] == 1)
    sample[OUTCOME] = sent_money.astype(float)
    return sample


@dataclass
class Stage:
    key: str                  # folder name under Output/
    title: str
    sample_note: str
    outcome_note: str
    build_sample: Callable


STAGES = [
    Stage(
        key="stage1_contact",
        title="Stage 1: reported scam contact",
        sample_note="Common sample",
        outcome_note="con21: 1 -> 1, 2 -> 0",
        build_sample=stage1_contact,
    ),
    Stage(
        key="stage2_send",
        title="Stage 2: sending money conditional on reported contact",
        sample_note=("Common sample with con21 = 1 and con22 in {1,2} "
                     "(conditional on reported contact)"),
        outcome_note="con22: 1 -> 1, 2 -> 0; 8 and 9 dropped",
        build_sample=stage2_send,
    ),
    Stage(
        key="stage3_joint",
        title="Stage 3: reported contact and sending money",
        sample_note="Common sample without con21 = 1 and con22 in {8,9}",
        outcome_note=("1 = contacted and sent money; "
                      "0 = not contacted, or contacted but did not send"),
        build_sample=stage3_joint,
    ),
]
