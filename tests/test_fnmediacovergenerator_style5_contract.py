import ast
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_PATH = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "__init__.py"
STYLE5_PREVIEW_PATH = REPO_ROOT / "images" / "style_5.jpeg"


def _load_tree() -> tuple[ast.AST, str]:
    source = INIT_PATH.read_text(encoding="utf-8")
    return ast.parse(source), source


def _imported_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.name)
    return names


def _method_source(tree: ast.AST, source: str, class_name: str, method_name: str) -> str:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return ast.get_source_segment(source, item) or ""
    return ""


class FnMediaCoverGeneratorStyle5ContractTests(unittest.TestCase):
    def test_init_module_has_style5_import_wiring(self):
        tree, _ = _load_tree()
        names = _imported_names(tree)

        self.assertIn("create_style_static_5", names)
        self.assertIn("pick_style5_source_urls", names)
        self.assertIn("remember_style5_primary", names)
        self.assertIn("resolve_style5_render_mode", names)
        self.assertIn("select_style5_image_urls", names)

    def test_style5_is_wired_to_style_ui_and_generation_methods(self):
        tree, source = _load_tree()

        select_index_source = _method_source(tree, source, "FnMediaCoverGenerator", "_select_style_index")
        self.assertIn("min(5", select_index_source)

        compose_source = _method_source(tree, source, "FnMediaCoverGenerator", "__compose_cover_style")
        self.assertIn("static_5", compose_source)

        resolve_ui_source = _method_source(tree, source, "FnMediaCoverGenerator", "__resolve_cover_style_ui")
        self.assertIn("static_5", resolve_ui_source)

        style_parts_source = _method_source(tree, source, "FnMediaCoverGenerator", "__get_cover_style_parts")
        self.assertIn("min(5", style_parts_source)

        required_items_source = _method_source(tree, source, "FnMediaCoverGenerator", "__get_required_items")
        self.assertIn("static_5", required_items_source)

        style_cards_source = _method_source(tree, source, "FnMediaCoverGenerator", "__build_page_style_cards")
        self.assertIn("range(1, 6)", style_cards_source)

        preview_source = _method_source(tree, source, "FnMediaCoverGenerator", "__style_preview_src")
        self.assertIn("min(5", preview_source)

        generate_source = _method_source(tree, source, "FnMediaCoverGenerator", "_generate_image_from_path")
        self.assertIn("static_5", generate_source)
        self.assertIn("create_style_static_5", generate_source)

    def test_style5_source_preparation_tracks_last_primary_state(self):
        tree, source = _load_tree()
        method_source = _method_source(
            tree,
            source,
            "FnMediaCoverGenerator",
            "_expand_trimemedia_library_image_urls",
        )

        self.assertIn("style5_last_primary_urls", method_source)
        self.assertIn("pick_style5_source_urls", method_source)
        self.assertIn("select_style5_image_urls", method_source)
        self.assertIn("remember_style5_primary", method_source)
        self.assertIn("resolve_style5_render_mode", method_source)

    def test_style5_preview_image_exists(self):
        self.assertTrue(STYLE5_PREVIEW_PATH.exists())


if __name__ == "__main__":
    unittest.main()
