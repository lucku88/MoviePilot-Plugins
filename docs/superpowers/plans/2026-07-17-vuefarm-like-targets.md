# Vue-农场固定点赞目标与每日时间实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 修复偷菜多选换行后的输入框对齐，并让自动点赞在每天 09:00 后按固定用户名优先、随机目标补足到三个的规则执行。

**架构：** 后端新增统一的用户名列表规范化、目标合并和每日时间判断，自动调度只调用这些函数；前端仅负责展示和保存三个固定用户名与点赞时间。手动点赞弹窗继续使用原有随机接口，不与自动配置混合。

**技术栈：** Python、MoviePilot 插件 API、Vue 3、Vuetify 3、CSS Grid、`unittest`、Vite。

**后续调整：** 用户在 `0.2.7` 完成后要求改用思齐农场同款 Cron 设置；`0.2.8` 将 `like_time` 替换为 `like_cron`，默认 `0 9 * * *`，并保留旧时间配置迁移。

---

## 文件结构

- 修改 `plugins.v2/vuefarm/__init__.py`：保存新配置、合并固定与随机目标、限制每日执行时间。
- 修改 `plugins.v2/vuefarm/src/components/Config.vue`：新增固定目标与每日时间输入框，修复多选换行对齐。
- 修改 `tests/test_vuefarm_backend.py`：覆盖目标补齐、去重、全固定不请求随机和时间门槛。
- 修改 `README.md`、`package.v2.json`、`plugins.v2/vuefarm/package.json`、`plugins.v2/vuefarm/package-lock.json`：发布 `0.2.7`。
- 构建 `plugins.v2/vuefarm/dist/`：生成与源码一致的前端产物；仅在构建内容发生变化时提交。

### 任务 1：固定点赞目标配置与规范化

**文件：**
- 修改：`tests/test_vuefarm_backend.py`
- 修改：`plugins.v2/vuefarm/__init__.py`

- [ ] **步骤 1：编写失败测试，验证新配置默认值、去重和最多三个目标**

```python
def test_like_targets_config_normalizes_blank_duplicate_and_extra_names(self):
    config = self.plugin._default_config()
    config["like_targets"] = [" 用户甲 ", "", "用户甲", "用户乙", "用户丙", "用户丁"]
    config["like_time"] = "9:5"

    self.plugin._apply_config(config)

    self.assertEqual(["用户甲", "用户乙", "用户丙"], self.plugin._like_targets)
    self.assertEqual("09:05", self.plugin._like_time)
    self.assertEqual(["用户甲", "用户乙", "用户丙"], self.plugin._get_config()["like_targets"])
```

- [ ] **步骤 2：运行测试并确认因字段或规范化函数缺失而失败**

运行：

```powershell
python -m unittest tests.test_vuefarm_backend.VueFarmBackendTests.test_like_targets_config_normalizes_blank_duplicate_and_extra_names -v
```

预期：`FAIL`，当前插件没有 `_like_targets` 或返回配置中没有 `like_targets`。

- [ ] **步骤 3：实现配置字段与规范化函数**

在类属性中增加：

```python
_like_targets: List[str] = []
_like_time: str = "09:00"
```

新增函数：

```python
def _normalize_like_targets(self, value: Any, limit: int = 3) -> List[str]:
    if isinstance(value, str):
        source = re.split(r"[,，;；\n\r]+", value)
    else:
        source = value if isinstance(value, (list, tuple, set)) else []
    result: List[str] = []
    for item in source:
        username = str(item or "").strip()
        if username and username not in result:
            result.append(username)
        if len(result) >= limit:
            break
    return result

def _normalize_daily_time(self, value: Any, default: str = "09:00") -> str:
    matched = re.fullmatch(r"\s*(\d{1,2}):(\d{1,2})\s*", str(value or ""))
    if not matched:
        return default
    hour, minute = int(matched.group(1)), int(matched.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return default
    return f"{hour:02d}:{minute:02d}"
```

同步 `_default_config()`、`_apply_config()` 和 `_get_config()`。

- [ ] **步骤 4：运行目标测试确认通过**

运行同步骤 2，预期：`PASS`。

### 任务 2：固定目标优先并随机补齐到三个

**文件：**
- 修改：`tests/test_vuefarm_backend.py`
- 修改：`plugins.v2/vuefarm/__init__.py`

- [ ] **步骤 1：编写失败测试，验证一个固定目标补两个随机目标**

```python
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
```

- [ ] **步骤 2：编写失败测试，验证三个固定目标时不请求随机接口**

```python
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
```

- [ ] **步骤 3：运行两个测试并确认当前逻辑失败**

```powershell
python -m unittest tests.test_vuefarm_backend.VueFarmBackendTests.test_auto_like_fills_missing_fixed_slots_with_unique_random_targets tests.test_vuefarm_backend.VueFarmBackendTests.test_auto_like_with_three_fixed_targets_skips_random_target_request -v
```

预期：`FAIL`，当前 `_run_like_cycle()` 总是直接使用随机名单。

- [ ] **步骤 4：实现自动目标合并**

新增：

```python
def _build_auto_like_targets(self, session: requests.Session) -> Tuple[List[str], Optional[dict]]:
    usernames = self._normalize_like_targets(self._like_targets)
    if len(usernames) >= 3:
        return usernames[:3], None
    random_result = self._post_action(session, "random_like_targets", {}, retry_network=True)
    if not random_result.get("success"):
        return usernames, random_result
    for username in self._normalize_like_targets(random_result.get("usernames"), limit=30):
        if username not in usernames:
            usernames.append(username)
        if len(usernames) >= 3:
            break
    return usernames, random_result
```

修改 `_run_like_cycle()`：显式传入 `payload.usernames` 时继续使用手动名单；没有手动名单时调用 `_build_auto_like_targets()`，固定与随机都为空时沿用现有“今天不再重复检查”处理。

- [ ] **步骤 5：运行两个测试确认通过**

运行同步骤 3，预期：两个测试均 `PASS`。

### 任务 3：每日 09:00 时间门槛与错过补跑

**文件：**
- 修改：`tests/test_vuefarm_backend.py`
- 修改：`plugins.v2/vuefarm/__init__.py`

- [ ] **步骤 1：编写失败测试，验证设定时间之前不自动点赞**

```python
def test_social_worker_does_not_auto_like_before_daily_time(self):
    self.plugin._auto_steal = False
    self.plugin._auto_like = True
    self.plugin._like_time = "09:00"
    timezone = self.module.pytz.timezone("Asia/Shanghai")
    self.plugin._aware_now = lambda: timezone.localize(datetime(2026, 7, 17, 8, 59))
    calls = []
    self.plugin._run_like_cycle = lambda force=False, payload=None: calls.append(force) or {"success": True}

    self.plugin._social_worker(force=False)

    self.assertEqual([], calls)
```

- [ ] **步骤 2：编写失败测试，验证 09:00 后当天未点赞会补跑**

```python
def test_social_worker_catches_up_auto_like_after_daily_time(self):
    self.plugin._auto_steal = False
    self.plugin._auto_like = True
    self.plugin._like_time = "09:00"
    timezone = self.module.pytz.timezone("Asia/Shanghai")
    self.plugin._aware_now = lambda: timezone.localize(datetime(2026, 7, 17, 12, 0))
    calls = []
    self.plugin._run_like_cycle = lambda force=False, payload=None: calls.append(force) or {"success": True}

    self.plugin._social_worker(force=False)

    self.assertEqual([False], calls)
```

- [ ] **步骤 3：运行测试并确认时间门槛尚未实现**

```powershell
python -m unittest tests.test_vuefarm_backend.VueFarmBackendTests.test_social_worker_does_not_auto_like_before_daily_time tests.test_vuefarm_backend.VueFarmBackendTests.test_social_worker_catches_up_auto_like_after_daily_time -v
```

预期：第一个测试 `FAIL`，当前逻辑在当天首次检查时立即点赞。

- [ ] **步骤 4：实现每日时间判断**

```python
def _is_auto_like_due(self, now: Optional[datetime] = None) -> bool:
    current = now or self._aware_now()
    hour, minute = (int(part) for part in self._like_time.split(":"))
    scheduled = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return current >= scheduled and self.get_data("auto_like_date") != current.strftime("%Y-%m-%d")
```

将 `_social_worker()` 中的自动点赞条件改为：

```python
if self._auto_like and (force or self._is_auto_like_due()):
    like_result = self._run_like_cycle(force=force)
```

手动 `force=True` 保持不受时间限制。

- [ ] **步骤 5：运行时间测试确认通过**

运行同步骤 3，预期：两个测试均 `PASS`。

### 任务 4：配置页布局与新字段

**文件：**
- 修改：`plugins.v2/vuefarm/src/components/Config.vue`

- [ ] **步骤 1：为互动首行增加专用布局类并垂直居中**

将首个互动网格改为：

```vue
<div class="siqi-form-grid steal-interaction-grid">
```

增加主题无关样式：

```css
.steal-interaction-grid{align-items:center}
```

样式只改变网格项目的垂直位置，不写死背景色、文字色或高度。

- [ ] **步骤 2：新增固定目标和每日时间输入框**

在偷菜时间段之后增加：

```vue
<div class="siqi-form-grid like-target-grid">
  <v-text-field v-for="index in 3" :key="index" v-model="config.like_targets[index - 1]" :label="`固定点赞目标 ${index}`" density="compact" variant="outlined" hide-details class="siqi-input" prepend-inner-icon="mdi-account-heart-outline" />
  <v-text-field v-model="config.like_time" label="每日点赞时间" type="time" density="compact" variant="outlined" hide-details class="siqi-input like-time-field" prepend-inner-icon="mdi-clock-check-outline" />
</div>
<div class="siqi-field-hint">固定目标不足 3 个时会用随机目标补齐；每天到达设定时间后执行一次。</div>
```

在 `config` 默认值中增加：

```javascript
like_targets: ['', '', ''],
like_time: '09:00',
```

- [ ] **步骤 3：加载和保存时固定为三个可编辑位置**

新增：

```javascript
function normalizeLikeTargetFields(value) {
  const source = Array.isArray(value) ? value : String(value || '').split(/[,，;；\n\r]+/)
  return [...new Set(source.map(item => String(item || '').trim()).filter(Boolean))].slice(0, 3).concat(['', '', '']).slice(0, 3)
}
```

在 `loadConfig()`、`syncCookie()`、`saveConfig()` 前后调用该函数，并在保存请求中发送 `like_targets` 与 `like_time`。

- [ ] **步骤 4：运行前端构建**

```powershell
npm run build
```

工作目录：`plugins.v2/vuefarm`

预期：Vite 构建成功，无 Vue 模板或 CSS 错误。

### 任务 5：版本、文档和完整验证

**文件：**
- 修改：`README.md`
- 修改：`package.v2.json`
- 修改：`plugins.v2/vuefarm/__init__.py`
- 修改：`plugins.v2/vuefarm/package.json`
- 修改：`plugins.v2/vuefarm/package-lock.json`

- [ ] **步骤 1：版本升级到 `0.2.7`**

同步后端、市场索引、npm 包和 README 版本。市场历史写明：多选布局垂直居中、三个固定点赞目标随机补齐、每日 09:00 后执行与错过补跑。

- [ ] **步骤 2：运行后端完整测试**

```powershell
python -m py_compile plugins.v2\vuefarm\__init__.py
python -m unittest tests.test_vuefarm_backend tests.test_vue_autocatchup tests.test_vue_retry_limits -v
```

预期：全部测试通过，失败数为 0。

- [ ] **步骤 3：校验 JSON 与差异格式**

```powershell
python -c "import json; json.load(open('package.v2.json', encoding='utf-8')); json.load(open('plugins.v2/vuefarm/package.json', encoding='utf-8')); json.load(open('plugins.v2/vuefarm/package-lock.json', encoding='utf-8')); print('JSON OK')"
git diff --check
git status --short --branch
```

预期：JSON 输出 `JSON OK`，差异检查无错误，工作区只包含本计划列出的文件和构建产物。

- [ ] **步骤 4：提交实现**

```powershell
git add -- README.md package.v2.json plugins.v2/vuefarm tests/test_vuefarm_backend.py docs/superpowers/plans/2026-07-17-vuefarm-like-targets.md
git commit -m "feat(Vue-农场): 增加固定点赞目标和每日时间"
```

- [ ] **步骤 5：推送并核验远程 main**

```powershell
git push origin main
git status --short --branch
git log -1 --oneline --decorate
```

预期：`main` 与 `origin/main` 一致。不要调用 MoviePilot 的安装或插件更新接口；提醒用户刷新市场并手动更新。
