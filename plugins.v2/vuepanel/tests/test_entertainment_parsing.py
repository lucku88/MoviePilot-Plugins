import importlib.util
import sys
import types
import unittest
from pathlib import Path


def load_vuepanel_class():
    class DummyScheduler:
        def __init__(self, *args, **kwargs):
            pass

        def add_job(self, *args, **kwargs):
            pass

        def remove_all_jobs(self):
            pass

        def shutdown(self):
            pass

        def start(self):
            pass

        @property
        def running(self):
            return False

    class DummyCronTrigger:
        @classmethod
        def from_crontab(cls, *args, **kwargs):
            return cls()

    class DummyPluginBase:
        def get_data(self, *args, **kwargs):
            return None

        def save_data(self, *args, **kwargs):
            pass

        def update_config(self, *args, **kwargs):
            pass

        def post_message(self, *args, **kwargs):
            pass

    class DummyLogger:
        def info(self, *args, **kwargs):
            pass

        def warning(self, *args, **kwargs):
            pass

        def error(self, *args, **kwargs):
            pass

    class DummySchedulerFacade:
        def update_plugin_job(self, *args, **kwargs):
            pass

        def remove_plugin_job(self, *args, **kwargs):
            pass

    requests_mod = types.ModuleType("requests")
    requests_mod.Session = type("Session", (), {})
    requests_mod.Response = type("Response", (), {})
    requests_mod.exceptions = types.SimpleNamespace(
        SSLError=type("SSLError", (Exception,), {}),
        Timeout=type("Timeout", (Exception,), {}),
        RequestException=type("RequestException", (Exception,), {}),
    )

    sys.modules.setdefault("requests", requests_mod)
    adapters_mod = types.ModuleType("requests.adapters")
    adapters_mod.HTTPAdapter = type("HTTPAdapter", (), {})
    sys.modules.setdefault("requests.adapters", adapters_mod)

    urllib3_mod = types.ModuleType("urllib3")
    urllib3_util_mod = types.ModuleType("urllib3.util")
    urllib3_util_mod.Retry = type("Retry", (), {})
    urllib3_mod.util = urllib3_util_mod
    sys.modules.setdefault("urllib3", urllib3_mod)
    sys.modules.setdefault("urllib3.util", urllib3_util_mod)
    urllib3_conn_mod = types.ModuleType("urllib3.util.connection")
    urllib3_conn_mod.allowed_gai_family = None
    urllib3_util_mod.connection = urllib3_conn_mod
    sys.modules.setdefault("urllib3.util.connection", urllib3_conn_mod)

    app_config_mod = types.ModuleType("app.core.config")
    app_config_mod.settings = types.SimpleNamespace(TZ="Asia/Shanghai")
    sys.modules.setdefault("app.core.config", app_config_mod)
    app_log_mod = types.ModuleType("app.log")
    app_log_mod.logger = DummyLogger()
    sys.modules.setdefault("app.log", app_log_mod)
    app_plugins_mod = types.ModuleType("app.plugins")
    app_plugins_mod._PluginBase = DummyPluginBase
    sys.modules.setdefault("app.plugins", app_plugins_mod)
    app_scheduler_mod = types.ModuleType("app.scheduler")
    app_scheduler_mod.Scheduler = DummySchedulerFacade
    sys.modules.setdefault("app.scheduler", app_scheduler_mod)
    app_schemas_mod = types.ModuleType("app.schemas")
    app_schemas_mod.NotificationType = types.SimpleNamespace(Plugin="Plugin")
    sys.modules.setdefault("app.schemas", app_schemas_mod)

    apscheduler_mod = types.ModuleType("apscheduler")
    apscheduler_schedulers_mod = types.ModuleType("apscheduler.schedulers")
    apscheduler_triggers_mod = types.ModuleType("apscheduler.triggers")
    sys.modules.setdefault("apscheduler", apscheduler_mod)
    sys.modules.setdefault("apscheduler.schedulers", apscheduler_schedulers_mod)
    sys.modules.setdefault("apscheduler.triggers", apscheduler_triggers_mod)
    apscheduler_background_mod = types.ModuleType("apscheduler.schedulers.background")
    apscheduler_background_mod.BackgroundScheduler = DummyScheduler
    sys.modules.setdefault("apscheduler.schedulers.background", apscheduler_background_mod)
    apscheduler_cron_mod = types.ModuleType("apscheduler.triggers.cron")
    apscheduler_cron_mod.CronTrigger = DummyCronTrigger
    sys.modules.setdefault("apscheduler.triggers.cron", apscheduler_cron_mod)

    plugin_path = Path(__file__).resolve().parents[1] / "__init__.py"
    spec = importlib.util.spec_from_file_location("vuepanel_under_test", plugin_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VuePanel


class EntertainmentParsingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VuePanel = load_vuepanel_class()

    def test_parse_entertainment_page_keeps_only_available_shout_targets(self):
        html = """
        <form class="live-shout-form" method="post">
          <input name="live_cabinet_action" value="live_cabinet_shout">
          <input name="cabinet_no" value="1">
          <input name="slot_index" value="1">
          <input name="doll_key" value="two_b">
          <input name="slot_owner" value="10867">
          <button type="submit">为TA呐喊</button>
        </form>
        <form class="live-shout-form" method="post">
          <input name="live_cabinet_action" value="live_cabinet_shout">
          <input name="cabinet_no" value="1">
          <input name="slot_index" value="2">
          <input name="doll_key" value="plato">
          <input name="slot_owner" value="10867">
          <button type="submit" disabled>今日已呐喊</button>
        </form>
        <button class="live-emoji-shout-btn" data-cabinet="1" data-used="0" data-limit="1">一键呐喊舞台</button>
        <button class="live-emoji-shout-btn" data-cabinet="2" data-used="1" data-limit="1" disabled>今日已达上限</button>
        """

        parsed = self.VuePanel._parse_siqi_entertainment_page(html)

        self.assertEqual(
            parsed["cabinet_forms"],
            [
                {
                    "cabinet_no": "1",
                    "slot_index": "1",
                    "doll_key": "two_b",
                    "slot_owner": "10867",
                }
            ],
        )
        self.assertEqual(parsed["stage_buttons"], [{"cabinet_no": "1", "used": "0", "limit": "1"}])

    def test_extract_self_magic_reward_from_success_message(self):
        self.assertEqual(self.VuePanel._extract_self_magic_reward("你获得魔力 +34"), 34)
        self.assertEqual(self.VuePanel._extract_self_magic_reward("主人获得魔力 +6，你获得魔力 +7"), 7)
        self.assertEqual(self.VuePanel._extract_self_magic_reward("没有收益"), 0)


if __name__ == "__main__":
    unittest.main()
