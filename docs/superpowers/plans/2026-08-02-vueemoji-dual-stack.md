# Vue-表情移除优先 IPv4 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 从 Vue-表情前后端彻底移除“优先 IPv4”，让网络连接使用系统默认 IPv4/IPv6 双栈选择，并发布 `0.1.6`。

**架构：** 保留现有 requests Session、超时和单层重试逻辑，只删除对 `urllib3.util.connection.allowed_gai_family` 的全局改写。配置迁移采用“读取时忽略、保存时丢弃”方式，旧配置不会要求用户重置。

**技术栈：** Python 3、requests、unittest、Vue 3、Vuetify 3、Vite 4。

---

## 文件职责

- 修改 `tests/test_vueemoji_backend.py`：锁定双栈网络和旧配置迁移行为。
- 修改 `tests/test_vueemoji_frontend_contract.py`：锁定配置页不再展示或提交 IPv4 字段。
- 修改 `tests/test_vueemoji_release_metadata.py`：锁定 `0.1.6` 版本和发布说明。
- 修改 `plugins.v2/vueemoji/__init__.py`：删除 IPv4 状态、配置字段和全局网络改写。
- 修改 `plugins.v2/vueemoji/src/components/Config.vue`：删除开关，并过滤旧字段。
- 修改 `plugins.v2/vueemoji/package.json`、`package-lock.json`、`package.v2.json`、`README.md`：同步发布元数据。
- 重建 `plugins.v2/vueemoji/dist/`：生成发布前端文件。

### 任务 1：后端双栈与旧配置迁移

**文件：**
- 修改：`tests/test_vueemoji_backend.py`
- 修改：`plugins.v2/vueemoji/__init__.py`

- [ ] **步骤 1：编写失败测试**

新增测试，要求源码和配置不再包含 IPv4 强制逻辑：

```python
def test_source_does_not_patch_global_ipv4_resolution(self):
    self.assertNotIn("allowed_gai_family", self.source)
    self.assertNotIn("socket.AF_INET", self.source)

def test_legacy_force_ipv4_is_ignored_and_not_persisted(self):
    self.plugin._apply_config({**self.plugin._default_config(), "force_ipv4": True})
    captured = {}
    self.plugin.update_config = lambda payload: captured.update(payload)
    self.plugin._update_config()
    self.assertNotIn("force_ipv4", self.plugin._default_config())
    self.assertNotIn("force_ipv4", self.plugin._get_config())
    self.assertNotIn("force_ipv4", captured)
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_vueemoji_backend -v`

预期：测试因仍存在 `allowed_gai_family` 和 `force_ipv4` 而失败。

- [ ] **步骤 3：编写最少后端实现**

在 `plugins.v2/vueemoji/__init__.py` 中：

```python
# 删除 import socket
# 删除 import urllib3.util.connection as urllib3_connection
# 删除 _force_ipv4 类属性
# 从 _get_config、_default_config、_apply_config、_update_config 删除 force_ipv4

def _build_session(self) -> requests.Session:
    retry = Retry(total=0, connect=0, read=0, redirect=0, status=0)
    session = requests.Session()
    # 保留现有 adapter、headers 和 proxy 逻辑
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m unittest tests.test_vueemoji_backend -v`

预期：全部通过。

### 任务 2：配置页删除旧字段

**文件：**
- 修改：`tests/test_vueemoji_frontend_contract.py`
- 修改：`plugins.v2/vueemoji/src/components/Config.vue`

- [ ] **步骤 1：编写失败测试**

```python
def test_config_removes_legacy_ipv4_field(self):
    self.assertNotIn("config.force_ipv4", self.config)
    self.assertNotIn("force_ipv4:", self.config)
    self.assertNotIn("优先 IPv4", self.config)
    self.assertIn("const { effect_options, capture_tips, force_ipv4, ...rest }", self.config)
```

- [ ] **步骤 2：运行测试验证失败**

运行：`python -m unittest tests.test_vueemoji_frontend_contract -v`

预期：测试发现开关和默认字段仍存在。

- [ ] **步骤 3：编写最少前端实现**

删除 IPv4 开关和默认值，并在 `applyConfig` 中过滤旧字段：

```javascript
const { effect_options, capture_tips, force_ipv4, ...rest } = data || {}
Object.assign(config, rest)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`python -m unittest tests.test_vueemoji_frontend_contract -v`

预期：全部通过。

### 任务 3：发布 `0.1.6`

**文件：**
- 修改：`tests/test_vueemoji_release_metadata.py`
- 修改：`plugins.v2/vueemoji/__init__.py`
- 修改：`plugins.v2/vueemoji/package.json`
- 修改：`plugins.v2/vueemoji/package-lock.json`
- 修改：`package.v2.json`
- 修改：`README.md`
- 重建：`plugins.v2/vueemoji/dist/`

- [ ] **步骤 1：更新并运行失败的发布测试**

将 `EXPECTED_VERSION` 改为 `0.1.6`，并要求市场和 README 包含：

```python
for phrase in ("IPv4", "IPv6", "保留配置"):
    self.assertIn(phrase, note)
```

运行：`python -m unittest tests.test_vueemoji_release_metadata -v`

预期：版本仍为 `0.1.5`，测试失败。

- [ ] **步骤 2：同步版本与说明**

把后端和两个 npm 文件升级到 `0.1.6`；市场历史首项说明删除优先 IPv4、系统自动选择 IPv4/IPv6、小版本保留配置；README 同步相同信息。

- [ ] **步骤 3：安装依赖并构建**

在 `plugins.v2/vueemoji` 运行：

```powershell
npm ci
npm run build
```

预期：Vite 构建退出码为 0，`dist` 中不再包含“优先 IPv4”或 `force_ipv4`。

- [ ] **步骤 4：完整验证**

在仓库根目录运行：

```powershell
python -m py_compile plugins.v2\vueemoji\__init__.py
python -m unittest tests.test_vueemoji_backend tests.test_vueemoji_frontend_contract tests.test_vueemoji_release_metadata tests.test_vue_autocatchup tests.test_vue_retry_limits -v
git diff --check
```

预期：全部命令退出码为 0，61 项以上测试无失败。

- [ ] **步骤 5：提交并推送**

```powershell
git add README.md package.v2.json plugins.v2/vueemoji tests/test_vueemoji_backend.py tests/test_vueemoji_frontend_contract.py tests/test_vueemoji_release_metadata.py
git commit -m "fix(Vue-表情): 移除优先 IPv4 设置"
git push origin HEAD:main
```

- [ ] **步骤 6：更新 MoviePilot 并实测**

刷新插件市场，将 Vue-表情更新到 `0.1.6`。确认配置页没有“优先 IPv4”，旧配置、Cookie、执行历史和动态调度仍保留；调用状态刷新和立即运行一次，确认系统双栈访问正常且日志无新异常。

