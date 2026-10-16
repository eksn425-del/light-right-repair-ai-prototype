"""Newly executed aggregate/statistical tests, separate from physical validation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("stats_audit", ROOT/"icores_2027/scripts/stats_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class FormulaTests(unittest.TestCase):
    def test_zero_range_normalization(self):
        np.testing.assert_array_equal(audit.normalize([0, 0, 0], 0, 0), [0, 0, 0])

    def test_fixed_bounds_not_refit_or_clipped(self):
        np.testing.assert_array_equal(audit.normalize([2, 4, 12], 0, 10), [.2, .4, 1.2])

    def test_formula_and_constant_N_weight(self):
        f = pd.DataFrame({"A": [0., 1.], "H": [0., 1.], "V": [0., 1.], "N": [0., 0.]})
        bounds = {k: {"lower": 0, "upper": 0 if k == "N" else 1} for k in audit.FIELDS}
        np.testing.assert_allclose(audit.score(f, bounds), [.2, .85])
        modified = audit.score(f, bounds, {**audit.WEIGHTS, "N": .25})
        np.testing.assert_allclose(modified-audit.score(f, bounds), .2)

    def test_exact_k_tie_policy_is_explicit(self):
        f = pd.DataFrame({"pair_key": ["C10,C11", "C2,C3", "C4,C5"], "x": [9, 9, 0]})
        self.assertEqual(audit.top_set(f, "x", 1, "pair_key_natural_numeric"), {"C2,C3"})
        self.assertEqual(audit.top_set(f, "x", 1, "pair_key_lexicographic"), {"C10,C11"})
        self.assertEqual(audit.top_set(f, "x", 1, "include_boundary_ties"), {"C2,C3", "C10,C11"})

    def test_float_zero_pvalue_not_presented_exact(self):
        self.assertEqual(audit.p_display(0.), "NUMERICAL_ZERO_NOT_EXACT_ZERO")
        self.assertNotEqual(audit.p_display(1e-20), "0")

    def test_night_mask_and_monotonicity(self):
        active = [False, True, True]
        base = audit.masked_direct_sun_hours([[False, True, False]], active, 30)
        reduced = audit.masked_direct_sun_hours([[False, False, False]], active, 30)
        np.testing.assert_array_equal(base, [.5])
        np.testing.assert_array_equal(reduced, [1.])
        self.assertGreaterEqual(reduced[0], base[0])

    def test_latent_legacy_night_bug_reproduced_not_claimed_fixed(self):
        self.assertEqual(audit.legacy_night_result(ROOT/audit.INPUTS["enumeration_source"]), .5)
        self.assertEqual(audit.masked_direct_sun_hours([[False]], [False], 30)[0], 0.)


class FrozenEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = audit.read_sources(ROOT)
        cls.comparisons, cls.bounds, cls.info = audit.build_comparisons(cls.data)

    def test_frozen_sample_bytes_pairs_and_disjointness(self):
        result = audit.validate_sample(ROOT, self.data)
        self.assertEqual(result["sha256"], audit.EXPECTED_SAMPLE_SHA256)
        self.assertEqual(result["sample_size"], 20)
        self.assertEqual(result["curated_overlap_count"], 0)
        self.assertTrue(result["pair_order_unchanged"])

    def test_complete_630_pair_universe_and_N(self):
        self.assertEqual(self.info["size"], 630)
        self.assertEqual(self.info["unique_building_ids"], 36)
        self.assertTrue(self.info["all_pairs_present"])
        self.assertEqual(self.info["N_min"], 0)
        self.assertEqual(self.info["N_max"], 0)
        self.assertLess(self.info["stored_score_max_abs_residual"], 1e-10)

    def test_only_N_weight_keeps_ranking(self):
        for case in self.info["N_weight_only_checks"]:
            self.assertTrue(case["rank_order_unchanged"])
            self.assertLess(case["max_constant_shift_residual"], 1e-12)

    def test_cohorts_not_pooled(self):
        self.assertEqual(self.comparisons.comparison_set.value_counts().to_dict(), {"curated23": 23, "heldout20": 20})

    def test_heldout_area_one_grid_cell_mismatch(self):
        heldout = self.comparisons[self.comparisons.comparison_set.eq("heldout20")]
        errors = heldout.error_A_2p5d_minus_hb.abs()
        self.assertEqual(int((errors == 0).sum()), 19)
        self.assertEqual(float(errors.max()), 9)
        self.assertAlmostEqual(float(errors.mean()), .45)

    def test_saved_solar_all_daytime_and_eight_hours(self):
        solar = self.data["solar"]
        self.assertEqual(len(solar), 16)
        self.assertTrue((solar.altitude_deg > 0).all())
        self.assertEqual(float(solar.weight_h.sum()), 8.)

    def test_heldout_scores_are_recomputed_from_frozen_bounds(self):
        h = self.comparisons[self.comparisons.comparison_set.eq("heldout20")].set_index("pair_key")
        archived = self.data["heldout"].set_index("pair_key").loc[h.index]
        np.testing.assert_allclose(h.two_d_score, archived.two_d_score, rtol=0, atol=1e-10)
        np.testing.assert_allclose(h.hb_score, archived.hb_score, rtol=0, atol=1e-10)

    def test_sample_newline_normalization_changes_digest(self):
        import hashlib
        raw = (ROOT/audit.INPUTS["sample"]).read_bytes()
        self.assertIn(b"\r\n", raw)
        self.assertNotEqual(hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(), audit.EXPECTED_SAMPLE_SHA256)


if __name__ == "__main__":
    unittest.main()
