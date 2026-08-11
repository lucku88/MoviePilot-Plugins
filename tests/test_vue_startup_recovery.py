import time
import unittest

from tests.test_vue_autocatchup import _load_plugin


class VueStartupRecoveryTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
