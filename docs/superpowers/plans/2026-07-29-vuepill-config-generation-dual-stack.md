# Vue-魔丸配置代号与双栈访问实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 保持 `Vue-魔丸 v0.2.0` 版本不变，为配置重置增加独立代号，并彻底移除强制 IPv4 配置与专用适配器。

**架构：** 后端用独立的 `CONFIG_GENERATION` 判断是否需要破坏性重置，普通插件版本更新不再参与清理判断；旧 `v020_initialized` 标记无损迁移为当前代号。网络客户端统一使用 `requests.adapters.HTTPAdapter`，由系统自动选择 IPv4 或 IPv6；前端、后端公开配置和旧保存字段同步收口。

**技术栈：** Python、`unittest`、Requests、Vue 3、Vuetify、Vite、MoviePilot 插件 API。

---

## 文件结构

- 修改：`plugins.v2/vuepill/__init__.py`，负责配置代号迁移、公开配置和站点客户端创建。
- 修改：`plugins.v2/vuepill/site_client.py`，删除 IPv4 专用适配器并统一创建标准会话。
- 修改：`plugins.v2/vuepill/src/components/Config.vue`，删除迁移警告和“强制 IPv4”开关。
- 修改：`plugins.v2/vuepill/src/utils/configValidation.js`，删除 `force_ipv4` 默认值和保存字段。
- 修改：`plugins.v2/vuepill/dist/**`，提交与源码一致的正式前端构建产物。
- 修改：`tests/test_vuepill_lifecycle.py`，覆盖配置代号迁移和后端配置兼容。
- 修改：`tests/test_vuepill_client.py`，覆盖标准双栈适配器和构造参数收口。
- 修改：`tests/test_vuepill_frontend_contract.py`，覆盖配置页字段、文案和运行时保存载荷。
- 修改：`tests/test_vuepill_release_metadata.py`，保持版本 `0.2.0` 并校验更新后的发布说明与构建产物。
- 修改：`package.v2.json`，更新现有 `v0.2.0` 说明，不新增版本节点。
- 修改：`README.md`，说明首次重写迁移与后续小更新的保留规则。

### 任务 1：用配置代号控制一次性重置

**文件：**
- 修改：`tests/test_vuepill_lifecycle.py`
- 修改：`plugins.v2/vuepill/__init__.py`

- [ ] **步骤 1：编写配置代号失败测试**

在 `VuePillLifecycleTests` 中新增或调整以下场景：

```python
def test_legacy_v020_marker_is_promoted_without_clearing_data(self):
    self.plugin.save_data("v020_initialized", True)
    self.plugin.save_data("history", [{"title": "保留记录"}])
    self.plugin.save_data("next_run_time", "2026-07-30 00:00:00")
    self.plugin.stop_service = lambda: None

    self.plugin.init_plugin({"enabled": True, "reserve_magic_pill_count": 7})

    self.assertEqual(
        self.plugin.CONFIG_GENERATION,
        self.plugin.get_data(self.plugin.CONFIG_GENERATION_KEY),
    )
    self.assertEqual([{"title": "保留记录"}], self.plugin.get_data("history"))
    self.assertEqual("2026-07-30 00:00:00", self.plugin.get_data("next_run_time"))
    self.assertIs(self.plugin._enabled, True)
    self.assertEqual(7, self.plugin._reserve_magic_pill_count)


def test_current_generation_minor_update_preserves_config_history_and_plan(self):
    self.plugin.save_data(
        self.plugin.CONFIG_GENERATION_KEY,
        self.plugin.CONFIG_GENERATION,
    )
    self.plugin.save_data("history", [{"title": "小版本记录"}])
    self.plugin.save_data("next_trigger_mode", "run:beach")
    self.plugin.stop_service = lambda: None

    self.plugin.init_plugin({"enabled": True, "notify": False})

    self.assertEqual([{"title": "小版本记录"}], self.plugin.get_data("history"))
    self.assertEqual("run:beach", self.plugin.get_data("next_trigger_mode"))
    self.assertIs(self.plugin._enabled, True)
    self.assertIs(self.plugin._notify, False)


def test_different_generation_resets_once_and_records_current_generation(self):
    self.plugin.save_data(self.plugin.CONFIG_GENERATION_KEY, 1)
    self.plugin.save_data("history", [{"title": "旧代数据"}])
    self.plugin.stop_service = lambda: None

    self.plugin.init_plugin({"enabled": True, "reserve_magic_pill_count": 3})

    self.assertEqual([], self.plugin.get_data("history"))
    self.assertIs(self.plugin._enabled, False)
    self.assertEqual(10, self.plugin._reserve_magic_pill_count)
    self.assertEqual(
        self.plugin.CONFIG_GENERATION,
        self.plugin.get_data(self.plugin.CONFIG_GENERATION_KEY),
    )
```

保留现有“旧 `v0.1.x` 配置首次进入 `v0.2.0` 会重置”“默认配置写入失败后可以重试”测试，并将断言扩展到配置代号。

- [ ] **步骤 2：运行测试确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_lifecycle -v
```

预期：新增测试因 `CONFIG_GENERATION`、`CONFIG_GENERATION_KEY` 或代号迁移逻辑不存在而失败。

- [ ] **步骤 3：实现最小配置代号逻辑**

在 `plugins.v2/vuepill/__init__.py` 定义：

```python
LEGACY_MIGRATION_KEY = "v020_initialized"
CONFIG_GENERATION_KEY = "config_generation"
CONFIG_GENERATION = 2
```

在 `VuePill` 类暴露同名常量，并新增严格读取与迁移模式判断：

```python
def _stored_config_generation(self) -> Optional[int]:
    raw = self.get_data(self.CONFIG_GENERATION_KEY)
    if raw in (None, ""):
        return None
    if isinstance(raw, bool):
        return -1
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw.strip())
    return -1

def _config_generation_mode(self, config: Optional[dict]) -> str:
    stored = self._stored_config_generation()
    if stored == self.CONFIG_GENERATION:
        return "current"
    if stored is None and self.get_data(self.LEGACY_MIGRATION_KEY):
        return "legacy-current"
    if stored is None and not config:
        return "fresh"
    return "reset"
```

调整 `_init_plugin_locked()`：

- `legacy-current` 只补写 `config_generation = 2`，随后按原配置继续初始化。
- `current` 不执行任何清理。
- `fresh` 写入安全默认配置和当前代号，不清理不存在的数据。
- `reset` 执行 `_reset_v020_data()`，成功写入默认配置后再保存当前代号。
- 为兼容已发布代码，完成初始化后继续保存 `v020_initialized = true`，但后续是否重置只由配置代号决定。

- [ ] **步骤 4：运行生命周期测试确认通过**

运行：

```powershell
python -m unittest tests.test_vuepill_lifecycle -v
```

预期：全部通过，测试数量不少于现有 46 项加新增用例。

- [ ] **步骤 5：提交配置代号改动**

```powershell
git add plugins.v2/vuepill/__init__.py tests/test_vuepill_lifecycle.py
git commit -m "fix(Vue-魔丸): 用配置代号控制升级重置"
```

### 任务 2：删除后端强制 IPv4 支持

**文件：**
- 修改：`tests/test_vuepill_client.py`
- 修改：`tests/test_vuepill_lifecycle.py`
- 修改：`plugins.v2/vuepill/site_client.py`
- 修改：`plugins.v2/vuepill/__init__.py`

- [ ] **步骤 1：编写双栈访问失败测试**

从测试客户端默认构造参数中删除 `force_ipv4`，并用以下测试替换原 IPv4 专用适配器测试：

```python
def test_build_session_uses_standard_adapters_without_forcing_source_address(self):
    client, _ = self.make_client()
    sentinel = lambda: socket.AF_UNSPEC
    connection_module = sys.modules["urllib3.util.connection"]

    with mock.patch.object(connection_module, "allowed_gai_family", sentinel):
        session = client.build_session()
        self.addCleanup(session.close)
        self.assertIs(sentinel, connection_module.allowed_gai_family)

    for prefix in ("http://", "https://"):
        adapter = session.adapters[prefix]
        self.assertIs(type(adapter), self.module.HTTPAdapter)
        self.assertNotIn(
            "source_address",
            adapter.poolmanager.connection_pool_kw,
        )
        self.assertEqual(0, adapter.max_retries.total)
```

在生命周期测试中增加公开配置兼容断言：

```python
def test_legacy_force_ipv4_is_ignored_and_not_saved(self):
    self.plugin.save_data(self.plugin.CONFIG_GENERATION_KEY, self.plugin.CONFIG_GENERATION)
    self.plugin.stop_service = lambda: None
    self.plugin.init_plugin({"enabled": False, "force_ipv4": True})

    self.assertNotIn("force_ipv4", self.plugin._get_config(include_options=False))
    self.plugin._update_config()
    self.assertNotIn("force_ipv4", self.plugin._config_store)
```

- [ ] **步骤 2：运行测试确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_client tests.test_vuepill_lifecycle -v
```

预期：客户端仍要求 `force_ipv4` 参数，后端公开配置仍包含该字段，测试失败。

- [ ] **步骤 3：删除 IPv4 专用实现**

在 `plugins.v2/vuepill/site_client.py`：

- 删除 `_IPv4HTTPAdapter` 类。
- 删除 `VuePillSiteClient.__init__()` 的 `force_ipv4` 参数和 `self.force_ipv4`。
- `build_session()` 固定创建标准 `HTTPAdapter`：

```python
adapter = HTTPAdapter(
    max_retries=0,
    pool_connections=10,
    pool_maxsize=10,
)
```

在 `plugins.v2/vuepill/__init__.py`：

- 删除 `_force_ipv4` 类属性和实例赋值。
- 从 `_get_config()`、`_default_config()`、`_apply_config()` 删除 `force_ipv4`。
- 创建 `VuePillSiteClient` 时不再传递 `force_ipv4`。
- 旧保存配置通过 `_merge_public_config()` 的允许字段过滤自然忽略。

- [ ] **步骤 4：运行客户端与生命周期测试确认通过**

运行：

```powershell
python -m unittest tests.test_vuepill_client tests.test_vuepill_lifecycle -v
```

预期：全部通过，且源码中不再存在 `_IPv4HTTPAdapter`。

- [ ] **步骤 5：提交后端双栈改动**

```powershell
git add plugins.v2/vuepill/__init__.py plugins.v2/vuepill/site_client.py tests/test_vuepill_client.py tests/test_vuepill_lifecycle.py
git commit -m "fix(Vue-魔丸): 移除强制IPv4访问限制"
```

### 任务 3：清理配置页字段和迁移警告

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/components/Config.vue`
- 修改：`plugins.v2/vuepill/src/utils/configValidation.js`
- 修改：`plugins.v2/vuepill/dist/**`

- [ ] **步骤 1：先修改前端契约测试**

将所有期望 `force_ipv4` 存在的字段列表、默认配置和保存载荷断言删除，并新增：

```python
def test_config_removes_ipv4_toggle_and_fixed_migration_warning(self):
    self.assertNotIn("force_ipv4", self.config)
    self.assertNotIn("强制IPv4", self.config)
    self.assertNotIn("v0.2.0 升级提示", self.config)
```

在运行时保存载荷测试中传入旧配置字段：

```javascript
initialConfig: {
  enabled: true,
  force_ipv4: true,
}
```

并断言发送给后端的 JSON 不包含 `force_ipv4`。

- [ ] **步骤 2：运行前端测试确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：配置源码仍包含开关、默认字段和迁移提示，新增断言失败。

- [ ] **步骤 3：删除前端字段和提示**

在 `Config.vue` 删除：

- 固定显示的 `v0.2.0` 迁移警告。
- “强制 IPv4”开关卡片。
- `CONFIG_FIELDS` 和 `DEFAULT_CONFIG` 中的 `force_ipv4`。

在 `configValidation.js` 删除：

- `BOOLEAN_CONFIG_FIELDS` 中的 `force_ipv4`。
- `DEFAULT_CONFIG` 中的 `force_ipv4`。

保留现有基础设置网格，删除一个卡片后由 CSS 自动重排，不新增专用布局。

- [ ] **步骤 4：运行前端测试并正式构建**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
npm run build
```

工作目录：`plugins.v2/vuepill`。

预期：前端契约测试通过，Vite 构建退出码为 0，`dist` 中不再出现 `force_ipv4`、`强制IPv4` 或固定迁移提示。

- [ ] **步骤 5：提交前端与构建产物**

```powershell
git add plugins.v2/vuepill/src plugins.v2/vuepill/dist tests/test_vuepill_frontend_contract.py
git commit -m "fix(Vue-魔丸): 清理IPv4配置与迁移提示"
```

### 任务 4：同步文档、市场说明和发布验证

**文件：**
- 修改：`README.md`
- 修改：`package.v2.json`
- 修改：`tests/test_vuepill_release_metadata.py`

- [ ] **步骤 1：更新发布测试的同版本说明**

保持：

```python
EXPECTED_VERSION = "0.2.0"
```

将 `EXPECTED_HISTORY` 改为与市场索引一致的新说明：

```python
EXPECTED_HISTORY = (
    "重写 Vue-魔丸 页面和后端：移植 Vue-农场风格，修复真实配方/沙滩状态解析，"
    "加入手动赠送与赠礼统计；首次从 v0.1.x 升级时重置一次，后续小更新保留配置，"
    "并移除强制 IPv4 限制以支持 IPv4/IPv6 自动访问。"
)
```

- [ ] **步骤 2：运行发布测试确认说明尚未同步**

运行：

```powershell
python -m unittest tests.test_vuepill_release_metadata -v
```

预期：`package.v2.json` 和 README 仍是旧说明，元数据断言失败。

- [ ] **步骤 3：更新 README 与市场索引**

- `package.v2.json` 只修改现有 `VuePill.history.v0.2.0` 文案，不新增 `v0.2.1`。
- README 将“后续小更新保留配置”写清楚，并补充默认支持 IPv4/IPv6 自动访问。
- `plugins.v2/vuepill/package.json` 和 `package-lock.json` 继续保持 `0.2.0`，不作版本修改。

- [ ] **步骤 4：运行发布与构建一致性测试**

运行：

```powershell
python -m unittest tests.test_vuepill_release_metadata -v
```

预期：10 项发布测试全部通过，测试内会执行干净的 `npm ci`、正式构建，并逐字节核对 13 个 `dist` 文件。

- [ ] **步骤 5：提交文档与索引**

```powershell
git add README.md package.v2.json tests/test_vuepill_release_metadata.py
git commit -m "docs(Vue-魔丸): 说明配置保留与双栈访问"
```

### 任务 5：最终验证

**文件：**
- 验证：`plugins.v2/vuepill/**`
- 验证：`tests/test_vuepill_*.py`
- 验证：`tests/test_vue_autocatchup.py`
- 验证：`tests/test_vue_retry_limits.py`

- [ ] **步骤 1：运行 Python 编译检查**

```powershell
python -m py_compile plugins.v2\vuepill\__init__.py plugins.v2\vuepill\site_client.py plugins.v2\vuepill\page_parser.py plugins.v2\vuepill\crafting.py
```

预期：退出码为 0，无输出。

- [ ] **步骤 2：分模块运行 266 项相关测试**

为避免仓库中其他插件测试留下的全局替身互相污染，以下模块分别在独立 Python 进程运行：

```powershell
python -m unittest tests.test_vue_autocatchup
python -m unittest tests.test_vue_retry_limits
python -m unittest tests.test_vuepill_business_flows
python -m unittest tests.test_vuepill_client
python -m unittest tests.test_vuepill_crafting
python -m unittest tests.test_vuepill_frontend_contract
python -m unittest tests.test_vuepill_lifecycle
python -m unittest tests.test_vuepill_parser
python -m unittest tests.test_vuepill_release_metadata
```

预期：各进程退出码均为 0；原基线合计 266 项，新增配置代号测试后总数相应增加。

- [ ] **步骤 3：验证版本和 JSON**

```powershell
python -c "import json, pathlib; p=json.loads(pathlib.Path('package.v2.json').read_text(encoding='utf-8')); a=json.loads(pathlib.Path('plugins.v2/vuepill/package.json').read_text(encoding='utf-8')); b=json.loads(pathlib.Path('plugins.v2/vuepill/package-lock.json').read_text(encoding='utf-8')); assert p['VuePill']['version']==a['version']==b['version']=='0.2.0'; print('VuePill version 0.2.0 OK')"
```

预期：输出 `VuePill version 0.2.0 OK`。

- [ ] **步骤 4：检查残留字段和 Git 差异**

```powershell
rg -n -g "test_vuepill_*.py" "force_ipv4|强制IPv4|_IPv4HTTPAdapter" plugins.v2/vuepill tests
git diff --check main...HEAD
git status --short --branch
```

预期：第一条没有业务源码或正式构建残留，只允许设计/计划文档描述该旧字段；`git diff --check` 无输出；工作区没有未提交文件。

- [ ] **步骤 5：停止在本地功能分支**

不推送、不安装、不更新 MoviePilot 插件。向用户报告验证结果，等待用户确认是否合并并推送 `main`。
