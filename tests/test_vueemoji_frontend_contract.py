import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PAGE = REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Page.vue"
CONFIG = REPO_ROOT / "plugins.v2" / "vueemoji" / "src" / "components" / "Config.vue"


class VueEmojiFrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.compact_page = re.sub(r"\s+", "", cls.page)
        cls.compact_config = re.sub(r"\s+", "", cls.config)

    def test_status_page_uses_shared_adaptive_shell(self):
        for expected in (
            'class="siqi-page"',
            'class="siqi-topbar"',
            'class="mb-3 overview-grid"',
            'class="stat-card',
            'class="siqi-card next-run-card mb-3"',
            'class="emoji-hub-grid"',
            'class="siqi-card slot-card"',
            'class="siqi-card bag-card',
            'class="siqi-card catalog-card',
            'class="siqi-card stage-card',
            'class="siqi-card log-card',
        ):
            self.assertIn(expected, self.page)

        for forbidden in (
            "emoji-hero",
            "isDarkTheme",
            "MutationObserver",
            "prefers-color-scheme",
        ):
            self.assertNotIn(forbidden, self.page)

    def test_status_page_uses_single_line_dynamic_run_card(self):
        self.assertIn('class="siqi-card next-run-card mb-3"', self.page)
        self.assertIn('class="next-run-body"', self.page)
        self.assertIn('动态运行', self.page)
        self.assertIn('class="next-run-time"', self.page)
        self.assertNotIn('class="siqi-card schedule-board', self.page)

    def test_bag_cards_render_upgrade_controls_and_operation_logs(self):
        for expected in (
            'class="bag-upgrade-row"',
            'class="bag-upgrade-controls"',
            'class="number-input bag-upgrade-input"',
            'v-model="upgradeCounts[bag.upgrade_rule.key]"',
            '@click="upgradeBag(bag)"',
            'class="siqi-card log-card',
            '最近30次操作日志',
            'operationLogs',
        ):
            self.assertIn(expected, self.page)
        self.assertNotIn('🧾 最近30次操作日志', self.page)
        self.assertNotIn('>执行历史</', self.page)

    def test_bag_upgrade_controls_are_compact_and_right_aligned(self):
        self.assertRegex(
            self.compact_page,
            r"\.bag-upgrade-row\{[^}]*grid-template-columns:minmax\(0,1fr\)auto",
        )
        self.assertRegex(
            self.page,
            r"\.bag-upgrade-input\s*\{[^}]*width:\s*76px",
        )

    def test_bag_upgrade_tip_shares_row_with_right_aligned_controls(self):
        self.assertIn(
            '<div class="bag-upgrade-tip">{{ bag.upgrade_rule.tip }}</div>',
            self.page,
        )
        self.assertNotIn('class="bag-tip"', self.page)
        self.assertLess(
            self.page.index('class="bag-upgrade-tip"'),
            self.page.index('class="bag-upgrade-controls"'),
        )
        self.assertRegex(
            self.compact_page,
            r"\.bag-upgrade-row\{[^}]*grid-template-columns:minmax\(0,1fr\)auto",
        )
        self.assertRegex(
            self.compact_page,
            r"\.bag-upgrade-tip\{[^}]*min-width:0",
        )

    def test_slot_and_bags_share_a_compact_responsive_two_column_hub(self):
        self.assertLess(
            self.page.index('class="siqi-card slot-card'),
            self.page.index('class="siqi-card bag-card'),
        )
        self.assertIn('class="emoji-hub-stack"', self.page)
        self.assertLess(
            self.page.index('class="emoji-hub-stack"'),
            self.page.index('class="siqi-card bag-card'),
        )
        self.assertIn(
            ".emoji-hub-grid{display:grid;grid-template-columns:minmax(260px,.72fr)minmax(0,1.65fr);gap:12px;align-items:stretch;margin-bottom:12px}",
            self.compact_page,
        )
        self.assertIn(
            ".emoji-hub-grid>.emoji-hub-stack,.emoji-hub-grid>.siqi-card{height:100%;min-height:0}",
            self.compact_page,
        )
        self.assertIn(
            ".emoji-hub-stack{display:grid;grid-template-rows:minmax(190px,1fr)minmax(140px,1fr);gap:12px;min-height:0}",
            self.compact_page,
        )
        self.assertIn(
            "@media(max-width:1100px){.emoji-hub-grid{grid-template-columns:1fr}",
            self.compact_page,
        )

    def test_recruit_card_is_compact_and_keeps_required_status_fields(self):
        for expected in (
            'class="siqi-card recruit-card"',
            'class="recruit-meta-grid"',
            '<span>下次检查</span>',
            '<span>时间段</span>',
            '<span>今日额度</span>',
            '目标：{{ recruitTierText }}',
        ):
            self.assertIn(expected, self.page)
        for removed in ('<span>目标等级</span>', '<span>扫描设置</span>', '<span>最近结果</span>'):
            self.assertNotIn(removed, self.page)
        self.assertRegex(
            self.compact_page,
            r"\.recruit-body\{display:grid;gap:8px;padding:10px12px!important\}",
        )

    def test_stage_effect_choices_keep_text_controls_without_preview_animation(self):
        for expected in (
            'class="effect-grid"',
            'class="effect-card"',
            'v-for="effect in effects"',
            '@click="selectEffect(effect)"',
            'effect.point_bonus_pct',
            'effect.magic_bonus_pct',
            'effect.duration_text',
        ):
            self.assertIn(expected, self.page)

        for forbidden in (
            'class="effect-preview"',
            'effect-preview-emoji',
            'effect.animation_class',
            'effect.preview_emojis',
            'slot.animation_class',
            '.stage-anim-',
            '@keyframes vueemoji-',
        ):
            self.assertNotIn(forbidden, self.page)

        self.assertIn(
            ".actor-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(58px,1fr));gap:6px}",
            self.compact_page,
        )
        self.assertIn(".actor-main{font-size:22px", self.compact_page)

    def test_recruit_time_window_input_is_centered(self):
        self.assertIn('class="siqi-input siqi-time-input"', self.config)
        self.assertIn('.siqi-time-input :deep(input) { text-align: center; }', self.config)
        self.assertIn(
            ".stage-slot-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(44px,1fr));gap:6px",
            self.compact_page,
        )
        self.assertIn(".stage-slot-emoji{font-size:18px", self.compact_page)

    def test_status_page_keeps_all_manual_actions(self):
        for endpoint in (
            "/refresh",
            "/run",
            "/cookie",
            "/spin",
            "/open-bag",
            "/accept-open",
            "/reroll-open",
            "/upgrade-bag",
            "/expand-stage-row",
            "/confirm-stage",
            "/recall-stage",
        ):
            self.assertIn(endpoint, self.page)

    def test_toolbar_matches_farm_pill_and_toy_hierarchy(self):
        topbar = self.page.split('<div class="siqi-content">', 1)[0]
        for expected in (
            'aria-label="刷新 Vue-表情状态"',
            'aria-label="打开 Vue-表情配置"',
            'aria-label="关闭 Vue-表情"',
        ):
            self.assertIn(expected, topbar)

        self.assertNotIn('aria-label="立即执行 Vue-表情"', topbar)
        self.assertNotIn("同步 Cookie", topbar)
        self.assertIn('class="schedule-run-btn"', self.page)
        self.assertIn('@click="runNow"', self.page)

    def test_overview_is_four_cards_and_catalog_keeps_progress(self):
        self.assertIn("const overviewStats = computed", self.page)
        self.assertIn("const catalogStat = computed", self.page)
        self.assertIn("v-for=\"(item, index) in overviewStats\"", self.page)
        self.assertIn("catalogStat", self.page)
        self.assertIn(
            ".overview-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0012px!important;}",
            self.compact_page,
        )

    def test_status_page_matches_shared_tone_cards_and_section_headers(self):
        self.assertIn(
            "return ['green', 'orange', 'blue', 'red'][index] || 'green'",
            self.page,
        )
        for expected in (
            'siqi-card-title--schedule',
            'siqi-card-title--bags',
            'siqi-card-title--catalog',
            'siqi-card-title--stage',
            'siqi-card-title--logs',
            '.stat-card{--stat-rgb:',
            '.stat-red{--stat-rgb:239,68,68;',
            '.siqi-card-title--schedule{background:rgba(76,175,80,.08)}',
            '.siqi-card-title--bags{background:rgba(249,115,22,.09)}',
            '.siqi-card-title--catalog{background:rgba(59,130,246,.09)}',
            '.siqi-card-title--stage{background:rgba(245,158,11,.09)}',
            '.siqi-card-title--logs{background:rgba(20,184,166,.08)}',
        ):
            self.assertIn(expected, self.compact_page)

        self.assertIn(
            '.siqi-card-title{min-height:44px;',
            self.compact_page,
        )

    def test_operation_logs_wrap_long_details(self):
        self.assertIn('class="log-item-head"', self.page)
        self.assertIn('class="log-item-detail"', self.page)
        self.assertIn("overflow-wrap:anywhere", self.compact_page)

    def test_config_uses_shared_form_shell(self):
        for expected in (
            'class="siqi-config"',
            'class="siqi-topbar"',
            'class="siqi-switch-grid"',
            'class="siqi-switch-item',
            'class="siqi-switch-main"',
            'class="siqi-switch-label"',
            'class="siqi-switch-desc"',
            'class="siqi-form-grid"',
            'class="siqi-field"',
            'v-model="config.spin_cron"',
            'v-model="config.auto_stage_effect_key"',
            'v-model="config.random_delay_max_seconds"',
            'v-model="config.cookie"',
            "cookieVisible",
            "VCronField",
        ):
            self.assertIn(expected, self.config)

        for forbidden in ("isDarkTheme", "MutationObserver", "prefers-color-scheme"):
            self.assertNotIn(forbidden, self.config)

    def test_config_removes_legacy_ipv4_field(self):
        self.assertNotIn("config.force_ipv4", self.config)
        self.assertNotIn("force_ipv4:", self.config)
        self.assertNotIn("force_ipv4", self.config)
        self.assertNotIn("优先 IPv4", self.config)
        self.assertIn(
            "const legacyIpv4Key = ['force', 'ipv4'].join('_')",
            self.config,
        )
        self.assertIn("delete rest[legacyIpv4Key]", self.config)

    def test_pages_reuse_shared_theme_tokens(self):
        shared_tokens = (
            "color:rgba(var(--v-theme-on-surface),.85)",
            "border:1pxsolidrgba(var(--v-theme-on-surface),.12)",
            "background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))",
            "backdrop-filter:blur(20px)saturate(150%)",
            "border:.5pxsolidrgba(var(--v-theme-on-surface),.08)",
            "box-shadow:02px10pxrgba(0,0,0,.05)",
        )
        for token in shared_tokens:
            self.assertIn(token, self.compact_page)
            self.assertIn(token, self.compact_config)

    def test_pages_have_mobile_layout_without_horizontal_overflow(self):
        self.assertIn("@media (max-width: 600px)", self.page)
        self.assertIn("@media (max-width: 600px)", self.config)
        self.assertIn("overflow-x: hidden", self.page)
        self.assertIn("overflow-x: hidden", self.config)
        self.assertIn("min-height:44px", self.compact_page)
        self.assertIn("min-height: 44px", self.config)

    def test_stage_uses_one_remaining_time_source(self):
        self.assertIn("Number(stage.value.remaining_seconds || 0)", self.page)
        self.assertNotIn("meta: stage.value.current_text", self.page)
        self.assertNotIn("stage.current_text", self.page)
        self.assertIn("stage.value.current_effect_name", self.page)
        self.assertIn("stage.value.active_count", self.page)

    def test_action_number_inputs_are_centered_and_mobile_safe(self):
        self.assertRegex(
            self.page,
            r"\.number-input\s*\{[^}]*height:\s*44px[^}]*text-align:\s*center",
        )
        self.assertRegex(
            self.page,
            r"\.slot-center-row,\.bag-action\s*\{[^}]*align-items:\s*center[^}]*min-width:\s*0",
        )
        self.assertIn(
            ".slot-center-row:deep(.v-btn),.bag-action:deep(.v-btn){height:44px",
            self.compact_page,
        )


if __name__ == "__main__":
    unittest.main()
