import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_INIT = REPO_ROOT / "plugins.v2" / "fnmediacovergenerator" / "__init__.py"
PACKAGE_V2 = REPO_ROOT / "package.v2.json"


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


if __name__ == "__main__":
    unittest.main()
