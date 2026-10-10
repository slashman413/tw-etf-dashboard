"""Offline tests for the CI refresh path: indicators, const patching, the pure refresh()."""
import json
import unittest

from twetf.analyzers import indicators as ind
from twetf.pipeline import ci_update
from twetf.renderers import dashboard_consts as dc


class Indicators(unittest.TestCase):
    def test_ma(self):
        self.assertEqual(ind.ma([1, 2, 3, 4], 2), 3.5)
        self.assertEqual(ind.ma([], 5), 0.0)

    def test_rsi_bounds(self):
        self.assertEqual(ind.rsi(list(range(1, 40))), 100.0)       # only gains
        self.assertEqual(ind.rsi([1, 2]), 50.0)                    # too short
        self.assertLess(ind.rsi(list(range(40, 1, -1))), 1.0)      # only losses

    def test_williams_r(self):
        rows = [["d", 0, c, c - 1, c + 1] for c in range(10, 30)]
        self.assertEqual(ind.williams_r(rows, 14), -6.7)   # hh=30 ll=15 close=29

    def test_append_today_idempotent(self):
        sm = {"2330": {"d": [["2026-10-08", 1, 2, 0.5, 3]]}}
        prices = {"2330": {"open": 5, "close": 6, "low": 4, "high": 7, "volume": 1}, "9999": {}}
        self.assertEqual(ind.append_today(sm, prices, "2026-10-09"), 1)
        self.assertEqual(ind.append_today(sm, prices, "2026-10-09"), 0)
        self.assertEqual(sm["2330"]["d"][-1], ["2026-10-09", 5, 6, 4, 7])


class Consts(unittest.TestCase):
    HTML = 'x;const MOVERS = [{"a":1}];\nconst OTHER = {"b": 2};'

    def test_extract_patch_roundtrip(self):
        self.assertEqual(dc.extract_const(self.HTML, "OTHER"), {"b": 2})
        out = dc.patch_const(self.HTML, "MOVERS", [{"a": 9}])
        self.assertEqual(dc.extract_const(out, "MOVERS"), [{"a": 9}])
        self.assertEqual(dc.extract_const(out, "OTHER"), {"b": 2})

    def test_missing_const_is_noop(self):
        self.assertEqual(dc.patch_const(self.HTML, "NOPE", {}), self.HTML)


class Refresh(unittest.TestCase):
    def test_refresh_patches_every_block(self):
        consts = {
            "MOMENTUM": {"all_momentum": [{"code": "2330", "prior_price": 100, "ma30": 100}]},
            "MOVERS": [],
            "MAREFRESH": {"all_results": [{"code": "2330"}]},
            "DNASIGNALS": {"all_signals": [{"code": "2330"}]},
            "GRANDDATA": {"all_ranked": [{"code": "2330", "fund_pts": 10}]},
        }
        html = "\n".join(f"const {k} = {json.dumps(v)};" for k, v in consts.items())
        sm = {"2330": {"d": [[f"2026-09-{i:02d}", 100, 100 + i, 99, 101 + i] for i in range(1, 30)]}}
        prices = {"2330": {"open": 120, "close": 125, "low": 119, "high": 126, "volume": 1000}}
        out = ci_update.refresh(html, sm, prices, "1151009", today="2026-10-09", stamp="S")
        mom = dc.extract_const(out, "MOMENTUM")
        self.assertEqual(mom["all_momentum"][0]["close"], 125)
        self.assertEqual(mom["all_momentum"][0]["signal"], "STRONG_UP")
        self.assertEqual(dc.extract_const(out, "MOVERS")[0]["code"], "2330")
        self.assertEqual(dc.extract_const(out, "MAREFRESH")["data_date"], "1151009")
        self.assertIn("s4_rsi60", dc.extract_const(out, "DNASIGNALS")["all_signals"][0])
        self.assertIn("mom_pts", dc.extract_const(out, "GRANDDATA")["all_ranked"][0])
        self.assertEqual(sm["2330"]["d"][-1][0], "2026-10-09")


if __name__ == "__main__":
    unittest.main()
