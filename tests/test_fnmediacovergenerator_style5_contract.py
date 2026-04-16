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


def _class_method_names(tree: ast.AST, class_name: str) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    names.add(item.name)
    return names


class FnMediaCoverGeneratorStyle5ContractTests(unittest.TestCase):
    def test_init_module_has_style5_import_wiring(self):
        tree, _ = _load_tree()
        names = _imported_names(tree)

        self.assertIn("create_style_static_5", names)
        self.assertIn("pick_style5_source_urls", names)
        self.assertIn("remember_style5_primary", names)
        self.assertIn("resolve_style5_render_mode", names)
        self.assertIn("select_style5_image_urls", names)

    def test_style5_has_entrypoints_and_generation_wiring(self):
        tree, source = _load_tree()
        method_names = _class_method_names(tree, "FnMediaCoverGenerator")

        self.assertIn("api_select_style_5", method_names)
        self.assertIn("select_style_5", source)
        self.assertIn('"title": "风格5"', source)
        self.assertIn('"value": "static_5"', source)

        generate_source = _method_source(
            tree, source, "FnMediaCoverGenerator", "_generate_image_from_path"
        )
        self.assertIn('if self._cover_style == "static_5"', generate_source)
        self.assertIn("create_style_static_5", generate_source)

    def test_style5_source_preparation_tracks_last_primary_state(self):
        tree, source = _load_tree()
        expand_source = _method_source(
            tree,
            source,
            "FnMediaCoverGenerator",
            "_expand_trimemedia_library_image_urls",
        )
        prepare_source = _method_source(
            tree,
            source,
            "FnMediaCoverGenerator",
            "_prepare_library_images_from_urls",
        )

        self.assertIn("style5_last_primary_urls", expand_source)
        self.assertIn("pick_style5_source_urls", expand_source)
        self.assertIn("select_style5_image_urls", expand_source)
        self.assertIn("remember_style5_primary", expand_source)
        self.assertIn("resolve_style5_render_mode", expand_source)
        self.assertIn('if self._cover_style == "static_5"', prepare_source)
        self.assertIn("style_5 保留真实张数", prepare_source)

    def test_style_preview_url_keeps_existing_repository_baseline(self):
        tree, source = _load_tree()
        preview_source = _method_source(
            tree,
            source,
            "FnMediaCoverGenerator",
            "__style_preview_src",
        )
        self.assertIn("raw.githubusercontent.com/justzerock/MoviePilot-Plugins/main/images/", preview_source)

    def test_style5_preview_image_exists(self):
        self.assertTrue(STYLE5_PREVIEW_PATH.exists())


if __name__ == "__main__":
    unittest.main()
