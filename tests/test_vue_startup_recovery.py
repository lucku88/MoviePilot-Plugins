import time
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

    def test_stop_service_removes_job_from_existing_moviepilot_scheduler(self):
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

                self.assertEqual([plugin_class.__name__], existing.removed)

    def test_stop_service_uses_moviepilot_singleton_registry(self):
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

                self.assertEqual([plugin_class.__name__], existing.removed)

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


if __name__ == "__main__":
    unittest.main()
