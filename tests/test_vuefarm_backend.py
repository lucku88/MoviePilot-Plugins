import importlib.util
import sys
import time
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VUEFARM_INIT = REPO_ROOT / "plugins.v2" / "vuefarm" / "__init__.py"


def _install_moviepilot_stubs():
    requests_module = types.ModuleType("requests")

    class Session:
        def __init__(self):
            self.headers = {}
            self.trust_env = False

        def mount(self, *args, **kwargs):
            return None

    requests_module.Session = Session
    requests_module.Response = type("Response", (), {})
    sys.modules["requests"] = requests_module

    adapters_module = types.ModuleType("requests.adapters")

    class HTTPAdapter:
        def __init__(self, *args, **kwargs):
            return None

    adapters_module.HTTPAdapter = HTTPAdapter
    sys.modules["requests.adapters"] = adapters_module

    urllib3_module = types.ModuleType("urllib3")
    sys.modules["urllib3"] = urllib3_module
    urllib3_util_module = types.ModuleType("urllib3.util")

    class Retry:
        def __init__(self, *args, **kwargs):
            return None

    urllib3_util_module.Retry = Retry
    sys.modules["urllib3.util"] = urllib3_util_module
    urllib3_connection_module = types.ModuleType("urllib3.util.connection")
    urllib3_connection_module.allowed_gai_family = lambda: None
    sys.modules["urllib3.util.connection"] = urllib3_connection_module

    app_module = types.ModuleType("app")
    sys.modules["app"] = app_module

    core_module = types.ModuleType("app.core")
    sys.modules["app.core"] = core_module
    config_module = types.ModuleType("app.core.config")
    config_module.settings = types.SimpleNamespace(TZ="Asia/Shanghai")
    sys.modules["app.core.config"] = config_module

    db_module = types.ModuleType("app.db")
    sys.modules["app.db"] = db_module
    site_oper_module = types.ModuleType("app.db.site_oper")

    class SiteOper:
        def get_by_domain(self, *args, **kwargs):
            return None

    site_oper_module.SiteOper = SiteOper
    sys.modules["app.db.site_oper"] = site_oper_module

    log_module = types.ModuleType("app.log")

    class Logger:
        def info(self, *args, **kwargs):
            return None

        def warning(self, *args, **kwargs):
            return None

        def error(self, *args, **kwargs):
            return None

    log_module.logger = Logger()
    sys.modules["app.log"] = log_module

    plugins_module = types.ModuleType("app.plugins")

    class PluginBase:
        def __init__(self):
            self._data_store = {}
            self._config_store = {}

        def get_data(self, key):
            return self._data_store.get(key)

        def save_data(self, key, value):
            self._data_store[key] = value

        def update_config(self, config):
            self._config_store = dict(config)

        def post_message(self, *args, **kwargs):
            return None

    plugins_module._PluginBase = PluginBase
    sys.modules["app.plugins"] = plugins_module

    scheduler_module = types.ModuleType("app.scheduler")

    class Scheduler:
        def update_plugin_job(self, *args, **kwargs):
            return None

        def reload_plugin_job(self, *args, **kwargs):
            return None

        def remove_plugin_job(self, *args, **kwargs):
            return None

    scheduler_module.Scheduler = Scheduler
    sys.modules["app.scheduler"] = scheduler_module

    schemas_module = types.ModuleType("app.schemas")
    schemas_module.NotificationType = types.SimpleNamespace(Plugin="Plugin")
    sys.modules["app.schemas"] = schemas_module

    apscheduler_module = types.ModuleType("apscheduler")
    sys.modules["apscheduler"] = apscheduler_module
    schedulers_module = types.ModuleType("apscheduler.schedulers")
    sys.modules["apscheduler.schedulers"] = schedulers_module
    background_module = types.ModuleType("apscheduler.schedulers.background")

    class BackgroundScheduler:
        def __init__(self, *args, **kwargs):
            self.running = False

        def add_job(self, *args, **kwargs):
            return None

        def remove_all_jobs(self):
            return None

        def shutdown(self):
            self.running = False

        def start(self):
            self.running = True

    background_module.BackgroundScheduler = BackgroundScheduler

    triggers_module = types.ModuleType("apscheduler.triggers")
    sys.modules["apscheduler.triggers"] = triggers_module
    cron_module = types.ModuleType("apscheduler.triggers.cron")

    class CronTrigger:
        def __init__(self, expression, timezone=None):
            self.expression = expression

        @classmethod
        def from_crontab(cls, expression, timezone=None):
            fields = str(expression).split()
            if len(fields) != 5:
                raise ValueError("Cron 必须包含 5 个字段")
            return cls(expression, timezone=timezone)

        @staticmethod
        def _matches(value, expression):
            if expression == "*":
                return True
            if expression.startswith("*/"):
                return value % int(expression[2:]) == 0
            return value == int(expression)

        def get_next_fire_time(self, previous_fire_time, start_date):
            minute_expr, hour_expr, _, _, _ = self.expression.split()
            candidate = start_date.replace(second=0, microsecond=0)
            if candidate < start_date:
                candidate += timedelta(minutes=1)
            for _ in range(7 * 24 * 60):
                if self._matches(candidate.minute, minute_expr) and self._matches(candidate.hour, hour_expr):
                    return candidate
                candidate += timedelta(minutes=1)
            return None

    cron_module.CronTrigger = CronTrigger
    sys.modules["apscheduler.triggers.cron"] = cron_module
    sys.modules["apscheduler.schedulers.background"] = background_module


def _load_vuefarm():
    _install_moviepilot_stubs()
    module_name = "vuefarm_under_test"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, VUEFARM_INIT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _ready_farm_data(count=20):
    return {
        "success": True,
        "user_bonus": 0,
        "user_stats": {"total_harvest": "500000"},
        "seeds": [
            {
                "id": "4",
                "name": "茄子",
                "icon": "🍆",
                "cost": "3600",
                "grow_time": "259200",
                "base_reward": "4230",
                "unlock_harvest": "500000",
            }
        ],
        "lands": [],
        "user_lands": [
            {
                "land_id": str((idx // 10) + 1),
                "plot_index": str(idx % 10),
                "seed_id": "4",
                "plant_time": str(int(time.time()) - 259300),
                "harvest_time": str(int(time.time()) - 100),
                "is_ready": 1,
            }
            for idx in range(count)
        ],
        "inventory": [],
        "user_logs": [],
    }


class VueFarmBackendTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_vuefarm()
        self.plugin = self.module.VueFarm()
        self.plugin._enabled = True
        self.plugin._notify = False
        self.plugin._force_ipv4 = False
        self.plugin._random_delay_max_seconds = 0

    def test_single_plot_fallback_counts_each_success_once_not_cumulative_inventory(self):
        ready_data = _ready_farm_data(20)
        empty_data = {**ready_data, "user_lands": []}

        self.plugin._harvest_all = lambda session: {
            "success": False,
            "detail": "OCR 未识别出有效验证码",
            "reward": 0,
            "items": [],
        }

        refetch_calls = {"count": 0}

        def refetch_state(*args, **kwargs):
            refetch_calls["count"] += 1
            return ready_data if refetch_calls["count"] == 1 else empty_data

        harvest_calls = {"count": 0}

        def post_action(session, action, payload, retry_network=False):
            self.assertEqual("harvest", action)
            harvest_calls["count"] += 1
            return {
                "success": True,
                "inventory": {
                    "seed_id": 4,
                    "name": "茄子",
                    "icon": "🍆",
                    "quantity": harvest_calls["count"],
                    "unit_reward": 4230,
                },
            }

        self.plugin._refetch_state_until = refetch_state
        self.plugin._post_action = post_action

        result = self.plugin._harvest_ready_plots(object(), ready_data)
        lines = self.plugin._build_result_lines(
            True,
            False,
            False,
            result["harvest_items"],
            [],
            [],
            {},
            "暂无成熟作物",
            harvest_success_count=result["harvested_count"],
            harvest_note_detail=result["note"],
        )

        self.assertTrue(result["success"])
        self.assertEqual(20, result["harvested_count"])
        self.assertIn("✅收菜：🍆茄子×20", lines)
        self.assertNotIn("✅收菜：🍆茄子×210", lines)

    def test_prefer_mushroom_when_total_harvest_contains_commas(self):
        data = {
            "success": True,
            "user_stats": {"total_harvest": "5,000,000"},
            "seeds": [
                {
                    "id": "4",
                    "name": "茄子",
                    "icon": "🍆",
                    "cost": "3600",
                    "grow_time": "259200",
                    "base_reward": "4230",
                    "unlock_harvest": "500000",
                },
                {
                    "id": "5",
                    "name": "蘑菇",
                    "icon": "🍄",
                    "cost": "8400",
                    "grow_time": "604800",
                    "base_reward": "10080",
                    "unlock_harvest": "5000000",
                },
            ],
        }
        self.plugin._prefer_seed = "蘑菇"

        picked = self.plugin._pick_seed(data)

        self.assertIsNotNone(picked)
        self.assertEqual("蘑菇", picked["name"])

    def test_prefer_mushroom_when_seed_reports_unlocked_before_stats_refresh(self):
        data = {
            "success": True,
            "user_stats": {"total_harvest": "4,999,999"},
            "seeds": [
                {
                    "id": "4",
                    "name": "茄子",
                    "icon": "🍆",
                    "cost": "3600",
                    "grow_time": "259200",
                    "base_reward": "4230",
                    "unlock_harvest": "500000",
                    "unlocked": True,
                },
                {
                    "id": "5",
                    "name": "蘑菇",
                    "icon": "🍄",
                    "cost": "8400",
                    "grow_time": "604800",
                    "base_reward": "10080",
                    "unlock_harvest": "5000000",
                    "unlocked": True,
                },
            ],
        }
        self.plugin._prefer_seed = "蘑菇"

        picked = self.plugin._pick_seed(data)
        seed_shop = self.plugin._build_seed_shop(data)

        self.assertIsNotNone(picked)
        self.assertEqual("蘑菇", picked["name"])
        self.assertTrue(next(seed for seed in seed_shop if seed["name"] == "蘑菇")["unlocked"])

    def test_legacy_disabled_ocr_setting_is_ignored_and_batch_still_runs(self):
        ready_data = _ready_farm_data(3)
        empty_data = {**ready_data, "user_lands": []}
        calls = []
        config = self.plugin._default_config()
        config["enable_ocr_harvest"] = False
        self.plugin._apply_config(config)
        self.module.settings.OCR_HOST = "http://moviepilot-ocr:3000"
        self.plugin._harvest_all = lambda session: calls.append("batch") or {
            "success": True,
            "detail": "",
            "items": [{"name": "茄子", "qty": 3, "unit": 4230, "icon": "🍆"}],
        }
        self.plugin._refetch_state_until = lambda *args, **kwargs: empty_data
        self.plugin._harvest_single_plot = lambda *args, **kwargs: self.fail("批量成功后不应逐坑位收菜")

        result = self.plugin._harvest_ready_plots(object(), ready_data)

        self.assertTrue(result["success"])
        self.assertEqual(3, result["harvested_count"])
        self.assertEqual(["batch"], calls)
        self.assertNotIn("enable_ocr_harvest", self.plugin._get_config(include_options=False))

    def test_missing_moviepilot_ocr_falls_back_to_individual_harvest(self):
        ready_data = _ready_farm_data(2)
        empty_data = {**ready_data, "user_lands": []}
        harvest_calls = []

        self.plugin._harvest_all = lambda session: self.fail("未配置 OCR API 时不应调用批量接口")
        self.plugin._refetch_state_until = lambda *args, **kwargs: empty_data
        self.plugin._harvest_single_plot = lambda session, land_id, plot_index: harvest_calls.append((land_id, plot_index)) or {
            "success": True,
            "items": [{"name": "茄子", "qty": 1, "unit": 4230, "icon": "🍆"}],
        }

        result = self.plugin._harvest_ready_plots(object(), ready_data)

        self.assertTrue(result["success"])
        self.assertEqual(2, result["harvested_count"])
        self.assertEqual([(1, 0), (1, 1)], harvest_calls)
        self.assertIn("未配置", result["note"])

    def test_ocr_batch_is_builtin_without_config_switch(self):
        config = self.plugin._default_config()

        self.assertNotIn("enable_ocr_harvest", config)
        self.assertEqual("moviepilot", config["ocr_provider"])
        self.assertEqual(45, config["harvest_time_budget_seconds"])

    def test_legacy_trwebocr_config_is_forced_to_moviepilot_ocr(self):
        config = self.plugin._default_config()
        config.update({"ocr_provider": "trwebocr", "ocr_api_url": "http://ocr:8089/api/tr-run/"})

        self.plugin._apply_config(config)

        self.assertEqual("moviepilot", self.plugin._ocr_provider)
        self.assertEqual("", self.plugin._ocr_api_url)

    def test_ocr_source_fields_are_not_exposed_in_plugin_config(self):
        config = self.plugin._get_config(include_options=False)

        self.assertNotIn("ocr_provider", config)
        self.assertNotIn("ocr_api_url", config)
        self.assertNotIn("enable_ocr_harvest", config)

    def test_ocr_batch_uses_moviepilot_host_after_legacy_provider_migration(self):
        config = self.plugin._default_config()
        config.update({"enable_ocr_harvest": False, "ocr_provider": "trwebocr", "ocr_api_url": ""})
        self.plugin._apply_config(config)
        self.module.settings.OCR_HOST = "http://moviepilot-ocr:3000"

        self.assertTrue(self.plugin._should_use_ocr_batch_harvest())

    def test_moviepilot_ocr_uses_captcha_base64_endpoint(self):
        captured = {}

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {"result": " aB-12 "}

        def post(url, json=None, timeout=None):
            captured.update({"url": url, "json": json, "timeout": timeout})
            return FakeResponse()

        self.module.settings.OCR_HOST = "http://moviepilot-ocr:3000/"
        self.module.requests.post = post
        self.plugin._ocr_provider = "moviepilot"

        result = self.plugin._recognize_captcha(object(), b"captcha-image")

        self.assertEqual("AB12", result)
        self.assertEqual("http://moviepilot-ocr:3000/captcha/base64", captured["url"])
        self.assertIn("base64_img", captured["json"])

    def test_ai_captcha_receives_absolute_image_url(self):
        captured = {}

        class FakeTool:
            def __init__(self, session_id, user_id):
                return None

            async def run(self, **kwargs):
                captured.update(kwargs)
                return {"success": True, "captcha_text": "xy-789"}

        self.module.settings.AI_AGENT_ENABLE = True
        self.module.RecognizeCaptchaTool = FakeTool
        self.plugin._use_ai_captcha = True
        self.plugin._site_url = "https://si-qi.xyz"

        result = self.plugin._ai_recognize_captcha("/captcha/code.png")

        self.assertEqual("XY789", result)
        self.assertEqual("https://si-qi.xyz/captcha/code.png", captured["image_url"])

    def test_ocr_failure_falls_back_to_ai_before_single_plot_harvest(self):
        ready_data = _ready_farm_data(1)
        calls = []
        self.plugin._ocr_provider = "moviepilot"
        self.plugin._use_ai_captcha = True
        self.module.settings.OCR_HOST = "http://moviepilot-ocr:3000"
        self.plugin._ai_agent_available = lambda: True
        self.plugin._harvest_all = lambda session: calls.append("ocr") or {"success": False, "detail": "OCR 识别失败", "items": []}
        self.plugin._harvest_ai = lambda session: calls.append("ai") or {"success": False, "detail": "AI 识别失败", "items": []}
        self.plugin._refetch_state_until = lambda *args, **kwargs: {**ready_data, "user_lands": []}
        self.plugin._harvest_single_plot = lambda session, land_id, plot_index: calls.append("single") or {
            "success": True,
            "items": [{"name": "茄子", "qty": 1, "unit": 4230, "icon": "🍆"}],
        }

        result = self.plugin._harvest_ready_plots(object(), ready_data)

        self.assertTrue(result["success"])
        self.assertEqual(["ocr", "ai", "single"], calls)
        self.assertIn("逐坑位收菜", result["note"])
        self.assertIsNone(self.plugin._harvest_deadline)
        self.assertIsNone(self.plugin._harvest_batch_deadline)

    def test_batch_harvest_stops_after_three_failed_captcha_attempts(self):
        class FakeResponse:
            content = b"captcha"

            def raise_for_status(self):
                return None

        class FakeSession:
            def get(self, *args, **kwargs):
                return FakeResponse()

        captcha_calls = {"count": 0}

        def post_action(session, action, payload, retry_network=False):
            if action == "get_harvest_all_captcha":
                captcha_calls["count"] += 1
                return {"success": True, "captcha": {"image_url": "/cap.jpg", "imagehash": "hash"}}
            self.fail(f"验证码识别失败时不应提交收菜：{action}")

        self.plugin._post_action = post_action
        self.plugin._recognize_captcha = lambda session, image_content: ""

        result = self.plugin._harvest_all(FakeSession())

        self.assertFalse(result["success"])
        self.assertEqual(3, captcha_calls["count"])
        self.assertIn("OCR", result["detail"])

    def test_bootstrap_runs_full_job_after_refresh_when_ready(self):
        run_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {"highlights": {"ready_count": 1}}
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
        }

        result = self.plugin._bootstrap_worker()

        self.assertEqual([(True, "bootstrap")], run_calls)
        self.assertEqual("补跑完成", result["message"])

    def test_scheduled_refresh_runs_full_job_when_next_run_is_overdue(self):
        overdue_ts = int(time.time()) - 60
        run_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {
            "highlights": {"ready_count": 0},
            "next_run_ts": overdue_ts,
        }
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
        }

        result = self.plugin._refresh_worker()

        self.assertEqual([(True, "smart")], run_calls)
        self.assertEqual("补跑完成", result["message"])

    def test_scheduled_pre_refresh_re_registers_final_run_trigger(self):
        next_run_ts = int(time.time()) + 60
        schedule_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {
            "highlights": {"ready_count": 0},
            "next_run_ts": next_run_ts,
        }
        self.plugin._load_saved_next_run = lambda: self.plugin._aware_from_timestamp(next_run_ts)
        self.plugin._schedule_next_run = lambda next_run, reason="", force_run=False: schedule_calls.append(
            (next_run, reason, force_run)
        )

        result = self.plugin._refresh_worker()

        self.assertTrue(result["success"])
        self.assertEqual([(next_run_ts, "scheduled-refresh-final", True)], schedule_calls)

    def test_scheduled_refresh_keeps_previous_manual_plant_time_when_plot_disappears(self):
        next_run_ts = int(time.time()) + 60
        self.plugin._next_run_time = self.plugin._aware_from_timestamp(next_run_ts)
        schedule_calls = []

        def refresh_state(reason, record_run=False):
            self.plugin._next_run_time = None
            return {
                "highlights": {"ready_count": 0},
                "next_run_ts": 0,
            }

        self.plugin._refresh_state = refresh_state
        self.plugin._schedule_next_run = lambda next_run, reason="", force_run=False: schedule_calls.append(
            (next_run, reason, force_run)
        )

        result = self.plugin._refresh_worker()

        self.assertTrue(result["success"])
        self.assertEqual([(next_run_ts, "scheduled-refresh-final", True)], schedule_calls)

    def test_refresh_schedule_prioritizes_ready_plot_over_future_crop(self):
        now = int(time.time())
        data = {
            "success": True,
            "seeds": [
                {"id": 1, "name": "萝卜", "grow_time": 14400},
                {"id": 5, "name": "蘑菇", "grow_time": 604800},
            ],
            "user_lands": [
                {"land_id": 1, "plot_index": 7, "seed_id": 1, "harvest_time": now - 10, "is_ready": 0},
                {"land_id": 1, "plot_index": 0, "seed_id": 5, "harvest_time": now + 432000, "is_ready": 0},
            ],
        }

        future_run = self.plugin._compute_next_run(data)
        schedule_run = self.plugin._normalize_refresh_schedule_run(data, future_run)

        self.assertEqual(now, schedule_run)

    def test_run_now_planting_uses_new_crop_time_instead_of_old_future_crop(self):
        now = int(time.time())
        radish = {"id": 1, "name": "萝卜", "cost": 200, "grow_time": 14400, "base_reward": 220, "unlocked": 1}
        mushroom = {"id": 5, "name": "蘑菇", "cost": 8400, "grow_time": 604800, "base_reward": 10080, "unlocked": 1}
        old_data = {
            "success": True,
            "user_bonus": 100000,
            "user_stats": {"total_harvest": 6000000, "unlocked_land_count": 1},
            "seeds": [radish, mushroom],
            "lands": [{"id": 1, "name": "新手农场", "plot_count": 2, "unlock_harvest": 0}],
            "plot_slot": {"effective_plot_counts": {"1": 2}},
            "user_lands": [
                {"land_id": 1, "plot_index": 0, "seed_id": 5, "harvest_time": now + 432000, "is_ready": 0},
            ],
            "inventory": [],
            "user_logs": [],
        }
        new_data = {
            **old_data,
            "user_lands": [
                *old_data["user_lands"],
                {"land_id": 1, "plot_index": 1, "seed_id": 1, "plant_time": now, "harvest_time": now + 14400, "is_ready": 0},
            ],
        }
        fetch_results = [old_data, old_data, new_data]
        fetch_calls = []
        schedule_calls = []

        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()

        def fetch_state(session):
            fetch_calls.append(1)
            return fetch_results[min(len(fetch_calls) - 1, len(fetch_results) - 1)]

        self.plugin._fetch_state = fetch_state
        self.plugin._pick_seed = lambda data: radish
        self.plugin._post_action = lambda session, action, payload=None, retry_network=False: {
            "success": True,
            "planted": 1,
            "total_cost": 200,
        }
        self.plugin._schedule_next_run = lambda next_run, reason="", force_run=False: schedule_calls.append(next_run)
        self.plugin._parse_logs = lambda *args, **kwargs: {}
        self.plugin._build_result_lines = lambda *args, **kwargs: []
        self.plugin._build_state_record = lambda *args, **kwargs: {}
        self.plugin._build_ui_state = lambda *args, **kwargs: {}
        self.plugin._build_status = lambda *args, **kwargs: {}
        self.plugin._append_history = lambda *args, **kwargs: None

        result = self.plugin.run_job(force=True, reason="manual-api")

        self.assertTrue(result["success"])
        self.assertGreaterEqual(len(fetch_calls), 3)
        self.assertEqual(now + 14400, schedule_calls[-1])

    def test_save_config_runs_full_job_after_refresh_when_ready(self):
        run_calls = []
        self.plugin._enabled = True
        self.plugin.init_plugin = lambda config: setattr(self.plugin, "_enabled", True)
        self.plugin._update_config = lambda: None
        self.plugin._reregister_plugin = lambda reason="": None
        self.plugin._refresh_state = lambda reason, record_run=False: {"highlights": {"ready_count": 1}}
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "status": {"ran": True},
        }

        result = self.plugin._save_config({"enabled": True})

        self.assertEqual([(True, "save-config")], run_calls)
        self.assertEqual("配置已保存，已执行补跑", result["message"])
        self.assertEqual({"ran": True}, result["status"])

    def test_manual_refresh_runs_full_job_after_refresh_when_ready(self):
        run_calls = []
        self.plugin._refresh_state = lambda reason, record_run=False: {"highlights": {"ready_count": 1}}
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "补跑完成",
            "status": {"ran": True},
        }

        result = self.plugin._refresh_data()

        self.assertEqual([(True, "manual-refresh")], run_calls)
        self.assertEqual("农场数据已刷新，已执行补跑", result["message"])
        self.assertEqual({"ran": True}, result["status"])

    def test_status_refresh_with_ready_string_registers_immediate_run(self):
        data = _ready_farm_data(18)
        for plot in data["user_lands"]:
            plot["is_ready"] = "1"
            plot["plant_time"] = None
            plot["harvest_time"] = None

        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_state = lambda session: data
        self.plugin._reregister_plugin = lambda reason="": None

        before_ts = int(time.time())
        farm_status = self.plugin._refresh_state(reason="status-init", record_run=False)

        self.assertEqual(18, farm_status["highlights"]["ready_count"])
        self.assertEqual("run", self.plugin.get_data("next_trigger_mode"))
        next_trigger = self.plugin._parse_datetime(self.plugin.get_data("next_trigger_time"))
        self.assertIsNotNone(next_trigger)
        self.assertLessEqual(int(next_trigger.timestamp()), before_ts + self.plugin.MIN_TRIGGER_SECONDS + 2)

    def test_refresh_only_when_not_ready_or_overdue(self):
        run_calls = []
        future_ts = int(time.time()) + 3600
        self.plugin._refresh_state = lambda reason, record_run=False: {
            "highlights": {"ready_count": 0},
            "next_run_ts": future_ts,
            "next_trigger_ts": future_ts,
        }
        self.plugin.run_job = lambda force=False, reason="manual": run_calls.append((force, reason)) or {
            "success": True,
            "message": "不应执行",
        }

        result = self.plugin._refresh_worker()

        self.assertEqual([], run_calls)
        self.assertEqual("农场状态已预刷新", result["message"])

    def test_social_worker_stops_same_window_only_after_quota_is_exhausted(self):
        self.plugin._auto_steal = True
        self.plugin._auto_like = False
        self.plugin._active_steal_window = lambda now=None: "2026-07-16|07:00-09:00"
        calls = []
        self.plugin._run_steal_cycle = lambda force=False, payload=None: calls.append("steal") or {
            "success": True,
            "message": "今日次数已用完",
            "exhausted": True,
        }

        self.plugin._social_worker()
        self.plugin._social_worker()

        self.assertEqual(["steal"], calls)
        self.assertEqual("2026-07-16|07:00-09:00", self.plugin.get_data("auto_steal_window_key"))
        self.assertEqual(self.plugin._today_key(), self.plugin.get_data("auto_steal_done_date"))

    def test_social_worker_retries_same_window_after_no_target(self):
        self.plugin._auto_steal = True
        self.plugin._auto_like = False
        self.plugin._active_steal_window = lambda now=None: "2026-07-16|00:00-23:59"
        results = iter([
            {"success": True, "message": "没有找到目标作物", "stolen": 0, "exhausted": False},
            {"success": True, "message": "偷到 1 份", "stolen": 1, "remaining": 0, "exhausted": True},
        ])
        calls = []
        self.plugin._run_steal_cycle = lambda force=False, payload=None: calls.append("steal") or next(results)

        self.plugin._social_worker()
        self.plugin._social_worker()

        self.assertEqual(["steal", "steal"], calls)
        self.assertEqual(self.plugin._today_key(), self.plugin.get_data("auto_steal_done_date"))

    def test_social_worker_ignores_legacy_no_target_window_marker(self):
        self.plugin._auto_steal = True
        self.plugin._auto_like = False
        window_key = "2026-07-16|00:00-23:59"
        self.plugin._active_steal_window = lambda now=None: window_key
        self.plugin.save_data("auto_steal_window_key", window_key)
        calls = []
        self.plugin._run_steal_cycle = lambda force=False, payload=None: calls.append("steal") or {
            "success": True,
            "message": "没有找到目标作物",
            "stolen": 0,
            "exhausted": False,
        }

        self.plugin._social_worker()

        self.assertEqual(["steal"], calls)

    def test_social_worker_stops_later_windows_after_daily_steal_is_exhausted(self):
        self.plugin._auto_steal = True
        self.plugin._auto_like = False
        self.plugin._active_steal_window = lambda now=None: "2026-07-16|07:00-09:00"
        calls = []
        self.plugin._run_steal_cycle = lambda force=False, payload=None: calls.append("steal") or {
            "success": True,
            "message": "今日次数已用完",
            "exhausted": True,
        }

        self.plugin._social_worker()
        self.plugin._active_steal_window = lambda now=None: "2026-07-16|12:00-14:00"
        self.plugin._social_worker()

        self.assertEqual(["steal"], calls)
        self.assertEqual(self.plugin._today_key(), self.plugin.get_data("auto_steal_done_date"))

    def test_social_worker_retries_same_window_when_quota_remains_after_steal(self):
        self.plugin._auto_steal = True
        self.plugin._auto_like = False
        self.plugin._active_steal_window = lambda now=None: "2026-07-16|07:00-09:00"
        results = iter([
            {"success": True, "message": "偷到 1 份", "stolen": 1, "remaining": 2, "exhausted": False},
            {"success": True, "message": "偷到 2 份", "stolen": 2, "remaining": 0, "exhausted": True},
        ])
        calls = []
        self.plugin._run_steal_cycle = lambda force=False, payload=None: calls.append("steal") or next(results)

        self.plugin._social_worker()
        self.plugin._social_worker()

        self.assertEqual(["steal", "steal"], calls)
        self.assertEqual(self.plugin._today_key(), self.plugin.get_data("auto_steal_done_date"))

    def test_steal_cycle_visits_requested_number_of_unique_victims(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        victims = iter([
            {"success": True, "victim_id": "a", "victim_name": "甲", "max_steal_count": 5, "steal_count_today": 0},
            {"success": True, "victim_id": "a", "victim_name": "甲", "max_steal_count": 5, "steal_count_today": 0},
            {"success": True, "victim_id": "b", "victim_name": "乙", "max_steal_count": 5, "steal_count_today": 0},
            {"success": True, "victim_id": "c", "victim_name": "丙", "max_steal_count": 5, "steal_count_today": 0},
        ])
        self.plugin._post_action = lambda session, action, payload=None, retry_network=False: next(victims)
        self.plugin._victim_stealable_plots = lambda victim, requested_crop: []

        result = self.plugin._run_steal_cycle(force=True, payload={"visit_count": 3})

        self.assertTrue(result["success"])
        self.assertEqual(3, result["visited"])

    def test_victim_crop_filter_only_returns_requested_crop(self):
        now = int(time.time())
        victim = {
            "seeds": [
                {"id": 4, "name": "茄子"},
                {"id": 5, "name": "蘑菇"},
            ],
            "victim_lands": [{"id": 1, "unlocked": 1}],
            "victim_plots": [
                {"land_id": 1, "plot_index": 0, "seed_id": 4, "harvest_time": now - 1},
                {"land_id": 1, "plot_index": 1, "seed_id": 5, "harvest_time": now - 1},
            ],
        }

        plots = self.plugin._victim_stealable_plots(victim, "蘑菇")

        self.assertEqual([(1, 1, "蘑菇")], plots)

    def test_victim_crop_filter_accepts_multiple_requested_crops(self):
        now = int(time.time())
        victim = {
            "seeds": [
                {"id": 2, "name": "西红柿"},
                {"id": 4, "name": "茄子"},
                {"id": 5, "name": "蘑菇"},
            ],
            "victim_lands": [{"id": 1, "unlocked": 1}],
            "victim_plots": [
                {"land_id": 1, "plot_index": 0, "seed_id": 2, "harvest_time": now - 1},
                {"land_id": 1, "plot_index": 1, "seed_id": 4, "harvest_time": now - 1},
                {"land_id": 1, "plot_index": 2, "seed_id": 5, "harvest_time": now - 1},
            ],
        }

        plots = self.plugin._victim_stealable_plots(victim, ["茄子", "蘑菇"])

        self.assertEqual([(1, 1, "茄子"), (1, 2, "蘑菇")], plots)

    def test_steal_cycle_uses_remaining_daily_quota_across_multiple_victims(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        now = int(time.time())
        victims = iter([
            {
                "success": True,
                "victim_id": "a",
                "victim_name": "甲",
                "max_steal_count": 4,
                "steal_count_today": 0,
                "seeds": [
                    {"id": 2, "name": "西红柿"},
                    {"id": 4, "name": "茄子"},
                    {"id": 5, "name": "蘑菇"},
                ],
                "victim_lands": [{"id": 1, "unlocked": 1}],
                "victim_plots": [
                    {"land_id": 1, "plot_index": 0, "seed_id": 5, "harvest_time": now - 1},
                    {"land_id": 1, "plot_index": 1, "seed_id": 4, "harvest_time": now - 1},
                    {"land_id": 1, "plot_index": 2, "seed_id": 5, "harvest_time": now - 1},
                    {"land_id": 1, "plot_index": 3, "seed_id": 2, "harvest_time": now - 1},
                ],
            },
            {
                "success": True,
                "victim_id": "b",
                "victim_name": "乙",
                "max_steal_count": 4,
                "steal_count_today": 3,
                "seeds": [{"id": 4, "name": "茄子"}],
                "victim_lands": [{"id": 2, "unlocked": 1}],
                "victim_plots": [
                    {"land_id": 2, "plot_index": 0, "seed_id": 4, "harvest_time": now - 1},
                ],
            },
        ])
        calls = []

        def post_action(session, action, payload=None, retry_network=False):
            calls.append((action, payload or {}))
            if action == "get_victim_farm":
                return next(victims)
            if action == "steal_vegetable":
                return {"success": True, "reward": 10}
            if action == "finish_stealing":
                return {"success": True}
            self.fail(f"未预期动作：{action}")

        self.plugin._post_action = post_action

        result = self.plugin._run_steal_cycle(
            force=True,
            payload={"crops": ["茄子", "蘑菇"], "visit_count": 5},
        )

        steal_calls = [payload for action, payload in calls if action == "steal_vegetable"]
        self.assertEqual(4, len(steal_calls))
        self.assertEqual(2, len([1 for action, _ in calls if action == "finish_stealing"]))
        self.assertEqual(4, result["stolen"])
        self.assertEqual(0, result["remaining"])
        self.assertTrue(result["exhausted"])

    def test_steal_notification_lists_only_crops_actually_stolen(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        now = int(time.time())
        victim = {
            "success": True,
            "victim_id": "corn-user",
            "victim_name": "玉米用户",
            "max_steal_count": 3,
            "steal_count_today": 0,
            "seeds": [
                {"id": 3, "name": "玉米"},
                {"id": 4, "name": "茄子"},
                {"id": 5, "name": "蘑菇"},
                {"id": 6, "name": "樱桃"},
                {"id": 2, "name": "西红柿"},
            ],
            "victim_lands": [{"id": 1, "unlocked": 1}],
            "victim_plots": [
                {"land_id": 1, "plot_index": 0, "seed_id": 3, "harvest_time": now - 1},
                {"land_id": 1, "plot_index": 1, "seed_id": 3, "harvest_time": now - 1},
                {"land_id": 1, "plot_index": 2, "seed_id": 3, "harvest_time": now - 1},
            ],
        }
        actions = []

        def post_action(session, action, payload=None, retry_network=False):
            actions.append(action)
            if action == "get_victim_farm":
                return victim if actions.count("get_victim_farm") == 1 else {
                    "success": False,
                    "message": "没有可访问农场",
                }
            if action == "steal_vegetable":
                return {"success": True, "reward": 345}
            if action == "finish_stealing":
                return {"success": True}
            self.fail(f"未预期动作：{action}")

        self.plugin._post_action = post_action

        result = self.plugin._run_steal_cycle(
            force=True,
            payload={"crops": ["玉米", "茄子", "蘑菇", "樱桃", "西红柿"], "visit_count": 9},
        )

        self.assertIn("🌽玉米×3", result["message"])
        self.assertNotIn("茄子、蘑菇、樱桃、西红柿", result["message"])

    def test_old_single_crop_config_is_normalized_to_multi_select_list(self):
        config = self.plugin._default_config()
        config["steal_crop"] = "蘑菇"

        self.plugin._apply_config(config)

        self.assertEqual(["蘑菇"], self.plugin._steal_crop)
        self.assertEqual(["蘑菇"], self.plugin._get_config()["steal_crop"])

    def test_json_encoded_multi_crop_config_is_normalized_without_brackets_or_quotes(self):
        config = self.plugin._default_config()
        config["steal_crop"] = '["萝卜", "玉米", "蘑菇"]'

        self.plugin._apply_config(config)

        self.assertEqual(["萝卜", "玉米", "蘑菇"], self.plugin._steal_crop)
        self.assertEqual(["萝卜", "玉米", "蘑菇"], self.plugin._get_config()["steal_crop"])

    def test_like_targets_config_normalizes_blank_duplicate_and_extra_names(self):
        config = self.plugin._default_config()
        config["like_targets"] = [" 用户甲 ", "", "用户甲", "用户乙", "用户丙", "用户丁"]
        config["like_cron"] = "5 */4 * * *"

        self.plugin._apply_config(config)

        self.assertEqual(["用户甲", "用户乙", "用户丙"], self.plugin._like_targets)
        self.assertEqual("5 */4 * * *", self.plugin._like_cron)
        self.assertEqual(["用户甲", "用户乙", "用户丙"], self.plugin._get_config()["like_targets"])
        self.assertEqual("5 */4 * * *", self.plugin._get_config()["like_cron"])

    def test_old_like_time_config_is_migrated_to_cron(self):
        config = self.plugin._default_config()
        config["like_time"] = "9:5"

        self.plugin._apply_config(config)

        self.assertEqual("5 9 * * *", self.plugin._like_cron)

    def test_one_time_worker_also_runs_enabled_social_tasks(self):
        main_calls = []
        social_calls = []
        self.plugin._enabled = True
        self.plugin._auto_steal = True
        self.plugin._auto_like = True
        self.plugin.run_job = lambda force=False, reason="manual": main_calls.append((force, reason)) or {
            "success": True,
            "message": "农场主任务完成",
        }
        self.plugin._social_worker = lambda force=False: social_calls.append(force) or {
            "success": True,
            "message": "偷菜和点赞完成",
        }

        result = self.plugin._manual_worker()

        self.assertEqual([(True, "onlyonce")], main_calls)
        self.assertEqual([True], social_calls)
        self.assertEqual("偷菜和点赞完成", result["social"]["message"])

    def test_social_worker_does_not_auto_like_before_daily_time(self):
        self.plugin._auto_steal = False
        self.plugin._auto_like = True
        self.plugin._like_cron = "30 10 * * *"
        timezone = self.module.pytz.timezone("Asia/Shanghai")
        self.plugin._aware_now = lambda: timezone.localize(datetime(2026, 7, 17, 10, 0))
        calls = []
        self.plugin._run_like_cycle = lambda force=False, payload=None: calls.append(force) or {"success": True}

        self.plugin._social_worker(force=False)

        self.assertEqual([], calls)

    def test_social_worker_catches_up_auto_like_after_daily_time(self):
        self.plugin._auto_steal = False
        self.plugin._auto_like = True
        self.plugin._like_cron = "30 10 * * *"
        timezone = self.module.pytz.timezone("Asia/Shanghai")
        self.plugin._aware_now = lambda: timezone.localize(datetime(2026, 7, 17, 11, 0))
        calls = []
        self.plugin._run_like_cycle = lambda force=False, payload=None: calls.append(force) or {"success": True}

        self.plugin._social_worker(force=False)

        self.assertEqual([False], calls)

    def test_cookie_auto_sync_cannot_be_disabled_by_legacy_config(self):
        config = self.plugin._default_config()
        config["auto_cookie"] = False

        self.plugin._apply_config(config)

        self.assertTrue(self.plugin._auto_cookie)
        self.assertNotIn("auto_cookie", self.plugin._get_config())

    def test_ensure_cookie_always_attempts_site_sync_before_manual_fallback(self):
        calls = []
        self.plugin._auto_cookie = False
        self.plugin._cookie = "manual-cookie"
        self.plugin._sync_cookie_from_site = lambda save_config=False, silent=True: calls.append(
            (save_config, silent)
        ) or {"success": False, "message": "站点暂时不可用"}

        self.plugin._ensure_cookie()

        self.assertEqual([(False, True)], calls)
        self.assertIn("备用", self.plugin._cookie_source)

    def test_auto_like_marks_today_checked_when_no_targets_exist(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._post_action = lambda session, action, payload=None, retry_network=False: {
            "success": True,
            "usernames": [],
        }

        result = self.plugin._run_like_cycle(force=False)

        self.assertTrue(result["success"])
        self.assertEqual(self.plugin._today_key(), self.plugin.get_data("auto_like_date"))

    def test_auto_like_fills_missing_fixed_slots_with_unique_random_targets(self):
        self.plugin._like_targets = ["固定甲"]
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        calls = []

        def post_action(session, action, payload=None, retry_network=False):
            calls.append((action, payload))
            if action == "random_like_targets":
                return {"success": True, "usernames": ["固定甲", "随机乙", "随机乙", "随机丙", "随机丁"]}
            if action == "like_farm_batch":
                return {"success": True, "message": "点赞完成"}
            self.fail(f"未预期动作：{action}")

        self.plugin._post_action = post_action

        result = self.plugin._run_like_cycle(force=False)

        self.assertTrue(result["success"])
        self.assertIn(("like_farm_batch", {"usernames": "固定甲\n随机乙\n随机丙"}), calls)

    def test_auto_like_with_three_fixed_targets_skips_random_target_request(self):
        self.plugin._like_targets = ["固定甲", "固定乙", "固定丙"]
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        actions = []

        def post_action(session, action, payload=None, retry_network=False):
            actions.append(action)
            return {"success": True, "message": "点赞完成"}

        self.plugin._post_action = post_action

        result = self.plugin._run_like_cycle(force=False)

        self.assertTrue(result["success"])
        self.assertNotIn("random_like_targets", actions)

    def test_active_steal_window_supports_cross_midnight_ranges(self):
        self.plugin._steal_time_windows = "22:00-01:00,07:00-09:00"
        current = datetime(2026, 7, 16, 0, 30)

        window_key = self.plugin._active_steal_window(current)

        self.assertEqual("2026-07-15|22:00-01:00", window_key)

    def test_manual_social_endpoints_use_reference_farm_actions(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        calls = []

        def post_action(session, action, payload=None, retry_network=False):
            calls.append((action, payload or {}))
            if action == "get_victim_farm":
                return {"success": True, "victim_id": 88, "victim_name": "测试用户"}
            if action == "random_like_targets":
                return {"success": True, "usernames": ["甲", "乙"]}
            return {"success": True, "reward": 12, "message": "操作成功"}

        self.plugin._post_action = post_action
        self.plugin._refresh_state = lambda reason, record_run=False: {"last_updated": "now"}

        target = self.plugin._steal_target_api()
        stolen = self.plugin._steal_plot_api({"victim_id": 88, "land_id": 1, "plot_index": 2})
        finished = self.plugin._finish_stealing_api({"stolen_count": 1, "reward": 12})
        like_targets = self.plugin._like_targets_api()
        liked = self.plugin._like_batch_api({"usernames": ["甲", "乙"]})

        self.assertTrue(target["success"])
        self.assertTrue(stolen["success"])
        self.assertTrue(finished["success"])
        self.assertEqual(["甲", "乙"], like_targets["usernames"])
        self.assertTrue(liked["success"])
        self.assertIn(("steal_vegetable", {"victim_id": 88, "land_id": 1, "plot_index": 2}), calls)
        self.assertIn(("finish_stealing", {}), calls)
        self.assertIn(("like_farm_batch", {"usernames": "甲\n乙"}), calls)

    def test_sell_all_inventory_uses_one_backend_flow(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        data = {
            "success": True,
            "inventory": [
                {"seed_id": 1, "name": "萝卜", "quantity": 2, "unit_reward": 220},
                {"seed_id": 2, "name": "西红柿", "quantity": 3, "unit_reward": 450},
            ],
            "seeds": [],
            "lands": [],
            "user_lands": [],
            "user_logs": [],
        }
        empty = {**data, "inventory": []}
        self.plugin._fetch_state = lambda session: data
        calls = []

        def post_action(session, action, payload=None, retry_network=False):
            calls.append((action, payload))
            return {"success": True, "gain": int(payload["quantity"]) * (220 if payload["seed_id"] == 1 else 450)}

        self.plugin._post_action = post_action
        self.plugin._refetch_state_until = lambda *args, **kwargs: empty
        self.plugin._refresh_and_store_farm_state = lambda latest, reason, lines=None: {"inventory": {"items": []}}

        result = self.plugin._sell_all_inventory_api()

        self.assertTrue(result["success"])
        self.assertEqual(2, result["sold_types"])
        self.assertEqual(1790, result["gain"])
        self.assertEqual([
            ("sell_inventory", {"seed_id": 1, "quantity": 2}),
            ("sell_inventory", {"seed_id": 2, "quantity": 3}),
        ], calls)

    def test_reference_page_data_includes_raw_farm_and_dynamic_schedule(self):
        data = _ready_farm_data(2)
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._fetch_state = lambda session: data
        self.plugin._schedule_next_run = lambda next_run, reason="": None
        self.plugin._compute_next_run = lambda latest: int(time.time()) + 3600

        result = self.plugin._get_page_data()

        self.assertTrue(result["success"])
        self.assertEqual(data["seeds"], result["seeds"])
        self.assertEqual(data["user_lands"], result["user_lands"])
        self.assertTrue(result["dynamic_schedule"])
        self.assertEqual(2, result["summary"]["ready"])
        self.assertIn("next_run_time", result)
        self.assertIn("config", result)

    def test_reference_plot_endpoints_translate_zero_based_plot_index(self):
        plant_payloads = []
        harvest_payloads = []
        self.plugin._plant_plot_api = lambda payload=None: plant_payloads.append(payload) or {"success": True}
        self.plugin._harvest_plot_api = lambda payload=None: harvest_payloads.append(payload) or {"success": True}

        self.plugin._reference_plant_api({"land_id": 2, "plot_index": 0, "seed_id": 5})
        self.plugin._reference_harvest_api({"land_id": 2, "plot_index": 3})

        self.assertEqual({"land_id": 2, "slot_index": 1, "seed_id": 5}, plant_payloads[0])
        self.assertEqual({"land_id": 2, "slot_index": 4}, harvest_payloads[0])

    def test_reference_stage_image_returns_data_url_from_same_site(self):
        class FakeResponse:
            status_code = 200
            content = b"fake-png"
            headers = {"content-type": "image/png"}

            def raise_for_status(self):
                return None

        class FakeSession:
            def __init__(self):
                self.requested_url = ""

            def get(self, url, **kwargs):
                self.requested_url = url
                return FakeResponse()

        session = FakeSession()
        self.plugin._site_url = "https://si-qi.xyz"
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: session

        result = self.plugin._stage_image_api("images/farm/tomato.png")

        self.assertTrue(result["success"])
        self.assertEqual("https://si-qi.xyz/images/farm/tomato.png", session.requested_url)
        self.assertTrue(result["data"].startswith("data:image/png;base64,"))

    def test_reference_stage_image_rejects_external_url(self):
        result = self.plugin._stage_image_api("https://example.com/not-allowed.png")

        self.assertFalse(result["success"])
        self.assertIn("无效", result["message"])

    def test_reference_interaction_endpoints_keep_original_action_payloads(self):
        self.plugin._ensure_cookie = lambda: None
        self.plugin._build_session = lambda: object()
        self.plugin._refresh_state = lambda reason, record_run=False: {}
        calls = []

        def post_action(session, action, payload=None, retry_network=False):
            calls.append((action, payload or {}, retry_network))
            return {"success": True}

        self.plugin._post_action = post_action

        self.assertTrue(self.plugin._buy_plot_slot_api({"land_id": 3})["success"])
        self.assertTrue(self.plugin._like_farm_api({"target_id": 88})["success"])
        self.assertTrue(self.plugin._visit_farm_api({"username": "测试用户"})["success"])
        self.assertTrue(self.plugin._visit_random_farm_api()["success"])

        self.assertIn(("buy_plot_slot", {"land_id": 3}, False), calls)
        self.assertIn(("like_farm", {"target_id": 88}, False), calls)
        self.assertIn(("view_farm_by_username", {"username": "测试用户"}, True), calls)
        self.assertIn(("view_random_farm", {}, True), calls)

        route_paths = {route["path"] for route in self.plugin.get_api()}
        self.assertTrue({
            "/data",
            "/plant",
            "/plant-fill",
            "/harvest",
            "/harvest-ocr",
            "/sell",
            "/buy-plot-slot",
            "/like-random",
            "/like-farm",
            "/visit-farm",
            "/visit-random",
            "/stage-image",
        }.issubset(route_paths))


if __name__ == "__main__":
    unittest.main()
