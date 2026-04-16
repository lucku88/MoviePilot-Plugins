import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "library_image_debug.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_library_image_debug",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LibraryImageDebugTests(unittest.TestCase):
    def test_count_non_empty_items_ignores_blank_values(self):
        module = load_module()

        count = module.count_non_empty_items(
            ["https://a.jpg", "", None, "  ", "https://b.jpg", 0]
        )

        self.assertEqual(count, 3)

    def test_format_library_image_stats_includes_returned_and_required_counts(self):
        module = load_module()

        message = module.format_library_image_stats(
            plugin_name="飞牛影视媒体库封面生成",
            server_name="飞牛主机",
            library_name="国漫",
            library_id="abc123",
            returned_count=4,
            required_items=9,
            deduped_count=3,
        )

        self.assertIn("飞牛主机", message)
        self.assertIn("国漫", message)
        self.assertIn("abc123", message)
        self.assertIn("飞牛返回 4 张", message)
        self.assertIn("URL 去重后 3 张", message)
        self.assertIn("当前风格需要 9 张", message)


if __name__ == "__main__":
    unittest.main()
