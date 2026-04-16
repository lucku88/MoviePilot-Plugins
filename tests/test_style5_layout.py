import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style5_layout.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style5_layout",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Style5LayoutTests(unittest.TestCase):
    def test_resolve_style5_eyebrow_matches_library_name(self):
        module = load_module()

        self.assertEqual(module.resolve_style5_eyebrow("电影"), "Movie Library")
        self.assertEqual(module.resolve_style5_eyebrow("日韩剧"), "Series Collection")
        self.assertEqual(module.resolve_style5_eyebrow("国漫"), "Animation Archive")

    def test_choose_style5_anchor_prefers_darker_and_cleaner_side(self):
        module = load_module()

        anchor = module.choose_style5_anchor(
            left_brightness=0.22,
            left_complexity=0.18,
            right_brightness=0.45,
            right_complexity=0.31,
        )

        self.assertEqual(anchor, "left")

    def test_resolve_style5_title_font_size_respects_lower_bound(self):
        module = load_module()

        self.assertEqual(
            module.resolve_style5_title_font_size(
                base_size=170,
                measured_width=1500,
                max_width=1200,
                min_ratio=0.88,
            ),
            149,
        )

    def test_resolve_style5_title_font_size_never_drops_below_one(self):
        module = load_module()

        self.assertGreaterEqual(
            module.resolve_style5_title_font_size(
                base_size=1,
                measured_width=9999,
                max_width=1,
                min_ratio=0,
            ),
            1,
        )

    def test_resolve_style5_title_font_size_with_large_min_ratio_never_exceeds_base_size(self):
        module = load_module()

        self.assertLessEqual(
            module.resolve_style5_title_font_size(
                base_size=10,
                measured_width=100,
                max_width=50,
                min_ratio=1.5,
            ),
            10,
        )
