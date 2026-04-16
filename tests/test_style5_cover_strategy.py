import importlib.util
import random
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "style5_cover_strategy.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_style5_cover_strategy",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Style5CoverStrategyTests(unittest.TestCase):
    def test_pick_style5_source_urls_prefers_supplemental_pool(self):
        module = load_module()

        urls, source = module.pick_style5_source_urls(
            base_urls=["https://base-1.jpg", "https://base-2.jpg"],
            supplemental_urls=["https://item-1.jpg", "https://item-2.jpg"],
        )

        self.assertEqual(urls, ["https://item-1.jpg", "https://item-2.jpg"])
        self.assertEqual(source, "supplemental")

    def test_select_style5_image_urls_avoids_last_primary_when_possible(self):
        module = load_module()
        rng = random.Random(7)

        selected, avoided = module.select_style5_image_urls(
            candidate_urls=[
                "https://a.jpg",
                "https://b.jpg",
                "https://c.jpg",
                "https://d.jpg",
            ],
            required_count=4,
            last_primary_url="https://a.jpg",
            rng=rng,
        )

        self.assertEqual(len(selected), 4)
        self.assertNotEqual(selected[0], "https://a.jpg")
        self.assertTrue(avoided)

    def test_select_style5_image_urls_not_avoid_when_last_primary_not_in_pool(self):
        module = load_module()
        rng = random.Random(7)

        selected, avoided = module.select_style5_image_urls(
            candidate_urls=["https://a.jpg", "https://b.jpg", "https://c.jpg"],
            required_count=3,
            last_primary_url="https://not-in-pool.jpg",
            rng=rng,
        )

        self.assertEqual(len(selected), 3)
        self.assertFalse(avoided)

    def test_select_style5_image_urls_not_avoid_when_last_primary_blank(self):
        module = load_module()
        rng = random.Random(7)

        selected, avoided = module.select_style5_image_urls(
            candidate_urls=["https://a.jpg", "https://b.jpg", "https://c.jpg"],
            required_count=3,
            last_primary_url="   ",
            rng=rng,
        )

        self.assertEqual(len(selected), 3)
        self.assertFalse(avoided)

    def test_select_style5_image_urls_returns_empty_when_required_count_is_zero(self):
        module = load_module()
        rng = random.Random(7)

        selected, avoided = module.select_style5_image_urls(
            candidate_urls=["https://a.jpg", "https://b.jpg"],
            required_count=0,
            last_primary_url="https://a.jpg",
            rng=rng,
        )

        self.assertEqual(selected, [])
        self.assertFalse(avoided)

    def test_resolve_style5_render_mode_degrades_without_duplication(self):
        module = load_module()

        self.assertEqual(
            module.resolve_style5_render_mode(4),
            {"mode": "a2_standard", "primary_count": 1, "echo_count": 3},
        )
        self.assertEqual(
            module.resolve_style5_render_mode(2),
            {"mode": "a2_sparse", "primary_count": 1, "echo_count": 1},
        )
        self.assertEqual(
            module.resolve_style5_render_mode(1),
            {"mode": "a1_fallback", "primary_count": 1, "echo_count": 0},
        )

    def test_remember_style5_primary_keeps_newest_items_only(self):
        module = load_module()

        state = {f"server::{index}": f"https://{index}.jpg" for index in range(205)}
        result = module.remember_style5_primary(
            state=state,
            library_key="server::new",
            primary_url="https://new.jpg",
            limit=200,
        )

        self.assertEqual(len(result), 200)
        self.assertEqual(result["server::new"], "https://new.jpg")
        self.assertNotIn("server::0", result)


if __name__ == "__main__":
    unittest.main()
