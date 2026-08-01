# Vue-表情 v0.1.5 稳定性与页面细节实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将 Vue-表情的网络请求限制为单层最多 5 次，对不可逆 POST 增加状态确认，清理重复老虎机方法，并统一舞台倒计时与操作控件布局。

**架构：** 保留单文件插件结构，在 `VueEmoji` 内增加小型动作标记和确认辅助函数，所有会改变站点状态的调用通过统一安全提交入口执行。前端继续使用现有 Vuetify 组件和 MoviePilot 主题变量，只调整状态来源与 CSS。

**技术栈：** Python 3、requests/urllib3、unittest、Vue 3、Vuetify 3、Vite 4。

---

## 文件职责

- 创建 `tests/test_vueemoji_backend.py`：后端重复方法、网络重试和动作恢复回归测试。
- 修改 `plugins.v2/vueemoji/__init__.py`：单层重试、安全动作确认、重复代码清理和版本号。
- 修改 `plugins.v2/vueemoji/src/components/Page.vue`：舞台单一倒计时与操作控件布局。
- 修改 `tests/test_vueemoji_frontend_contract.py`：前端行为契约。
- 修改 `plugins.v2/vueemoji/package.json`、`package-lock.json`、`package.v2.json`、`README.md`：发布元数据。
- 重建 `plugins.v2/vueemoji/dist/`：发布前端产物。

### 任务 1：锁定重复方法和双层重试

- [ ] **步骤 1：编写失败测试**

在 `tests/test_vueemoji_backend.py` 中加载真实 `VueEmoji` 类，并加入：

```python
def test_vueemoji_class_has_no_duplicate_methods(self):
    method_names = [node.name for node in self.class_node.body if isinstance(node, ast.FunctionDef)]
    self.assertEqual(len(method_names), len(set(method_names)))

def test_requests_adapter_does_not_retry_under_manual_retry_layer(self):
    self.plugin._build_session()
    self.assertEqual(0, captured_retry_kwargs["total"])
    self.assertEqual(0, captured_retry_kwargs["connect"])
    self.assertEqual(0, captured_retry_kwargs["read"])
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_vueemoji_backend -v`

预期：重复方法测试发现 `_run_auto_spin`、`_manual_spin`；适配器测试得到 `5` 而不是 `0`。

- [ ] **步骤 3：最少实现**

将 Retry 配置改为：

```python
retry = Retry(total=0, connect=0, read=0, redirect=0, status=0)
```

移动并保留带恢复逻辑的老虎机实现，删除旧重复定义；手动老虎机成功状态改为：

```python
after_state = self._extract_action_state(result) or self._fetch_bundle(session)["state"]
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m unittest tests.test_vueemoji_backend -v`

预期：任务 1 测试通过。

### 任务 2：不可逆 POST 状态确认

- [ ] **步骤 1：编写失败测试**

增加测试，模拟第一次 POST 已在服务端成功但客户端收到 Timeout，随后刷新状态已经变化：

```python
def test_spin_timeout_confirmed_by_state_does_not_post_twice(self):
    result = self.plugin._post_action_confirmed(session, "spin_slot", {"count": 1}, before_state)
    self.assertTrue(result["success"])
    self.assertEqual(1, session.post_calls)
```

再模拟状态明确未变化，前四次超时、第五次成功：

```python
def test_unchanged_state_allows_at_most_five_total_post_attempts(self):
    result = self.plugin._post_action_confirmed(session, "open_bag", {"tier": 1, "count": 1}, before_state)
    self.assertTrue(result["success"])
    self.assertEqual(5, session.post_calls)
```

覆盖 accept、reroll、upgrade、expand、confirm、recall 的状态标记变化判断。

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_vueemoji_backend -v`

预期：缺少 `_post_action_confirmed` 和动作标记函数。

- [ ] **步骤 3：实现动作确认辅助函数**

在插件类中新增四个边界明确的辅助函数：

```python
def _capture_action_marker(self, state: Dict[str, Any], action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": action, "payload": dict(payload), "state": self._action_marker_values(state, action, payload)}

def _action_was_applied(self, marker: Dict[str, Any], state: Dict[str, Any]) -> bool:
    return marker["state"] != self._action_marker_values(state, marker["action"], marker["payload"])

def _confirmed_action_result(self, before_state: Dict[str, Any], after_state: Dict[str, Any], action: str) -> Dict[str, Any]:
    result = {"success": True, "data": after_state, "confirmed_after_network_error": True}
    if action == "recall_stage":
        before_user = before_state.get("user") or {}
        after_user = after_state.get("user") or {}
        result["result"] = {
            "point_gain": max(0, self._safe_int(after_user.get("total_points"), 0) - self._safe_int(before_user.get("total_points"), 0)),
            "magic_gain": max(0, self._safe_int(after_user.get("magic"), 0) - self._safe_int(before_user.get("magic"), 0)),
        }
    return result
```

`_post_action_confirmed()` 每轮只发送一次 POST；网络异常后先 GET 页面确认。状态已变化直接返回 `_confirmed_action_result()`，明确未变化才进入下一轮，无法确认立即抛出原网络异常。

- [ ] **步骤 4：替换所有不可逆调用**

把自动和手动流程中的 `retry_network=True` 改为 `_post_action_confirmed(session, action, payload, before_state)`，并把每次动作前的完整状态传入。明确业务失败不重试。

- [ ] **步骤 5：运行测试验证通过**

运行：`python -m unittest tests.test_vueemoji_backend tests.test_vue_autocatchup tests.test_vue_retry_limits -v`

预期：全部通过。

### 任务 3：舞台时间与页面细节

- [ ] **步骤 1：编写失败的前端契约测试**

在 `tests/test_vueemoji_frontend_contract.py` 增加：

```python
def test_stage_uses_one_remaining_time_source(self):
    self.assertIn("stage.value.remaining_seconds", self.page)
    self.assertNotIn("'剩余 ' + stageRemainText.value", self.page)

def test_action_number_inputs_are_centered_and_mobile_safe(self):
    self.assertRegex(self.page, r"\.number-input\s*\{[^}]*text-align:\s*center")
    self.assertIn("align-items: center", self.page)
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_vueemoji_frontend_contract -v`

预期：舞台仍同时显示计算倒计时和后端说明，控件契约不完整。

- [ ] **步骤 3：最少页面实现**

让 `stageRemainText` 优先使用 `remaining_seconds`，动态任务卡片的说明不再重复另一个剩余时间；统一 `.number-input`、`.bag-action`、`.slot-machine-action` 的高度、居中和手机换行。

- [ ] **步骤 4：构建并验证**

运行：`npm run build`（工作目录 `plugins.v2/vueemoji`）。

运行：`python -m unittest tests.test_vueemoji_frontend_contract -v`

预期：构建成功，前端测试通过。

### 任务 4：发布 v0.1.5

- [ ] **步骤 1：更新版本元数据测试**

将 `tests/test_vueemoji_release_metadata.py` 的期望版本改为 `0.1.5`，并断言历史说明包含“重试”“状态确认”“舞台”。先运行确认版本不一致而失败。

- [ ] **步骤 2：同步版本文件**

更新后端、两个 npm 文件、市场索引和 README，说明小版本保留配置与历史。

- [ ] **步骤 3：完整验证**

运行：

```powershell
python -m py_compile plugins.v2\vueemoji\__init__.py
python -m unittest tests.test_vueemoji_backend tests.test_vueemoji_frontend_contract tests.test_vueemoji_release_metadata tests.test_vue_autocatchup tests.test_vue_retry_limits -v
npm run build
git diff --check
```

预期：所有命令退出码为 0。

### 任务 5：推送并更新 MoviePilot

- [ ] **步骤 1：提交与推送**

先执行 `git fetch origin main`，确认没有远端分叉；将功能分支快进合并到 `main`，提交信息为：

```text
fix(Vue-表情): 强化动作重试与页面状态
```

推送 `origin main` 并验证远端 SHA 与本地一致。

- [ ] **步骤 2：自动更新插件**

刷新 MoviePilot 插件市场，使用插件更新或插件管理中心重装 Vue-表情到 `0.1.5`。不得打印 Token、Cookie。

- [ ] **步骤 3：实机验证**

确认安装版本、启用状态、配置保留、状态页和配置页加载、调度注册、日志无新异常；检查深色、浅色和 390px 手机宽度。只进行刷新和读取状态，不执行消耗资源的游戏动作。
