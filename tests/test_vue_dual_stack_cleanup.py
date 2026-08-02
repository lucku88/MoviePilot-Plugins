import importlib.util
import json
import socket
import sys
import unittest
from pathlib import Path

from tests.test_vuefarm_backend import _install_moviepilot_stubs


REPO_ROOT = Path(__file__).resolve().parents[1]
VUEFARM_INIT = REPO_ROOT / "plugins.v2" / "vuefarm" / "__init__.py"
VUEPANEL_INIT = REPO_ROOT / "plugins.v2" / "vuepanel" / "__init__.py"
VUEEMOJI_INIT = REPO_ROOT / "plugins.v2" / "vueemoji" / "__init__.py"
VUEFARM_CONFIG = REPO_ROOT / "plugins.v2" / "vuefarm" / "src" / "components" / "Config.vue"
VUEPANEL_PAGE = REPO_ROOT / "plugins.v2" / "vuepanel" / "src" / "components" / "Page.vue"


def _load_plugin(module_name: str, source_path: Path):
    _install_moviepilot_stubs()
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, source_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class VueDualStackCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.farm_source = VUEFARM_INIT.read_text(encoding="utf-8")
        cls.panel_source = VUEPANEL_INIT.read_text(encoding="utf-8")
        cls.farm_config = VUEFARM_CONFIG.read_text(encoding="utf-8")
        cls.panel_page = VUEPANEL_PAGE.read_text(encoding="utf-8")

    def test_sources_do_not_keep_ipv4_config_or_runtime_patch(self):
        for source in (self.farm_source, self.panel_source):
            self.assertNotIn("_force_ipv4", source)
            self.assertNotIn("lambda: socket.AF_INET", source)

    def test_frontend_does_not_render_or_submit_ipv4_setting(self):
        self.assertNotIn("强制 IPv4", self.farm_config)
        self.assertNotIn("config.force_ipv4", self.farm_config)
        self.assertNotIn("force_ipv4:", self.farm_config)
        self.assertNotIn("force_ipv4", self.panel_page)

    def test_legacy_config_is_ignored_and_not_persisted(self):
        farm_module = _load_plugin("vuefarm_dual_stack_test", VUEFARM_INIT)
        farm = farm_module.VueFarm()
        farm._apply_config({**farm._default_config(), "force_ipv4": True})
        farm_captured = {}
        farm.update_config = lambda payload: farm_captured.update(payload)
        farm._update_config()

        self.assertNotIn("force_ipv4", farm._default_config())
        self.assertNotIn("force_ipv4", farm._get_config(include_options=False))
        self.assertNotIn("force_ipv4", farm_captured)

        panel_module = _load_plugin("vuepanel_dual_stack_test", VUEPANEL_INIT)
        panel = panel_module.VuePanel()
        panel._apply_config({**panel._default_config(), "force_ipv4": True})
        panel_captured = {}
        panel.update_config = lambda payload: panel_captured.update(payload)
        panel._update_config()

        self.assertNotIn("force_ipv4", panel._default_config())
        self.assertNotIn("force_ipv4", panel._get_config())
        self.assertNotIn("force_ipv4", panel_captured)

    def test_hot_upgrade_restores_each_plugins_own_legacy_selector(self):
        cases = (
            ("vuefarm_hot_upgrade_test", VUEFARM_INIT, "VueFarm"),
            ("vuepanel_hot_upgrade_test", VUEPANEL_INIT, "VuePanel"),
        )
        for module_name, source_path, class_name in cases:
            with self.subTest(plugin=class_name):
                module = _load_plugin(module_name, source_path)
                plugin = getattr(module, class_name)()
                connection_module = sys.modules["urllib3.util.connection"]
                legacy_selector = eval(
                    compile("lambda: socket.AF_INET", str(source_path), "eval"),
                    {"socket": socket},
                )
                connection_module.allowed_gai_family = legacy_selector
                connection_module.HAS_IPV6 = True

                plugin._restore_legacy_address_family_selector()

                self.assertIsNot(legacy_selector, connection_module.allowed_gai_family)
                self.assertEqual(socket.AF_UNSPEC, connection_module.allowed_gai_family())

    def test_hot_upgrade_preserves_selector_from_other_source(self):
        cases = (
            ("vuefarm_foreign_selector_test", VUEFARM_INIT, "VueFarm"),
            ("vuepanel_foreign_selector_test", VUEPANEL_INIT, "VuePanel"),
        )
        for module_name, source_path, class_name in cases:
            with self.subTest(plugin=class_name):
                module = _load_plugin(module_name, source_path)
                plugin = getattr(module, class_name)()
                connection_module = sys.modules["urllib3.util.connection"]
                foreign_selector = eval(
                    compile("lambda: socket.AF_INET", str(VUEEMOJI_INIT), "eval"),
                    {"socket": socket},
                )
                connection_module.allowed_gai_family = foreign_selector

                plugin._restore_legacy_address_family_selector()

                self.assertIs(foreign_selector, connection_module.allowed_gai_family)

    def test_init_plugin_runs_legacy_cleanup_before_runtime_bootstrap(self):
        farm_module = _load_plugin("vuefarm_init_cleanup_test", VUEFARM_INIT)
        farm = farm_module.VueFarm()
        farm_connection = sys.modules["urllib3.util.connection"]
        farm_legacy = eval(
            compile("lambda: socket.AF_INET", str(VUEFARM_INIT), "eval"),
            {"socket": socket},
        )
        farm_connection.allowed_gai_family = farm_legacy
        farm_connection.HAS_IPV6 = True
        observed_farm_selectors = []
        farm._sync_cookie_from_site = lambda silent=True: (
            observed_farm_selectors.append(farm_connection.allowed_gai_family),
            {"success": True},
        )[1]

        farm.init_plugin({"enabled": False})

        self.assertEqual(1, len(observed_farm_selectors))
        self.assertIsNot(farm_legacy, observed_farm_selectors[0])
        self.assertEqual(socket.AF_UNSPEC, observed_farm_selectors[0]())

        panel_module = _load_plugin("vuepanel_init_cleanup_test", VUEPANEL_INIT)
        panel = panel_module.VuePanel()
        panel_connection = sys.modules["urllib3.util.connection"]
        panel_legacy = eval(
            compile("lambda: socket.AF_INET", str(VUEPANEL_INIT), "eval"),
            {"socket": socket},
        )
        panel_connection.allowed_gai_family = panel_legacy
        panel_connection.HAS_IPV6 = True

        panel.init_plugin({"enabled": True}, schedule_bootstrap=False)

        self.assertIsNot(panel_legacy, panel_connection.allowed_gai_family)
        self.assertEqual(socket.AF_UNSPEC, panel_connection.allowed_gai_family())

    def test_release_versions_and_upgrade_notes_are_consistent(self):
        expected = {"VueFarm": "0.2.14", "VuePanel": "0.1.36"}
        market = json.loads((REPO_ROOT / "package.v2.json").read_text(encoding="utf-8"))
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        for key, version in expected.items():
            with self.subTest(plugin=key):
                plugin_dir = "vuefarm" if key == "VueFarm" else "vuepanel"
                class_name = key
                source_path = VUEFARM_INIT if key == "VueFarm" else VUEPANEL_INIT
                module = _load_plugin(f"{plugin_dir}_release_test", source_path)
                package = json.loads((REPO_ROOT / "plugins.v2" / plugin_dir / "package.json").read_text(encoding="utf-8"))
                package_lock = json.loads((REPO_ROOT / "plugins.v2" / plugin_dir / "package-lock.json").read_text(encoding="utf-8"))

                self.assertEqual(version, getattr(module, class_name).plugin_version)
                self.assertEqual(version, package["version"])
                self.assertEqual(version, package_lock["version"])
                self.assertEqual(version, package_lock["packages"][""]["version"])
                self.assertEqual(version, market[key]["version"])
                self.assertIn(f"v{version}", market[key]["history"])
                self.assertIn("IPv4", market[key]["history"][f"v{version}"])
                self.assertIn("IPv6", market[key]["history"][f"v{version}"])

        self.assertIn("| `Vue-农场` | `v0.2.14` |", readme)
        self.assertIn("| `Vue-面板` | `v0.1.36` |", readme)


if __name__ == "__main__":
    unittest.main()
