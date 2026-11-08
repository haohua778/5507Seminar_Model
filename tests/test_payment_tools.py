"""Boundary checks for Task 7 sample selection, without using private microdata."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd
import numpy as np
from Model_Pipeline.results import estimate_stage
from run_payment_checks import independent_tables, table_matches, validate

from DataClean_Pipeline.payment_tools import (
    PAYMENT_VARIABLE, build_payment_samples, load_payment_raw, payment_complete_cases,
)
from Model_Pipeline.payment_tools import supplemental_specs
from Model_Pipeline.stages import SPECS, STAGES


def toy_raw():
    return pd.DataFrame({
        "economy": ["Example"] * 8, "economycode": ["AAA"] * 8, "wgt": [1.0] * 8,
        "con1": [1] * 8, "fin25e2": [1] * 8, "fin25e3": [1, 2, 3, 1, 2, 3, 1, 2],
        "con21": [1, 1, 2, 1, 1, 2, 2, 1], "con22": [1, 2, None, 8, 1, None, None, 2],
        "age": [25, 35, 45, 55, 65, 100, 99, 30], "female": [1] * 8,
        "educ": [1] * 8, "inc_q": [1] * 8, "emp_in": [1] * 8, "urbanicity": [1] * 8,
        "internet_use": [1] * 8, "con9": [1] * 8, "account": [1] * 8,
        "fin25e1": [1, 2, 3, 4, None, 2, 1, 1], "con23": [1, 2, 8, 9, None, 9, 8, 2],
    }, index=[8, 3, 12, 15, 21, 42, 67, 99])


class PaymentSamplesTest(unittest.TestCase):
    def test_yes_no_only_and_row_alignment(self):
        raw = toy_raw()
        before = raw.copy(deep=True)
        common, matched, _ = build_payment_samples(raw)
        self.assertEqual(matched.index.tolist(), [8, 3, 42, 67, 99])
        self.assertEqual(matched[PAYMENT_VARIABLE].tolist(), [1.0, 0.0, 0.0, 1.0, 1.0])
        self.assertEqual(len(common), 8)
        pd.testing.assert_frame_equal(raw, before)

    def test_con23_nonresponse_is_not_a_sample_gate(self):
        common, _, _ = build_payment_samples(toy_raw())
        common["con23"] = None
        self.assertEqual(len(payment_complete_cases(common)), 5)

    def test_age100_only_removed_in_explicit_alternative(self):
        raw = toy_raw()
        common, matched, _ = build_payment_samples(raw, exclude_age100=True)
        self.assertNotIn(42, common.index)
        self.assertIn(67, common.index)  # 99 is retained.
        self.assertNotIn(42, matched.index)
        self.assertEqual(raw.loc[42, "age"], 100)

    def test_stage_filter_and_payment_filter_commute(self):
        common, matched, _ = build_payment_samples(toy_raw())
        for stage in STAGES:
            after = payment_complete_cases(stage.build_sample(common))
            before = stage.build_sample(matched)
            pd.testing.assert_frame_equal(after.sort_index(axis=1), before.sort_index(axis=1))

    def test_specs_do_not_mutate_main_settings(self):
        old = {key: list(value) for key, value in SPECS.items()}
        new = supplemental_specs()
        new["(1)"].append("test_only")
        self.assertEqual(SPECS, old)

    def test_loader_rejects_unknown_codes_and_nonpositive_weights(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.csv"
            raw = toy_raw()
            raw.loc[8, "fin25e1"] = 7
            raw.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "Unexpected fin25e1"):
                load_payment_raw(path)
            raw.loc[8, "fin25e1"] = 1
            raw.loc[8, "wgt"] = 0
            raw.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "positive survey weights"):
                load_payment_raw(path)


class SavedArtifactsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(742)
        n = 180
        frequency = rng.integers(1, 4, n)
        cls.sample = pd.DataFrame({
            "economycode": np.repeat(["AAA", "BBB", "CCC", "DDD", "EEE", "FFF"], 30),
            "wgt": rng.uniform(.25, 3, n), "weekly": (frequency == 1).astype(float),
            "monthly": (frequency == 2).astype(float),
            PAYMENT_VARIABLE: rng.integers(0, 2, n).astype(float),
            "outcome": rng.binomial(1, .35, n).astype(float),
        })
        cls.columns = ["weekly", "monthly", PAYMENT_VARIABLE]
        cls.saved, cls.coef = estimate_stage(cls.sample, specifications={"B": cls.columns})
        cls.expected, cls.expected_coef = independent_tables(cls.sample, cls.columns)
        cls.values = ["estimate", "se", "ci_low", "ci_high", "t", "p_value"]

    def test_independent_reference_matches_all_reported_statistics(self):
        self.assertTrue(table_matches(self.saved, self.expected, ["quantity"], self.values)[0])
        self.assertTrue(table_matches(self.coef, self.expected_coef, ["variable"], self.values)[0])

    def test_equal_offset_on_all_probabilities_is_detected(self):
        bad = self.saved.copy()
        bad.loc[bad.quantity.str.startswith("P_"), "estimate"] += .1
        # Pairwise probability differences remain identical: old identity checks missed this.
        self.assertFalse(table_matches(bad, self.expected, ["quantity"], self.values)[0])

    def test_wrong_p_value_and_weekly_monthly_interval_are_detected(self):
        for field in ["p_value", "ci_low", "ci_high", "se"]:
            bad = self.saved.copy()
            bad.loc[bad.quantity.eq("beta_W_minus_beta_M"), field] += .1
            self.assertFalse(table_matches(bad, self.expected, ["quantity"], self.values)[0])

    def test_wrong_added_variable_coefficient_is_detected(self):
        bad = self.coef.copy()
        bad.loc[bad.variable.eq(PAYMENT_VARIABLE), "estimate"] += .1
        self.assertFalse(table_matches(bad, self.expected_coef, ["variable"], self.values)[0])

    def test_missing_duplicate_and_nan_rows_are_detected(self):
        self.assertFalse(table_matches(self.saved.iloc[:-1], self.expected, ["quantity"], self.values)[0])
        duplicated = pd.concat([self.saved, self.saved.iloc[:1]])
        self.assertFalse(table_matches(duplicated, self.expected, ["quantity"], self.values)[0])
        bad = self.saved.copy()
        bad.loc[bad.quantity.eq("beta_W"), "estimate"] = np.nan
        self.assertFalse(table_matches(bad, self.expected, ["quantity"], self.values)[0])

    def test_failed_recheck_clears_old_pass_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            (output / "validation.csv").write_text("passed\nTrue\n")
            with self.assertRaises(FileNotFoundError):
                validate(output / "missing.csv", output)
            self.assertFalse((output / "validation.csv").exists())


if __name__ == "__main__":
    unittest.main()
