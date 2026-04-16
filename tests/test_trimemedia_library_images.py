import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "plugins.v2"
    / "fnmediacovergenerator"
    / "utils"
    / "trimemedia_library_images.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location(
        "fnmediacovergenerator_trimemedia_library_images",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TrimemediaLibraryImagesTests(unittest.TestCase):
    def test_collect_library_item_image_paths_walks_directories_and_uses_details(self):
        module = load_module()
        children = {
            "library": [
                {"guid": "dir-1", "type": "Directory"},
                {"guid": "show-1", "type": "TV"},
            ],
            "dir-1": [
                {"guid": "movie-1", "type": "Movie"},
                {"guid": "movie-2", "type": "Movie"},
            ],
        }
        details = {
            "show-1": {"guid": "show-1", "posters": "/img/show-1.jpg"},
            "movie-1": {"guid": "movie-1", "poster": "/img/movie-1.jpg"},
            "movie-2": {"guid": "movie-2", "posters": "/img/movie-2.jpg"},
        }

        result = module.collect_library_item_image_paths(
            library_guid="library",
            fetch_children=lambda parent_guid: children.get(parent_guid, []),
            fetch_details=lambda item_guid: details.get(item_guid),
            limit=10,
        )

        self.assertEqual(
            result,
            ["/img/show-1.jpg", "/img/movie-1.jpg", "/img/movie-2.jpg"],
        )

    def test_merge_unique_image_urls_preserves_first_seen_order(self):
        module = load_module()

        result = module.merge_unique_image_urls(
            ["https://a.jpg", "https://b.jpg"],
            ["https://b.jpg", "https://c.jpg", "", None, "https://d.jpg"],
            limit=4,
        )

        self.assertEqual(
            result,
            ["https://a.jpg", "https://b.jpg", "https://c.jpg", "https://d.jpg"],
        )

    def test_prefer_supplemental_urls_over_library_image_list(self):
        module = load_module()

        result = module.prefer_supplemental_image_urls(
            base_urls=["https://base-1.jpg", "https://base-2.jpg"],
            supplemental_urls=["https://item-1.jpg", "https://item-2.jpg"],
            limit=9,
        )

        self.assertEqual(
            result,
            ["https://item-1.jpg", "https://item-2.jpg"],
        )


if __name__ == "__main__":
    unittest.main()
