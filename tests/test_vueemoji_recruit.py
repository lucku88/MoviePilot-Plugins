import copy
import unittest
from datetime import timedelta
from unittest import mock

from tests.test_vueemoji_backend import _base_state, _load_vueemoji


class VueEmojiRecruitTests(unittest.TestCase):
    def setUp(self):
        self.module = _load_vueemoji()
        self.plugin = self.module.VueEmoji()
        self.plugin._enabled = True
        self.plugin._auto_recruit = True
        self.plugin._cookie = "sid=test"
        self.plugin._http_retry_times = 5
        self.plugin._http_retry_delay = 0
        self.plugin._recruit_tiers = [1, 3]
        self.plugin._recruit_visit_count = 3
        self.plugin._recruit_interval_minutes = 30
        self.plugin._ensure_cookie = mock.Mock()
        self.plugin._build_session = mock.Mock(return_value=object())
        self.plugin._reregister_plugin = mock.Mock()
        self.plugin._append_history = mock.Mock()
        self.plugin.post_message = mock.Mock()

    def test_config_normalizes_recruit_values(self):
        config = self.plugin._default_config()

        self.assertFalse(config["auto_recruit"])
        self.assertEqual([1, 2, 3, 4], config["recruit_tiers"])
        self.assertEqual("07:00-23:00", config["recruit_time_windows"])
        self.assertEqual(30, config["recruit_interval_minutes"])
        self.assertEqual(10, config["recruit_visit_count"])

        self.plugin._apply_config({
            **config,
            "auto_recruit": "true",
            "recruit_tiers": ["4", "2", "2", "99"],
            "recruit_time_windows": "08:00-12:00, 18:00-23:00",
            "recruit_interval_minutes": 2,
            "recruit_visit_count": 999,
        })

        self.assertTrue(self.plugin._auto_recruit)
        self.assertEqual([2, 4], self.plugin._recruit_tiers)
        self.assertEqual("08:00-12:00, 18:00-23:00", self.plugin._recruit_time_windows)
        self.assertEqual(5, self.plugin._recruit_interval_minutes)
        self.assertEqual(50, self.plugin._recruit_visit_count)

    def test_recruit_window_supports_active_and_outside_times(self):
        timezone = self.module.pytz.timezone("Asia/Shanghai")
        self.plugin._recruit_time_windows = "07:00-23:00"

        active = timezone.localize(self.module.datetime(2026, 8, 8, 9, 0, 0))
        outside = timezone.localize(self.module.datetime(2026, 8, 8, 23, 30, 0))

        self.assertTrue(self.plugin._is_in_recruit_time_window(active))
        self.assertFalse(self.plugin._is_in_recruit_time_window(outside))

    def test_choose_recruit_slot_filters_tiers_and_prefers_highest_value(self):
        visit_result = {
            "can_steal": True,
            "rows": [
                {
                    "slots": [
                        {"slot_id": "low", "can_steal": True, "bag_tier": 2, "point_bonus": 999},
                        {"slot_id": "wanted", "can_steal": True, "bag_tier": 3, "point_bonus": 4, "magic_bonus": 8},
                        {"slot_id": "blocked", "can_steal": False, "bag_tier": 3, "point_bonus": 9999},
                    ]
                }
            ],
        }

        chosen = self.plugin._choose_recruit_slot(visit_result)

        self.assertEqual("wanted", chosen["slot_id"])
        self.assertEqual(3, chosen["tier"])

    def test_recruit_cycle_steals_only_selected_tier_and_reports_actual_count(self):
        state = _base_state()
        state["user"]["id"] = 100
        state["steal"] = {"used": 1, "limit": 5}
        visit_result = {
            "success": True,
            "user_id": 200,
            "username": "目标甲",
            "can_steal": True,
            "rows": [{"slots": [
                {"slot_id": "tier-2", "can_steal": True, "bag_tier": 2, "emoji": "😀"},
                {"slot_id": "tier-3", "can_steal": True, "bag_tier": 3, "emoji": "🎭"},
            ]}],
        }

        def request_with_retry(label, func):
            if label == "viewStage":
                return visit_result
            return func()

        self.plugin._active_recruit_window = mock.Mock(return_value="2026-08-08|07:00-23:00")
        self.plugin._request_with_retry = request_with_retry
        self.plugin._fetch_bundle = mock.Mock(return_value={"state": state})
        self.plugin._post_action_confirmed = mock.Mock(return_value={"success": True})

        result = self.plugin._run_recruit_cycle(force=True)

        self.assertTrue(result["success"])
        self.assertEqual(1, result["stolen"])
        self.assertEqual({"知名": 1}, result["stolen_by_tier"])
        self.plugin._post_action_confirmed.assert_called_once_with(
            mock.ANY,
            "steal_actor",
            {"slot_id": "tier-3"},
            state,
        )
        self.plugin._append_history.assert_called_once()

    def test_recruit_cycle_without_target_keeps_next_check_and_no_success_history(self):
        state = _base_state()
        state["user"]["id"] = 100
        state["steal"] = {"used": 1, "limit": 5}
        visit_result = {
            "success": True,
            "user_id": 200,
            "username": "演出中",
            "can_steal": False,
            "rows": [{"slots": []}],
        }

        self.plugin._active_recruit_window = mock.Mock(return_value="2026-08-08|07:00-23:00")
        self.plugin._request_with_retry = mock.Mock(return_value=visit_result)
        self.plugin._fetch_bundle = mock.Mock(return_value={"state": state})

        result = self.plugin._run_recruit_cycle(force=True)

        self.assertTrue(result["success"])
        self.assertEqual(0, result["stolen"])
        self.assertGreater(result["next_check_ts"], int(self.plugin._aware_now().timestamp()))
        self.plugin._append_history.assert_not_called()
        self.plugin.post_message.assert_not_called()

    def test_recruit_cycle_stops_for_today_when_quota_is_exhausted(self):
        state = _base_state()
        state["user"]["id"] = 100
        state["steal"] = {"used": 5, "limit": 5}
        self.plugin._fetch_bundle = mock.Mock(return_value={"state": state})
        self.plugin._request_with_retry = mock.Mock()

        result = self.plugin._run_recruit_cycle(force=True)

        self.assertTrue(result["success"])
        self.assertEqual("今日挖角次数已用完", result["message"])
        self.plugin._request_with_retry.assert_not_called()
        self.assertGreater(result["next_check_ts"], int(self.plugin._aware_now().timestamp()))

    def test_steal_actor_timeout_confirmed_by_inventory_does_not_post_twice(self):
        before = _base_state()
        before["steal"] = {"used": 1, "limit": 5}
        before["actor_inventory_by_tier"] = {
            "3": [{"code": "actor", "quantity": 0, "available": 0}],
        }
        after = copy.deepcopy(before)
        after["steal"]["used"] = 2
        after["actor_inventory_by_tier"]["3"][0]["quantity"] = 1
        after["actor_inventory_by_tier"]["3"][0]["available"] = 1

        with (
            mock.patch.object(
                self.plugin,
                "_post_action",
                side_effect=self.module.requests.exceptions.Timeout("timeout"),
            ) as post_action,
            mock.patch.object(
                self.plugin,
                "_fetch_bundle_once",
                return_value={"state": after, "html": ""},
            ),
        ):
            result = self.plugin._post_action_confirmed(
                object(), "steal_actor", {"slot_id": "slot-1"}, before
            )

        self.assertTrue(result["success"])
        self.assertTrue(result["confirmed_after_network_error"])
        self.assertEqual(1, post_action.call_count)

    def test_get_service_registers_recruit_as_independent_date_job(self):
        self.plugin._auto_stage = False
        self.plugin._auto_spin = False
        self.plugin._auto_open_bags = False
        self.plugin._bootstrap_pending = False
        self.plugin._recruit_next_check_ts = int(self.plugin._aware_now().timestamp()) + 600

        services = self.plugin.get_service()

        recruit_services = [item for item in services if item["id"] == "VueEmoji_recruit"]
        self.assertEqual(1, len(recruit_services))
        self.assertEqual("date", recruit_services[0]["trigger"])
        self.assertEqual(self.plugin._recruit_worker, recruit_services[0]["func"])


if __name__ == "__main__":
    unittest.main()
