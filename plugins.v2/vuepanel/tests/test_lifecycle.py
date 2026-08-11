import unittest

from test_entertainment_parsing import load_vuepanel_class


class VuePanelLifecycleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.VuePanel = load_vuepanel_class()
        cls.module_globals = cls.VuePanel.stop_service.__globals__

    def setUp(self):
        self.original_scheduler = self.module_globals["Scheduler"]

    def tearDown(self):
        self.module_globals["Scheduler"] = self.original_scheduler

    def test_stop_service_does_not_construct_moviepilot_scheduler_during_startup(self):
        class SingletonMeta(type):
            _instances = {}

        class SchedulerProbe(metaclass=SingletonMeta):
            constructed = 0

            def __new__(cls):
                cls.constructed += 1
                raise AssertionError("stop_service must not create the MoviePilot scheduler")

        self.module_globals["Scheduler"] = SchedulerProbe
        plugin = self.VuePanel()
        plugin._scheduler = None

        plugin.stop_service()

        self.assertEqual(0, SchedulerProbe.constructed)

    def test_stop_service_removes_job_from_existing_moviepilot_scheduler(self):
        class ExistingScheduler:
            def __init__(self):
                self.removed = []

            def remove_plugin_job(self, plugin_id):
                self.removed.append(plugin_id)

        existing = ExistingScheduler()

        class SingletonMeta(type):
            _instances = {}

        class SchedulerProbe(metaclass=SingletonMeta):
            def __new__(cls):
                raise AssertionError("the existing scheduler should be reused")

        SingletonMeta._instances[SchedulerProbe] = existing
        self.module_globals["Scheduler"] = SchedulerProbe
        plugin = self.VuePanel()
        plugin._scheduler = None

        plugin.stop_service()

        self.assertEqual([self.VuePanel.__name__], existing.removed)


if __name__ == "__main__":
    unittest.main()
