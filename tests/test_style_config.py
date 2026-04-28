import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style_config.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style_config",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StyleConfigTests(unittest.TestCase):
    def test_resolve_static_cover_style_base_prefers_valid_cover_style_when_base_is_stale(self):
        module = load_module()

        result = module.resolve_static_cover_style_base(
            cover_style="static_3",
            cover_style_base="static_5",
        )

        self.assertEqual(result, "static_3")

    def test_sanitize_title_layout_values_clamps_legacy_large_offsets(self):
        module = load_module()

        zh_offset, title_spacing, en_line_spacing = module.sanitize_title_layout_values(
            zh_font_offset="120",
            title_spacing="500",
            en_line_spacing="0",
            title_scale=1.0,
        )

        self.assertEqual(zh_offset, 120.0)
        self.assertEqual(title_spacing, 220.0)
        self.assertEqual(en_line_spacing, 20.0)


if __name__ == "__main__":
    unittest.main()
