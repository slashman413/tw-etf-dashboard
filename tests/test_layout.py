"""Guards for the src/ layout: every module compiles, run.py resolves names, LLM config renders."""
import py_compile
import subprocess
import sys
import unittest

from twetf import llm, paths

ROOT = paths.ROOT


class Layout(unittest.TestCase):
    def test_all_modules_compile(self):
        for p in (ROOT / "src").rglob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_no_scripts_left_at_root(self):
        self.assertEqual(sorted(p.name for p in ROOT.glob("*.py")), ["run.py"])

    def test_run_py_lists_and_rejects(self):
        out = subprocess.run([sys.executable, str(ROOT / "run.py"), "--list"],
                             capture_output=True, text=True, check=True).stdout
        self.assertIn("pipeline   ci_update", out)
        r = subprocess.run([sys.executable, str(ROOT / "run.py"), "no_such_script"], capture_output=True)
        self.assertEqual(r.returncode, 2)

    def test_names_are_unique_across_layers(self):
        names = [p.stem for layer in ("fetchers", "analyzers", "renderers", "pipeline", "oneoff")
                 for p in (ROOT / "src" / "twetf" / layer).glob("*.py") if p.stem != "__init__"]
        self.assertEqual(len(names), len(set(names)))

    def test_published_files_stay_at_root(self):
        self.assertEqual(paths.DASHBOARD.parent, ROOT)
        self.assertEqual(paths.SERIES_MAP.parent, ROOT)   # fetched by dashboard.html at runtime


class LlmConfig(unittest.TestCase):
    def test_every_task_renders(self):
        sample = dict(url="u", raw_text="t", language="py", code="c", persona="p", count=3,
                      topic="x", format_instructions="f", content="c")
        for name in llm.config()["tasks"]:
            req = llm.build_request(name, **sample)
            self.assertTrue(req["model"].startswith("claude-"))
            self.assertNotIn("{", req["messages"][0]["content"].replace("{c}", ""))


if __name__ == "__main__":
    unittest.main()
