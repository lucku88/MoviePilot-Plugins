import sys
import time
import types
import unittest

from tests.test_vue_autocatchup import _load_plugin


class VueStartupRecoveryTests(unittest.TestCase):
    PLUGIN_CLASSES = {
        "vuefarm": "VueFarm",
        "vuepill": "VuePill",
        "vuetoy": "VueToy",
        "vueemoji": "VueEmoji",
    }

    def assert_resilient_date_service(self, service):
        self.assertEqual("date", service["trigger"])
        self.assertIsNone(service["kwargs"]["misfire_grace_time"])
        self.assertTrue(service["kwargs"]["coalesce"])
        self.assertEqual(1, service["kwargs"]["max_instances"])

    @staticmethod
    def _service(services, service_id):
        return next(service for service in services if service["id"] == service_id)

    def test_vuefarm_dynamic_job_survives_delayed_scheduler_start(self):
        module = _load_plugin("vuefarm")
        plugin = module.VueFarm()
        plugin._enabled = True
        plugin._bootstrap_pending = True
        plugin._auto_steal = True
        plugin._auto_like = False
        plugin._social_cron = "*/15 * * * *"

        services = plugin.get_service()

        self.assert_resilient_date_service(self._service(services, "VueFarm_auto"))
        social = self._service(services, "VueFarm_social")
        self.assertNotEqual("date", social["trigger"])
        self.assertNotIn("misfire_grace_time", social.get("kwargs", {}))

    def test_vuepill_dynamic_job_survives_delayed_scheduler_start(self):
        module = _load_plugin("vuepill")
        plugin = module.VuePill()
        plugin._enabled = True
        plugin._bootstrap_pending = True

        service = self._service(plugin.get_service(), "VuePill_auto")

        self.assert_resilient_date_service(service)

    def test_vuetoy_dynamic_job_survives_delayed_scheduler_start(self):
        module = _load_plugin("vuetoy")
        plugin = module.VueToy()
        plugin._enabled = True
        plugin._bootstrap_pending = True

        service = self._service(plugin.get_service(), "VueToy_auto")

        self.assert_resilient_date_service(service)

    def test_vueemoji_dynamic_jobs_survive_delayed_scheduler_start(self):
        module = _load_plugin("vueemoji")
        plugin = module.VueEmoji()
        plugin._enabled = True
        plugin._auto_stage = True
        plugin._auto_spin = False
        plugin._auto_open_bags = False
        plugin._bootstrap_pending = True
        plugin._auto_recruit = True
        plugin._recruit_next_check_ts = int(time.time()) + 3600

        services = plugin.get_service()

        self.assert_resilient_date_service(self._service(services, "VueEmoji_auto"))
        self.assert_resilient_date_service(self._service(services, "VueEmoji_recruit"))

    def test_stop_service_does_not_construct_moviepilot_scheduler_during_startup(self):
        for plugin_key, class_name in self.PLUGIN_CLASSES.items():
            with self.subTest(plugin=plugin_key):
                module = _load_plugin(plugin_key)
                plugin = getattr(module, class_name)()

                class SchedulerProbe:
                    constructed = 0

                    @classmethod
                    def get_existing_instance(cls):
                        return None

                    def __new__(cls):
                        cls.constructed += 1
                        raise AssertionError("MoviePilot scheduler must not be created here")

                module.Scheduler = SchedulerProbe
                stop = plugin._stop_service_locked if plugin_key == "vuepill" else plugin.stop_service

                stop()

                self.assertEqual(0, SchedulerProbe.constructed)

    def test_stop_service_leaves_existing_moviepilot_jobs_for_host_reload(self):
        for plugin_key, class_name in self.PLUGIN_CLASSES.items():
            with self.subTest(plugin=plugin_key):
                module = _load_plugin(plugin_key)
                plugin_class = getattr(module, class_name)
                plugin = plugin_class()

                class ExistingScheduler:
                    def __init__(self):
                        self.removed = []

                    def remove_plugin_job(self, plugin_id):
                        self.removed.append(plugin_id)

                existing = ExistingScheduler()

                class SchedulerProbe:
                    @classmethod
                    def get_existing_instance(cls):
                        return existing

                    def __new__(cls):
                        raise AssertionError("Existing MoviePilot scheduler should be reused")

                module.Scheduler = SchedulerProbe
                stop = plugin._stop_service_locked if plugin_key == "vuepill" else plugin.stop_service

                stop()

                self.assertEqual([], existing.removed)

    def test_stop_service_does_not_remove_jobs_from_moviepilot_singleton_registry(self):
        for plugin_key, class_name in self.PLUGIN_CLASSES.items():
            with self.subTest(plugin=plugin_key):
                module = _load_plugin(plugin_key)
                plugin_class = getattr(module, class_name)
                plugin = plugin_class()

                class ExistingScheduler:
                    def __init__(self):
                        self.removed = []

                    def remove_plugin_job(self, plugin_id):
                        self.removed.append(plugin_id)

                class SchedulerSingletonProbe(type):
                    _instances = {}

                class SchedulerProbe(metaclass=SchedulerSingletonProbe):
                    def __new__(cls):
                        raise AssertionError("Singleton registry should be read without construction")

                existing = ExistingScheduler()
                SchedulerSingletonProbe._instances[SchedulerProbe] = existing
                module.Scheduler = SchedulerProbe
                stop = plugin._stop_service_locked if plugin_key == "vuepill" else plugin.stop_service

                stop()

                self.assertEqual([], existing.removed)

    def test_stop_service_never_constructs_scheduler_without_existing_instance(self):
        for plugin_key, class_name in self.PLUGIN_CLASSES.items():
            with self.subTest(plugin=plugin_key):
                module = _load_plugin(plugin_key)
                plugin = getattr(module, class_name)()

                class SchedulerProbe:
                    constructed = 0

                    def __new__(cls):
                        cls.constructed += 1
                        raise AssertionError("MoviePilot scheduler must not be created during cleanup")

                module.Scheduler = SchedulerProbe
                stop = plugin._stop_service_locked if plugin_key == "vuepill" else plugin.stop_service

                stop()

                self.assertEqual(0, SchedulerProbe.constructed)

    def test_plugins_delayed_registration_repairs_host_scheduler(self):
        for plugin_key, class_name in self.PLUGIN_CLASSES.items():
            with self.subTest(plugin=plugin_key):
                module = _load_plugin(plugin_key)
                plugin = getattr(module, class_name)()
                plugin._enabled = True
                plugin.get_service = lambda: [{"id": "startup_probe"}]

                self.assertTrue(
                    hasattr(plugin, "_schedule_startup_registration"),
                    f"{class_name} must schedule a delayed host registration check",
                )

                timers = []

                class TimerProbe:
                    def __init__(self, interval, function, args=None, kwargs=None):
                        self.interval = interval
                        self.function = function
                        self.args = tuple(args or ())
                        self.kwargs = dict(kwargs or {})
                        self.daemon = False
                        self.started = False
                        self.cancelled = False
                        timers.append(self)

                    def start(self):
                        self.started = True

                    def cancel(self):
                        self.cancelled = True

                    def fire(self):
                        if not self.cancelled:
                            self.function(*self.args, **self.kwargs)

                host_scheduler = types.SimpleNamespace(
                    _scheduler=types.SimpleNamespace(running=True),
                    _jobs={},
                    updated=[],
                )

                def update_plugin_job(plugin_id):
                    host_scheduler.updated.append(plugin_id)
                    host_scheduler._jobs[f"{plugin_id}_startup_probe"] = {}

                host_scheduler.update_plugin_job = update_plugin_job

                class SchedulerProbe:
                    constructed = 0

                    def __new__(cls):
                        cls.constructed += 1
                        return host_scheduler

                plugin_manager_module = types.ModuleType("app.core.plugin")

                class PluginManager:
                    running_plugins = {class_name: plugin}

                plugin_manager_module.PluginManager = PluginManager
                previous_plugin_manager = sys.modules.get("app.core.plugin")
                sys.modules["app.core.plugin"] = plugin_manager_module
                original_scheduler = module.Scheduler
                original_timer = module.threading.Timer
                module.Scheduler = SchedulerProbe
                module.threading.Timer = TimerProbe
                try:
                    plugin._schedule_startup_registration()

                    self.assertEqual(1, len(timers))
                    self.assertTrue(timers[0].started)
                    self.assertGreaterEqual(timers[0].interval, 5)
                    self.assertEqual(0, SchedulerProbe.constructed)

                    timers[0].fire()

                    self.assertEqual(1, SchedulerProbe.constructed)
                    self.assertEqual([class_name], host_scheduler.updated)
                finally:
                    module.Scheduler = original_scheduler
                    module.threading.Timer = original_timer
                    if previous_plugin_manager is None:
                        sys.modules.pop("app.core.plugin", None)
                    else:
                        sys.modules["app.core.plugin"] = previous_plugin_manager

    def test_stop_service_cancels_pending_startup_registration(self):
        for plugin_key, class_name in self.PLUGIN_CLASSES.items():
            with self.subTest(plugin=plugin_key):
                module = _load_plugin(plugin_key)
                plugin = getattr(module, class_name)()
                plugin._enabled = True
                plugin.get_service = lambda: [{"id": "startup_probe"}]

                self.assertTrue(
                    hasattr(plugin, "_schedule_startup_registration"),
                    f"{class_name} must expose delayed startup registration",
                )

                timers = []

                class TimerProbe:
                    def __init__(self, interval, function, args=None, kwargs=None):
                        self.cancelled = False
                        self.daemon = False
                        timers.append(self)

                    def start(self):
                        return None

                    def cancel(self):
                        self.cancelled = True

                original_timer = module.threading.Timer
                module.threading.Timer = TimerProbe
                try:
                    plugin._schedule_startup_registration()
                    stop = plugin._stop_service_locked if plugin_key == "vuepill" else plugin.stop_service
                    stop()

                    self.assertEqual(1, len(timers))
                    self.assertTrue(timers[0].cancelled)
                finally:
                    module.threading.Timer = original_timer


if __name__ == "__main__":
    unittest.main()
