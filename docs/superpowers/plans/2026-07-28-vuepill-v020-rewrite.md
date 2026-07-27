# Vue-魔丸 v0.2.0 重写实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans` 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将 `Vue-魔丸` 重写为 v0.2.0，完整移植 Vue-农场的页面风格，同时保留动态沙滩调度、搬砖 Cron、自动炼造/兑换和安全重试，并新增手动赠送与赠礼统计。

**架构：** 将当前单文件后端拆成站点请求、页面解析、炼造计算和插件生命周期四层。页面解析与计算层只接收普通数据，不发网络请求；生命周期层负责 MoviePilot 配置、调度、通知和 API。前端直接以 `plugins.v2/vuefarm/src/components` 的结构、主题变量和 Cron 控件为底稿，只替换业务字段和操作弹窗。

**技术栈：** Python 3、MoviePilot 插件 API、`requests`、`APScheduler`、Python 标准库 `html.parser`/`json`/`re`；Vue 3、Vuetify 3、Vite Module Federation。

---

## 文件边界

### 新建文件

- `plugins.v2/vuepill/site_client.py`：站点会话、Cookie、GET 页面、POST 动作、网络重试和响应校验。
- `plugins.v2/vuepill/page_parser.py`：纯页面解析，输出统计、搬砖、沙滩、兑换、物品、配方和按钮状态。
- `plugins.v2/vuepill/crafting.py`：库存映射、六层配方计算、兑换分批和赠送数量限制。
- `tests/fixtures/vuepill_page.html`：脱敏后的页面夹具，包含真实页面的嵌套卡片、禁用按钮、14 种物品和 6 种配方。
- `tests/test_vuepill_parser.py`：解析器回归测试。
- `tests/test_vuepill_crafting.py`：炼造、兑换和赠送计算测试。
- `tests/test_vuepill_client.py`：站点请求、重试次数和敏感信息屏蔽测试。
- `tests/test_vuepill_lifecycle.py`：v0.2.0 重置、Cookie 同步、API 和调度生命周期测试。
- `tests/test_vuepill_frontend_contract.py`：前端源码和 API 路径契约测试。

### 修改文件

- `plugins.v2/vuepill/__init__.py`：重写为插件生命周期、配置、调度、动作编排、历史和通知入口；删除重复定义。
- `plugins.v2/vuepill/src/components/Page.vue`：完整移植 Vue-农场状态页结构，加入魔丸业务卡片、赠送确认和统计弹窗。
- `plugins.v2/vuepill/src/components/Config.vue`：完整移植 Vue-农场配置页风格，改用 Cron 设置，移除 Cookie 开关和输入框。
- `plugins.v2/vuepill/src/App.vue`：将开发壳标题和背景改为与 Vue-农场一致的主题适配结构。
- `plugins.v2/vuepill/index.html`：更新页面标题为 `Vue-魔丸`。
- `plugins.v2/vuepill/vite.config.js`：保留 `VuePill` 联邦名称，确认构建输出仍写入 `dist/assets`。
- `plugins.v2/vuepill/package.json`：版本更新为 `0.2.0`。
- `plugins.v2/vuepill/package-lock.json`：根包和锁定包版本更新为 `0.2.0`。
- `package.v2.json`：市场索引版本、描述和 v0.2.0 历史说明。
- `README.md`：插件列表、功能说明和升级提示。
- `tests/test_vue_autocatchup.py`：将 Vue-魔丸补跑桩适配新模块，并保留沙滩/搬砖边界回归。

### 构建生成文件

- `plugins.v2/vuepill/dist/assets/**`：执行前端构建后整体更新，不手工修改压缩产物。

---

## 任务 0：建立 v0.1.18 稳定备份

**文件：** 无代码文件。

- [ ] **步骤 1：确认当前工作区只有规格和计划文档**

运行：

```powershell
git status --short
git log -1 --format="%H %s"
```

预期：没有未提交的插件代码；当前重写前插件代码提交为 `dd0daa8`。

- [ ] **步骤 2：创建指向重写前代码的稳定标签**

运行：

```powershell
git tag vuepill-v0.1.18-stable dd0daa8
git show --no-patch --format="%D %s" vuepill-v0.1.18-stable
```

预期：输出标签 `vuepill-v0.1.18-stable`，且指向 `dd0daa8`。

- [ ] **步骤 3：推送稳定标签，不修改 main 内容**

运行：

```powershell
git push origin vuepill-v0.1.18-stable
```

预期：GitHub 出现稳定标签；若远端已存在同名标签，先停止并比较两者提交，不能强制覆盖。

---

## 任务 1：先锁定真实页面解析行为

**文件：**
- 创建：`tests/fixtures/vuepill_page.html`
- 创建：`tests/test_vuepill_parser.py`

- [ ] **步骤 1：制作脱敏页面夹具**

从 `C:\Users\12089\.codex\attachments\8057d3dc-2cf7-4772-b84b-c2df1346d3e7\pasted-text.txt` 整理页面主体，并补入两组最小状态片段：

```html
<div id="beachStatus"><span class="countdown">下次清理: 0:06:15</span></div>
<button id="beachBtn" disabled="">清理沙滩</button>
<button id="collectAllTrashBtn" disabled="">一键收集</button>
<script>
  const gameData = {"server_now": 1785100000,"last_beach_time":1785096000,"beach_interval":7200};
</script>
```

夹具必须保留嵌套的 `.recipe` 卡片、`onclick="craft(1)"` 到 `onclick="craft(6)"`、`max` 属性、14 个 `.inventory-item` 和赠送按钮；不得保存 Cookie、Token 或真实 UID。

- [ ] **步骤 2：编写解析失败测试**

在 `tests/test_vuepill_parser.py` 定义纯模块导入和以下测试：

```python
def test_parse_page_reads_stats_inventory_and_giftable_items():
    data = parse_page(FIXTURE.read_text(encoding="utf-8"), now_ts=1785100000)
    assert data["stats"]["magic_pills"] == 57
    assert len(data["inventory"]) == 14
    assert data["inventory"][0]["giftable"] is True
    assert next(item for item in data["inventory"] if item["name"] == "魔丸")["count"] == 57

def test_disabled_beach_with_countdown_is_not_ready():
    data = parse_page(FIXTURE.read_text(encoding="utf-8"), now_ts=1785100000)
    assert data["beach"]["ready"] is False
    assert data["beach"]["collect_enabled"] is False
    assert data["beach"]["next_ready_ts"] > 1785100000

def test_nested_recipe_cards_keep_all_six_ids_and_limits():
    data = parse_page(FIXTURE.read_text(encoding="utf-8"), now_ts=1785100000)
    recipes = {row["craft_id"]: row for row in data["recipes"]}
    assert set(recipes) == {1, 2, 3, 4, 5, 6}
    assert recipes[1]["max_count"] == 8
    assert recipes[6]["ingredients"]["魔丸胚胎"] == 2
```

- [ ] **步骤 3：运行测试确认当前实现不能满足需求**

运行：

```powershell
python -m unittest tests.test_vuepill_parser -v
```

预期：FAIL，原因是 `plugins.v2/vuepill/page_parser.py` 尚未创建；这一步只确认测试确实覆盖新行为。

- [ ] **步骤 4：提交解析测试和夹具**

运行：

```powershell
git add tests/fixtures/vuepill_page.html tests/test_vuepill_parser.py
git commit -m "test(Vue-魔丸): 锁定页面解析规则"
```

---

## 任务 2：实现独立页面解析器

**文件：**
- 创建：`plugins.v2/vuepill/page_parser.py`
- 测试：`tests/test_vuepill_parser.py`

- [ ] **步骤 1：定义解析器公共接口和返回结构**

实现以下接口，不导入 MoviePilot、`requests` 或插件类：

```python
def parse_page(html: str, *, now_ts: Optional[int] = None) -> Dict[str, Any]:
    """解析 mowan.php 页面，永远返回稳定的业务字典。"""

def parse_inventory(container_html: str) -> List[Dict[str, Any]]: ...

def parse_recipes(container_html: str, inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]: ...
```

返回对象至少包含：

```python
{
    "title": str,
    "price_text": str,
    "stats": {"points": int, "bonus_earned": int, "magic_pills": int,
              "daily_bricks": int, "daily_limit": int},
    "brick": {"ready": bool, "daily_bricks": int, "daily_limit": int,
              "available_count": int, "bag_count": int, "next_reset_ts": int},
    "beach": {"ready": bool, "can_enter": bool, "can_collect": bool,
              "collect_enabled": bool, "has_trash": bool,
              "next_ready_ts": int, "status_text": str},
    "exchange": {"pill_price": int, "magic_pills": int, "points": int,
                 "max_count": int, "enabled": bool, "action_ready": bool},
    "inventory": list,
    "recipes": list,
    "server_now": int,
}
```

- [ ] **步骤 2：实现嵌套 HTML 块提取和数值清洗**

使用标准库 `HTMLParser` 或带深度计数的元素扫描，不能用当前的“遇到第一个 `</div>` 就结束”正则。统一实现：

```python
def safe_int(value: Any, default: int = 0) -> int: ...
def extract_balanced_blocks(html: str, class_name: str) -> List[str]: ...
def button_enabled(tag_html: str) -> bool: ...
```

数值解析要去掉逗号和单位；时间戳同时支持秒、毫秒、脚本中的 `server_now`/`serverNow`/`next_brick_reset_ts`/`last_beach_time`/`beachInterval`。

- [ ] **步骤 3：实现沙滩保守判定**

按下面的规则计算，不允许只因没有时间戳就返回 ready：

```python
future_ready = last_beach_time > 0 and last_beach_time + beach_interval > server_now
has_countdown = bool(re.search(r"倒计时|下次清理|冷却", status_text))
can_enter = enter_button_exists and enter_button_enabled and not future_ready and not has_countdown
can_collect = collect_button_enabled or has_trash
ready = can_enter and not can_collect
```

如果页面已进入沙滩且存在垃圾，`can_collect` 为真，即使进入冷却也保留收集动作；按钮禁用且存在倒计时时 `ready` 必须为假。

- [ ] **步骤 4：实现物品和配方解析**

每个物品输出 `name/icon/count/giftable/has_items`；配方输出 `craft_id/title/output_item/icon/ingredients/max_count/can_craft/enabled`。从 `onclick="craft(n)"` 读取编号，从每个 `material-item` 中解析名称和需求数量；页面完全缺少配方时才使用规格中的六个兼容定义。

- [ ] **步骤 5：运行解析测试并提交**

运行：

```powershell
python -m unittest tests.test_vuepill_parser -v
python -m py_compile plugins.v2/vuepill/page_parser.py
```

预期：全部解析测试 PASS，编译命令无输出。

提交：

```powershell
git add plugins.v2/vuepill/page_parser.py tests/test_vuepill_parser.py
git commit -m "feat(Vue-魔丸): 拆出稳健页面解析器"
```

---

## 任务 3：实现纯炼造、兑换和赠送计算

**文件：**
- 创建：`plugins.v2/vuepill/crafting.py`
- 创建：`tests/test_vuepill_crafting.py`

- [ ] **步骤 1：先编写计算测试**

定义六个配方的测试库存，并覆盖以下边界：

```python
def test_magic_pill_plan_uses_dynamic_recipe_ids():
    result = compute_magic_pill_plan(INVENTORY, RECIPES, target=1)
    assert result["plan"][1] == 2       # 木工件材料链
    assert result["plan"][2] == 2       # 塑料件材料链
    assert result["plan"][3] == 1
    assert result["plan"][4] == 1
    assert result["plan"][5] == 1
    assert result["plan"][6] == 1

def test_exchange_batches_never_cross_reserve_or_request_over_100():
    assert exchange_batches(current=257, reserve=10, max_per_request=100) == [100, 100, 47]
    assert exchange_batches(current=10, reserve=10, max_per_request=100) == []

def test_gift_limit_is_minimum_of_stock_and_500():
    assert max_gift_quantity({"木材": 501}, "木材") == 500
    assert max_gift_quantity({"木材": 3}, "木材") == 3
```

- [ ] **步骤 2：运行测试确认计算模块尚不存在**

运行：

```powershell
python -m unittest tests.test_vuepill_crafting -v
```

预期：FAIL，提示 `crafting` 模块或公共函数不存在。

- [ ] **步骤 3：实现明确的纯函数**

提供以下签名，并只传递普通字典：

```python
def inventory_to_map(items: Iterable[Dict[str, Any]], reserve_magic_pill_count: int = 0) -> Dict[str, int]: ...
def compute_magic_pill_plan(inventory: Dict[str, int], recipes: Iterable[Dict[str, Any]], target: Optional[int] = None) -> Dict[str, Any]: ...
def exchange_batches(current: int, reserve: int, max_per_request: int = 100) -> List[int]: ...
def max_gift_quantity(inventory: Dict[str, int], item_name: str, cap: int = 500) -> int: ...
```

炼造计划按基础材料到成品递归展开，先消费已有中间产物；每次成功请求后由生命周期层重新抓页面再计算下一步，不能把接口返回的累计库存当作本轮新增量。

- [ ] **步骤 4：运行计算测试并提交**

运行：

```powershell
python -m unittest tests.test_vuepill_crafting -v
python -m py_compile plugins.v2/vuepill/crafting.py
```

预期：全部 PASS。

提交：

```powershell
git add plugins.v2/vuepill/crafting.py tests/test_vuepill_crafting.py
git commit -m "feat(Vue-魔丸): 增加炼造兑换计算模块"
```

---

## 任务 4：抽离站点请求和网络重试

**文件：**
- 创建：`plugins.v2/vuepill/site_client.py`
- 创建：`tests/test_vuepill_client.py`

- [ ] **步骤 1：编写请求层测试**

使用假的 `Session` 和 `Response`，覆盖：

```python
def test_network_request_retries_at_most_five_times(self):
    client = make_client(retry_times=5)
    session = FailingSession(error=TimeoutError("read timed out"))
    with self.assertRaises(TimeoutError):
        client.post_action(session, "move_brick", retry_network=True)
    self.assertEqual(session.post_calls, 5)

def test_gift_action_is_not_retried_automatically(self):
    client = make_client(retry_times=5)
    session = FailingSession(error=TimeoutError("read timed out"))
    with self.assertRaises(TimeoutError):
        client.post_action(session, "gift_item", {"item_name": "木材"}, retry_network=False)
    self.assertEqual(session.post_calls, 1)
```

在测试文件中定义 `FailingSession`、`FakeResponse` 和 `make_client()`，并让测试类继承 `unittest.TestCase`；测试不能依赖仓库未安装的第三方测试库。

- [ ] **步骤 2：定义 `VuePillSiteClient`**

实现以下接口：

```python
class VuePillSiteClient:
    def __init__(self, site_url, cookie, user_agent, timeout, retry_times,
                 retry_delay_ms, use_proxy, force_ipv4, logger): ...
    def build_session(self) -> requests.Session: ...
    def fetch_page_html(self, session: requests.Session) -> str: ...
    def post_action(self, session, action: str, payload=None,
                    retry_network: bool = False) -> Dict[str, Any]: ...
```

GET 页面和明确允许重试的网络动作使用最多 5 次；`gift_item`、炼造、兑换等可能造成重复数据的动作默认只请求一次。日志只记录动作名、次数和脱敏错误，不记录 Cookie、请求头、Token 或 UID。

- [ ] **步骤 3：统一响应校验**

`post_action` 将非 JSON、HTTP 错误和 `success=false` 转为带网站 message 的异常/结果；不要把 HTML 登录页当成功 JSON。请求表单固定包含 `action`，业务字段由生命周期层传入；当前已确认的动作名只允许规格中的 8 个，拒绝 `reset_game` 和 `update_settings`。

- [ ] **步骤 4：运行请求层测试并提交**

运行：

```powershell
python -m unittest tests.test_vuepill_client -v
python -m py_compile plugins.v2/vuepill/site_client.py
```

预期：重试次数、无重试动作和敏感信息屏蔽测试全部 PASS。

提交：

```powershell
git add plugins.v2/vuepill/site_client.py tests/test_vuepill_client.py
git commit -m "feat(Vue-魔丸): 抽离站点请求和重试"
```

---

## 任务 5：重写插件配置、升级重置和公共 API

**文件：**
- 修改：`plugins.v2/vuepill/__init__.py`
- 创建：`tests/test_vuepill_lifecycle.py`

- [ ] **步骤 1：先写 v0.2.0 生命周期失败测试**

覆盖以下明确行为：

```python
def test_first_v020_init_resets_old_state_and_stays_disabled():
    plugin = make_plugin(config={"enabled": True, "reserve_magic_pill_count": 0})
    plugin.save_data("history", [{"title": "旧记录"}])
    plugin.save_data("next_run_time", "2026-01-01 00:00:00")
    plugin.init_plugin({"enabled": True, "reserve_magic_pill_count": 0})
    assert plugin.get_data("v020_initialized") is True
    assert plugin.get_data("history") == []
    assert plugin._enabled is False
    assert plugin._reserve_magic_pill_count == 10

def test_saved_config_after_migration_can_enable_plugin():
    plugin = make_plugin()
    plugin.save_data("v020_initialized", True)
    result = plugin._save_config({"enabled": True, "enable_beach": True})
    assert result["config"]["enabled"] is True

def test_public_config_and_api_never_expose_cookie_input():
    plugin = make_plugin()
    plugin.save_data("v020_initialized", True)
    assert "cookie" not in plugin._get_config()
    assert all(row["path"] != "/cookie" for row in plugin.get_api())
```

测试辅助函数 `make_plugin()` 要复用现有 `tests/test_vue_autocatchup.py` 的 MoviePilot 桩，但只实例化插件，不自动调用 `init_plugin()`；这样第一条测试才能先写入旧数据，再验证首次初始化清理范围。

- [ ] **步骤 2：实现一次性迁移和安全默认值**

加入常量 `MIGRATION_KEY = "v020_initialized"`。首次发现标记不存在时，按顺序停止服务、清空 `history`、`state`、`pill_status`、`last_run`、`next_run_time`、`next_trigger_time`、`next_trigger_mode`、`consecutive_error_retries` 和 `last_error_retry_detail`，写入默认配置并设置标记；不要清理 MoviePilot 站点 Cookie。默认值固定为：插件关闭、搬砖开启、动态沙滩开启、自动炼造关闭、自动兑换关闭、保留魔丸 10、请求重试 5 次、搬砖 Cron `5 0 * * *`。

- [ ] **步骤 3：固定站点 Cookie 自动同步**

删除公开配置中的 `auto_cookie` 和 `cookie`，保留内部 `_cookie`；`_ensure_cookie()` 每次请求前从 `SiteOper().get_by_domain("si-qi.xyz")` 读取最新 Cookie。状态只返回 `cookie_source` 和脱敏状态，不返回 Cookie 内容。同步失败时禁止改变账号数据的动作，并返回清楚的错误信息。

- [ ] **步骤 4：重建 API 列表和输入校验**

保留 `/config`、`/status`、`/refresh`、`/run`、`/move-bricks`、`/clean-beach`、`/exchange-points`、`/craft-item`、`/craft-max-pill`；新增：

```python
{"path": "/gift-item", "endpoint": self._gift_item_api, "methods": ["POST"], "auth": "bear"}
{"path": "/gift-stats", "endpoint": self._gift_stats_api, "methods": ["POST"], "auth": "bear"}
```

`gift-item` 校验物品必须在解析结果中 `giftable=true`，UID 非空，数量为正整数且不超过 `min(库存, 500)`；`gift-stats` 只接受 `direction in {"out", "in"}` 和 `range in {"30", "all"}`。两者都不把 Cookie、Token 或完整请求结果写入响应。

- [ ] **步骤 5：运行生命周期测试并提交基础重写**

运行：

```powershell
python -m unittest tests.test_vuepill_lifecycle -v
python -m py_compile plugins.v2/vuepill/__init__.py
```

预期：迁移、默认配置、Cookie 隐藏和 API 校验测试 PASS。

提交：

```powershell
git add plugins.v2/vuepill/__init__.py tests/test_vuepill_lifecycle.py
git commit -m "refactor(Vue-魔丸): 重建v020生命周期和配置"
```

---

## 任务 6：接回动态调度、动作边界和自动业务流

**文件：**
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`tests/test_vue_autocatchup.py`
- 修改：`tests/test_vue_retry_limits.py`

- [ ] **步骤 1：保留并扩展补跑测试**

新增或迁移以下测试名和断言：

```python
def test_save_refresh_runs_when_beach_is_ready(): ...
def test_bootstrap_refresh_runs_when_saved_plan_is_overdue(): ...
def test_pre_refresh_does_not_run_before_formal_time(): ...
def test_run_beach_rechecks_ready_after_first_page_is_cooling(): ...
def test_run_beach_stays_short_retry_when_every_refresh_is_not_ready(): ...
def test_run_brick_never_cleans_ready_beach(): ...
def test_today_brick_quota_does_not_trigger_on_every_restart(): ...
```

`run:beach` 的回归场景必须模拟：第一次页面冷却中、最终刷新 ready、`_run_beach_flow()` 只调用一次；未 ready 场景的 `next_trigger_mode` 必须保持 `run:beach`，不能被下一天的 `brick` 覆盖。

- [ ] **步骤 2：实现单一的调度入口**

删除 `__init__.py` 中第二份 `_run_brick_flow`、`_build_result_lines`、`_build_notify_text`、`_normalize_history_entry` 及其关联重复辅助函数，只保留一份实现。`get_service()` 只注册一个下一次 date 服务；启动时先注册一次 `status-init` 刷新，`onlyonce` 不再叠加第二个初始化任务。

- [ ] **步骤 3：实现沙滩正式触发窗口的二次确认**

在 `run_job()` 中保留动作边界：

```python
scheduled_action = self._resolve_scheduled_action(force, reason)
run_beach = self._enable_beach and scheduled_action in {"all", "beach"}
if run_beach and scheduled_action == "beach" and not page["beach"]["ready"]:
    page = self._refresh_beach_due_page(session, page)
if run_beach and page["beach"]["ready"]:
    beach_result = self._run_beach_flow(session)
```

正式窗口内最终刷新变 ready 时补调一次；仍未 ready 时调用 `_limit_retry_plan_if_needed("beach", now + ready_retry_seconds, ...)`。`run:brick` 只跑搬砖，不能因为沙滩 ready 顺带清理。

- [ ] **步骤 4：实现自动炼造和兑换的安全循环**

收集成功后才运行自动炼造/兑换；每个 `craft_item` 成功后重新抓页面、重新计算剩余计划。兑换使用 `exchange_batches(current, reserve, 100)`，每批成功后重抓库存，下一批数量取实际库存，任何时候都不得低于 10 个魔丸。部分失败保留已完成结果并停止后续步骤。

- [ ] **步骤 5：实现手动赠送和统计动作**

手动赠送流程只允许一次 POST，不自动重试；成功后刷新页面、追加一条 `🎁赠送：物品×数量 / 目标 UID ...` 历史。统计调用 `gift_stats`，返回最近 30 天或全部汇总，不写执行历史。

- [ ] **步骤 6：运行调度和重试回归**

运行：

```powershell
python -m unittest tests.test_vue_autocatchup -v
python -m unittest tests.test_vue_retry_limits -v
python -m py_compile plugins.v2/vuepill/__init__.py plugins.v2/vuepill/site_client.py plugins.v2/vuepill/page_parser.py plugins.v2/vuepill/crafting.py
```

预期：Vue-魔丸以及现有 Vue-玩偶/Vue-表情补跑和重试测试全部 PASS，且没有重复方法定义导致的覆盖。

提交：

```powershell
git add plugins.v2/vuepill/__init__.py tests/test_vue_autocatchup.py tests/test_vue_retry_limits.py
git commit -m "fix(Vue-魔丸): 保持动态调度和动作边界"
```

---

## 任务 7：移植 Vue-农场状态页并补齐赠送/炼造界面

**文件：**
- 修改：`plugins.v2/vuepill/src/components/Page.vue`
- 修改：`plugins.v2/vuepill/src/App.vue`
- 修改：`plugins.v2/vuepill/index.html`

- [ ] **步骤 1：先写前端静态契约检查**

在 `tests/test_vuepill_frontend_contract.py` 检查源码文本包含：

```python
assert "siqi-topbar" in page_source
assert "执行历史" in page_source
assert "gift-item" in page_source
assert "gift-stats" in page_source
assert "v-dialog" in page_source
assert "Vue-魔丸" in index_source
assert "同步 Cookie" not in page_source
```

同时检查状态页使用 `time` 右对齐、历史正文只显示一行，不再显示通用的“任务结果”标题。

- [ ] **步骤 2：以 Vue-农场 Page.vue 为视觉底稿**

直接移植 `plugins.v2/vuefarm/src/components/Page.vue` 的 `siqi-page`、`siqi-topbar`、`siqi-card`、主题变量、响应式网格和 `history-item` 结构；不要保留旧版 `vp-*` 紫色玻璃卡片作为主结构。保留 MoviePilot 自定义主题变量（`rgba(var(--v-theme-...), ...)`）和移动端断点。

- [ ] **步骤 3：接入魔丸状态数据**

状态页按顺序显示顶部工具栏、4 个概览卡、搬砖/沙滩动态调度卡、兑换卡、物品栏、炼造工坊和执行历史。API 调用统一使用：

```javascript
const PLUGIN_ID = 'VuePill'
const apiGet = path => props.api.get(`/plugin/${PLUGIN_ID}${path}`)
const apiPost = (path, data) => props.api.post(`/plugin/${PLUGIN_ID}${path}`, data)
```

页面只使用后端状态里的 `overview`、`brick`、`beach`、`exchange`、`inventory.items`、`recipes`、`history`，不在浏览器猜测可执行状态。

- [ ] **步骤 4：加入手动赠送二次确认和统计弹窗**

物品卡点击“赠送”打开 Vuetify 对话框，填写 UID 和数量；第一步校验数量上限，第二步用 `window.confirm` 或第二个确认按钮确认后才调用 `/gift-item`。统计按钮调用 `/gift-stats`，支持“最近 30 天”和“全部记录”、赠出/收到切换，显示总事件数、总数量、用户汇总和物品汇总。

- [ ] **步骤 5：加入动态六配方炼造和兑换**

每张配方卡使用后端的 `craft_id`、`ingredients`、`max_count` 和 `enabled`；数量输入上限绑定 `max_count`，材料不足时禁用按钮。兑换输入上限绑定后端 `exchange.max_count`，显示保留 10 个魔丸提示。一键炼造使用 `/craft-max-pill`，单配方使用 `/craft-item`。

- [ ] **步骤 6：运行前端静态检查并提交**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：契约测试 PASS。

提交：

```powershell
git add plugins.v2/vuepill/src/components/Page.vue plugins.v2/vuepill/src/App.vue plugins.v2/vuepill/index.html tests/test_vuepill_frontend_contract.py
git commit -m "feat(Vue-魔丸): 移植农场风格状态页"
```

---

## 任务 8：移植 Vue-农场配置页并固定 Cron/Cookie 规则

**文件：**
- 修改：`plugins.v2/vuepill/src/components/Config.vue`

- [ ] **步骤 1：复制配置页布局并删除旧 Cookie 控件**

以 `plugins.v2/vuefarm/src/components/Config.vue` 为底稿，保留 `siqi-config`、`siqi-topbar`、`siqi-switch-grid`、`siqi-form-grid` 和 MoviePilot 主题变量。删除 Cookie 开关、Cookie 文本框和“同步 Cookie”按钮，只显示“Cookie：从 MoviePilot 站点自动同步”的说明。

- [ ] **步骤 2：实现配置字段和默认值**

配置页字段固定为：启用插件、通知、立即运行一次、代理、强制 IPv4、自动搬砖、动态清沙滩、自动炼造、自动兑换、搬砖 Cron、冷却缓冲、保留魔丸、随机延迟、请求超时、网络重试次数和重试间隔。搬砖 Cron 使用 Vue-农场同款 `VCronField`，默认 `5 0 * * *`；保留魔丸默认 `10`，重试次数输入最大 `5`。

- [ ] **步骤 3：验证保存结果和重置提示**

保存调用 `/plugin/VuePill/config`，显示后端返回的“配置已保存”或“配置已保存，已执行补跑”。首次升级后配置保持关闭，页面提示用户保存一次新版设置后再启用任务。

- [ ] **步骤 4：运行前端编译前检查并提交**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：配置页不存在 Cookie 输入字段，存在 `VCronField` 和 `reserve_magic_pill_count`。

提交：

```powershell
git add plugins.v2/vuepill/src/components/Config.vue tests/test_vuepill_frontend_contract.py
git commit -m "feat(Vue-魔丸): 对齐农场配置页和Cron设置"
```

---

## 任务 9：版本、市场索引、README 和前端构建

**文件：**
- 修改：`plugins.v2/vuepill/package.json`
- 修改：`plugins.v2/vuepill/package-lock.json`
- 修改：`package.v2.json`
- 修改：`README.md`
- 生成：`plugins.v2/vuepill/dist/assets/**`

- [ ] **步骤 1：统一版本号**

将以下版本统一为 `0.2.0`：

```text
plugins.v2/vuepill/__init__.py      plugin_version
plugins.v2/vuepill/package.json     version
plugins.v2/vuepill/package-lock.json 根包 version
package.v2.json                    VuePill.version
```

在 `package.v2.json` 的 `VuePill.history` 首行加入：

```json
"v0.2.0": "重写 Vue-魔丸 页面和后端：移植 Vue-农场风格，修复真实配方/沙滩状态解析，加入手动赠送与赠礼统计，并首次升级时重置旧配置和历史。"
```

- [ ] **步骤 2：更新 README**

更新插件列表为 `v0.2.0`，补充：Cookie 自动同步、动态沙滩与搬砖独立 Cron、6 种配方、保留 10 个魔丸、手动赠送二次确认、赠礼/收礼统计和一次性升级重置。明确说明用户需要在 MoviePilot 中手动刷新市场并手动更新插件，不自动安装或更新。

- [ ] **步骤 3：安装依赖并构建远程前端**

在插件目录运行：

```powershell
npm install
npm run build
```

预期：`dist/assets/assets/remoteEntry.js`、`__federation_expose_Page-*.js` 和 `__federation_expose_Config-*.js` 重新生成，构建退出码为 0；不要手工编辑 `dist`。

- [ ] **步骤 4：提交版本和构建产物**

运行：

```powershell
git add plugins.v2/vuepill/package.json plugins.v2/vuepill/package-lock.json package.v2.json README.md plugins.v2/vuepill/dist/assets
git commit -m "release(Vue-魔丸): 发布v0.2.0"
```

---

## 任务 10：完整验证、线上只读冒烟和推送 main

**文件：** 已有全部 Vue-魔丸文件和测试文件。

- [ ] **步骤 1：运行 Python 测试套件**

运行：

```powershell
python -m unittest tests.test_vuepill_parser -v
python -m unittest tests.test_vuepill_crafting -v
python -m unittest tests.test_vuepill_client -v
python -m unittest tests.test_vuepill_lifecycle -v
python -m unittest tests.test_vue_autocatchup -v
python -m unittest tests.test_vue_retry_limits -v
```

预期：所有测试 PASS，无未捕获异常。

- [ ] **步骤 2：运行静态、JSON 和构建检查**

运行：

```powershell
python -m py_compile plugins.v2/vuepill/__init__.py plugins.v2/vuepill/site_client.py plugins.v2/vuepill/page_parser.py plugins.v2/vuepill/crafting.py
python -c "import json; json.load(open('package.v2.json', encoding='utf-8')); json.load(open('plugins.v2/vuepill/package.json', encoding='utf-8')); json.load(open('plugins.v2/vuepill/package-lock.json', encoding='utf-8')); print('metadata OK')"
git diff --check
npm run build
```

预期：输出 `metadata OK`，所有命令退出码为 0。

- [ ] **步骤 3：执行 MoviePilot 只读冒烟**

只调用插件状态和刷新接口，确认页面能加载、Cookie 来源显示为站点同步、14 种物品和 6 种配方能显示、沙滩倒计时状态不被误判为 ready。开发调试可以使用用户提供的 MoviePilot 地址和令牌，但令牌只能放在本机命令环境中，不写入脚本、日志、截图、提交或最终回复；不执行搬砖、沙滩、炼造、兑换和赠送动作。

- [ ] **步骤 4：核对变更范围和版本**

运行：

```powershell
git status --short
git diff --stat origin/main...HEAD
rg -n 'plugin_version = "0\.2\.0"|"version": "0\.2\.0"|"v0\.2\.0"' plugins.v2/vuepill/__init__.py plugins.v2/vuepill/package.json plugins.v2/vuepill/package-lock.json package.v2.json
```

预期：只包含 Vue-魔丸代码、测试、README、市场索引和前端构建产物；版本匹配 `0.2.0`。

- [ ] **步骤 5：提交最终验证并推送 main**

若前面验证产生了修正，先提交：

```powershell
git add plugins.v2/vuepill tests/test_vuepill_*.py tests/test_vue_autocatchup.py tests/test_vue_retry_limits.py package.v2.json README.md
git commit -m "test(Vue-魔丸): 完成v0.2.0发布验证"
```

确认工作区干净后推送：

```powershell
git push origin main
```

预期：`main` 推送成功；提醒用户在 MoviePilot 中手动刷新插件市场，再手动点击更新 `Vue-魔丸`。

---

## 规格覆盖自检

- 页面与配置：任务 7、8 完成 Vue-农场结构、主题适配、移动端和 Cron 控件移植。
- 物品、配方、沙滩和服务器时间：任务 1、2 完成解析测试与保守判定。
- 搬砖、动态沙滩和补跑：任务 6 完成调度、正式触发窗口和动作边界。
- 自动炼造、兑换保留和分批：任务 3、6 完成纯计算、重新抓取和 100 个上限。
- 手动赠送、统计和安全限制：任务 4、5、6、7 完成接口、校验、二次确认和只读统计。
- 一次性 v0.2.0 重置：任务 5 完成标记、清理范围和安全默认值。
- 网络重试与刷屏限制：任务 4、6、10 完成最多 5 次请求重试和连续短重试上限。
- 版本、README、市场索引和 dist：任务 9、10 完成。
- 稳定版本标签和发布推送：任务 0、10 完成。
