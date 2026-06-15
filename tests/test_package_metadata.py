import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_INIT = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "__init__.py"
PACKAGE_V2 = REPO_ROOT / "package.v2.json"
PLUGIN_REQUIREMENTS = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "requirements.txt"
TEXT_RENDERING = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "style" / "text_rendering.py"


class PackageMetadataTests(unittest.TestCase):
    def test_fnmediacovergenerator_market_version_matches_plugin_version(self):
        init_text = PLUGIN_INIT.read_text(encoding="utf-8")
        version_match = re.search(r'plugin_version\s*=\s*"([^"]+)"', init_text)

        self.assertIsNotNone(version_match)
        plugin_version = version_match.group(1)

        package_data = json.loads(PACKAGE_V2.read_text(encoding="utf-8"))
        market_entry = package_data["FnMediaCoverGenerator"]

        self.assertEqual(plugin_version, market_entry["version"])
        self.assertIn(f"v{plugin_version}", market_entry["history"])

    def test_fnmediacovergenerator_requirements_do_not_exact_pin_shared_runtime_packages(self):
        requirements = [
            line.strip()
            for line in PLUGIN_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

        exact_pins = [line for line in requirements if "==" in line]

        self.assertEqual(
            exact_pins,
            [],
            "插件运行在 MoviePilot 共享环境中，requirements 不应精确锁死主环境已有依赖",
        )
        self.assertTrue(any(line.lower().startswith("fonttools>=") for line in requirements))
        self.assertTrue(any(line.lower().startswith("brotli>=") for line in requirements))

    def test_fnmediacovergenerator_runtime_dependency_repair_uses_compatible_ranges(self):
        source = TEXT_RENDERING.read_text(encoding="utf-8")

        self.assertNotIn("fonttools==", source.lower())
        self.assertNotIn("brotli==", source.lower())
        self.assertIn("fonttools>=", source.lower())
        self.assertIn("brotli>=", source.lower())


if __name__ == "__main__":
    unittest.main()
