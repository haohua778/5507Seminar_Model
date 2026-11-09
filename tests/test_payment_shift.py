"""Check the paired model-change calculation against an algebraic identity."""

import unittest

import numpy as np
import pandas as pd

from DataClean_Pipeline.payment_tools import PAYMENT_VARIABLE
from Model_Pipeline.lpm import fit_lpm
from Model_Pipeline.payment_shift import paired_weekly_shift


class PairedShiftTest(unittest.TestCase):
    def test_shift_obeys_weighted_omitted_variable_identity(self):
        rng = np.random.default_rng(5107)
        n = 480
        frequency = rng.integers(0, 3, n)
        weekly = (frequency == 0).astype(float)
        monthly = (frequency == 1).astype(float)
        payment = rng.binomial(1, 0.20 + 0.55 * weekly + 0.20 * monthly)
        sample = pd.DataFrame({
            "economycode": np.repeat([f"E{i}" for i in range(8)], n // 8),
            "wgt": rng.uniform(0.5, 2, n),
            "weekly": weekly, "monthly": monthly,
            PAYMENT_VARIABLE: payment.astype(float),
            "outcome": rng.binomial(1, 0.15 + 0.30 * payment + 0.10 * weekly).astype(float),
        })
        base = ["weekly", "monthly"]
        added = [*base, PAYMENT_VARIABLE]
        result = paired_weekly_shift(sample, base, added)

        full = fit_lpm(sample, "outcome", added)
        payment_on_base = fit_lpm(sample.assign(payment_response=payment), "payment_response", base)
        expected_shift = -full.params[PAYMENT_VARIABLE] * payment_on_base.params["weekly"]
        self.assertAlmostEqual(result["shift_pp"], 100 * expected_shift, places=9)
        self.assertAlmostEqual(result["augmented_weekly_pp"] - result["baseline_weekly_pp"],
                               result["shift_pp"], places=9)
        self.assertLess(result["ci_low_pp"], result["ci_high_pp"])
        self.assertTrue(0 <= result["p_value"] <= 1)


if __name__ == "__main__":
    unittest.main()
