import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "history_selection.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_history_selection",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class HistorySelectionTests(unittest.TestCase):
    def test_toggle_history_selection_adds_and_removes_target(self):
        module = load_module()

        selected = module.toggle_history_selection(["/a.png"], "/b.png")
        self.assertEqual(selected, ["/a.png", "/b.png"])

        selected = module.toggle_history_selection(selected, "/a.png")
        self.assertEqual(selected, ["/b.png"])

    def test_retain_history_selection_keeps_only_visible_paths(self):
        module = load_module()

        retained = module.retain_history_selection(
            ["/a.png", "/b.png", "/c.png"],
            ["/b.png", "/d.png"],
        )

        self.assertEqual(retained, ["/b.png"])

    def test_resolve_history_delete_targets_supports_single_and_batch(self):
        module = load_module()

        targets = module.resolve_history_delete_targets(
            file="/a.png",
            data={"file": "/b.png", "files": ["/c.png", "", "/b.png"]},
        )

        self.assertEqual(targets, ["/a.png", "/b.png", "/c.png"])


if __name__ == "__main__":
    unittest.main()
