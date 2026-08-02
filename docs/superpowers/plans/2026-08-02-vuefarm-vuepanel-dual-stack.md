# Vue-农场与 Vue-面板双栈清理实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 删除 Vue-农场和 Vue-面板剩余的 IPv4 强制配置与运行逻辑，并在热更新时安全恢复旧版留下的全局网络选择器。

**架构：** 两个插件继续使用现有 `requests.Session` 和重试配置，连接地址族交回 Python 与操作系统自动选择。旧配置采用“读取忽略、保存丢弃”迁移；热更新清理通过函数源码文件精确识别旧版 lambda，只恢复当前插件自己留下的限制。

**技术栈：** Python 3、MoviePilot 插件 API、Vue 3、Vuetify、Vite、`unittest`、Git。

---

## 文件职责

- `tests/test_vue_dual_stack_cleanup.py`：覆盖两个插件的旧配置迁移、热更新清理、前端字段删除和版本一致性。
- `tests/test_vuefarm_backend.py`：更新 Vue-农场发布版本断言，移除测试夹具中的旧运行字段。
- `plugins.v2/vuefarm/__init__.py`：删除 IPv4 配置与运行限制，增加仅针对农场旧代码的热更新清理。
- `plugins.v2/vuefarm/src/components/Config.vue`：删除开关，并确保旧接口字段不会被再次提交。
- `plugins.v2/vuepanel/__init__.py`：删除 IPv4 配置与运行限制，增加仅针对面板旧代码的热更新清理。
- `plugins.v2/vuepanel/src/components/Page.vue`：删除隐藏在配置模型和保存载荷中的旧字段。
- `plugins.v2/vuefarm/package.json`、`plugins.v2/vuefarm/package-lock.json`：同步农场版本。
- `plugins.v2/vuepanel/package.json`、`plugins.v2/vuepanel/package-lock.json`：同步面板版本。
- `plugins.v2/vuefarm/dist/**`、`plugins.v2/vuepanel/dist/**`：提交重新构建后的联邦前端产物。
- `package.v2.json`、`README.md`：同步市场版本和升级说明。

### 任务 1：建立双栈回归测试

**文件：**
- 创建：`tests/test_vue_dual_stack_cleanup.py`
- 修改：`tests/test_vuefarm_backend.py`

- [ ] **步骤 1：编写失败的后端和前端契约测试**

测试文件加载两个插件，并覆盖以下行为：

```python
def test_sources_do_not_keep_ipv4_config_or_runtime_patch(self):
    for source in (self.farm_source, self.panel_source):
        self.assertNotIn("_force_ipv4", source)
        self.assertNotIn("lambda: socket.AF_INET", source)

def test_legacy_config_is_ignored_and_not_persisted(self):
    for plugin in (self.farm, self.panel):
        plugin._apply_config({**plugin._default_config(), "force_ipv4": True})
        captured = {}
        plugin.update_config = lambda payload, target=captured: target.update(payload)
        plugin._update_config()
        self.assertNotIn("force_ipv4", plugin._default_config())
        self.assertNotIn("force_ipv4", plugin._get_config())
        self.assertNotIn("force_ipv4", captured)

def test_hot_upgrade_restores_only_own_legacy_selector(self):
    legacy = eval(compile("lambda: socket.AF_INET", str(source_path), "eval"), {"socket": socket})
    connection.allowed_gai_family = legacy
    plugin._restore_legacy_address_family_selector()
    self.assertEqual(socket.AF_UNSPEC, connection.allowed_gai_family())

def test_frontend_does_not_render_or_submit_ipv4_setting(self):
    self.assertNotIn("强制 IPv4", self.farm_config)
    self.assertNotIn("config.force_ipv4", self.farm_config)
    self.assertNotIn("force_ipv4", self.panel_page)
```

版本测试固定期望：

```python
EXPECTED = {"VueFarm": "0.2.14", "VuePanel": "0.1.36"}
```

- [ ] **步骤 2：运行测试确认正确失败**

运行：

```powershell
python -m unittest tests.test_vue_dual_stack_cleanup tests.test_vuefarm_backend -v
```

预期：新增测试因源码仍存在 `_force_ipv4`、前端仍存在字段、缺少清理方法和版本未升级而失败。

- [ ] **步骤 3：提交测试红灯**

```powershell
git add -- tests/test_vue_dual_stack_cleanup.py tests/test_vuefarm_backend.py
git commit -m "test(Vue插件): 锁定农场与面板双栈迁移"
```

### 任务 2：删除前后端 IPv4 限制

**文件：**
- 修改：`plugins.v2/vuefarm/__init__.py`
- 修改：`plugins.v2/vuefarm/src/components/Config.vue`
- 修改：`plugins.v2/vuepanel/__init__.py`
- 修改：`plugins.v2/vuepanel/src/components/Page.vue`

- [ ] **步骤 1：实现后端最小迁移逻辑**

两个插件删除 `_force_ipv4` 的声明、读取、返回和持久化，并删除运行前的全局 lambda。初始化入口调用以下同形方法：

```python
@staticmethod
def _restore_legacy_address_family_selector():
    selector = getattr(urllib3_connection, "allowed_gai_family", None)
    code = getattr(selector, "__code__", None)
    try:
        is_own_source = Path(str(getattr(code, "co_filename", ""))).resolve() == Path(__file__).resolve()
    except Exception:
        is_own_source = False
    is_legacy_patch = (
        getattr(selector, "__name__", "") == "<lambda>"
        and getattr(code, "co_argcount", -1) == 0
        and tuple(getattr(code, "co_names", ())) == ("socket", "AF_INET")
        and is_own_source
    )
    if not is_legacy_patch:
        return

    def system_address_family():
        if getattr(urllib3_connection, "HAS_IPV6", True):
            return socket.AF_UNSPEC
        return socket.AF_INET

    urllib3_connection.allowed_gai_family = system_address_family
    logger.info("%s 已清理旧版遗留的 IPv4 网络限制", PluginClass.plugin_name)
```

- [ ] **步骤 2：实现前端旧字段过滤**

农场删除可见开关和默认值，并使用动态旧键避免旧接口响应被展开回保存请求：

```javascript
const legacyIpv4Key = ['force', 'ipv4'].join('_')

function mergeConfig(source = {}) {
  const next = { ...source }
  delete next[legacyIpv4Key]
  Object.assign(config, next)
  delete config[legacyIpv4Key]
}
```

保存前构造载荷并执行 `delete payload[legacyIpv4Key]`。面板从 `createEmptyConfig()`、`normalizeConfig()` 和 `serializeConfig()` 删除对应字段，旧导入数据通过已存在的白名单归一化自然丢弃。

- [ ] **步骤 3：运行目标测试确认逻辑通过**

```powershell
python -m unittest tests.test_vue_dual_stack_cleanup tests.test_vuefarm_backend -v
```

预期：除发布版本断言外，双栈行为测试通过。

- [ ] **步骤 4：提交实现**

```powershell
git add -- plugins.v2/vuefarm/__init__.py plugins.v2/vuefarm/src/components/Config.vue plugins.v2/vuepanel/__init__.py plugins.v2/vuepanel/src/components/Page.vue
git commit -m "fix(Vue插件): 移除农场与面板 IPv4 限制"
```

### 任务 3：发布版本与前端产物

**文件：**
- 修改：`plugins.v2/vuefarm/__init__.py`
- 修改：`plugins.v2/vuefarm/package.json`
- 修改：`plugins.v2/vuefarm/package-lock.json`
- 修改：`plugins.v2/vuefarm/dist/**`
- 修改：`plugins.v2/vuepanel/__init__.py`
- 修改：`plugins.v2/vuepanel/package.json`
- 修改：`plugins.v2/vuepanel/package-lock.json`
- 修改：`plugins.v2/vuepanel/dist/**`
- 修改：`package.v2.json`
- 修改：`README.md`

- [ ] **步骤 1：同步版本和发布说明**

农场统一为 `0.2.14`，面板统一为 `0.1.36`。市场历史和 README 说明删除 IPv4 限制、系统自动选择 IPv4/IPv6、热更新无需重置、现有配置和历史继续保留。

- [ ] **步骤 2：安装依赖并构建两个插件**

```powershell
Set-Location plugins.v2/vuefarm
npm ci
npm run build
Set-Location ../vuepanel
npm ci
npm run build
```

预期：两个 Vite 构建均以退出码 `0` 完成，`dist` 中不含 `force_ipv4` 或“强制 IPv4”。

- [ ] **步骤 3：运行目标测试和产物检查**

```powershell
python -m unittest tests.test_vue_dual_stack_cleanup tests.test_vuefarm_backend -v
rg -n "force_ipv4|强制 IPv4" plugins.v2/vuefarm/src plugins.v2/vuefarm/dist plugins.v2/vuepanel/src plugins.v2/vuepanel/dist
```

预期：测试全部通过；`rg` 无匹配并返回未找到状态。

- [ ] **步骤 4：提交发布内容**

```powershell
git add -- plugins.v2/vuefarm plugins.v2/vuepanel package.v2.json README.md tests/test_vue_dual_stack_cleanup.py tests/test_vuefarm_backend.py
git commit -m "chore(Vue插件): 发布农场与面板双栈版本"
```

### 任务 4：完整验证、集成和实测

**文件：**
- 检查：本计划涉及的全部文件

- [ ] **步骤 1：运行静态和完整自动测试**

```powershell
python -m py_compile plugins.v2/vuefarm/__init__.py plugins.v2/vuepanel/__init__.py
python -m unittest discover -s tests -p "test_vue*.py" -v
python -c "import json; json.load(open('package.v2.json', encoding='utf-8')); print('package.v2.json OK')"
git diff --check main...HEAD
git status --short
```

预期：Python 编译成功，全部 Vue 测试通过，JSON 可解析，差异检查无错误，工作区只包含计划内提交。

- [ ] **步骤 2：合并并推送 `main`**

在主工作区快进合并 `fix/vuefarm-vuepanel-dual-stack`，再次运行目标测试后推送：

```powershell
git merge --ff-only fix/vuefarm-vuepanel-dual-stack
git push origin main
```

- [ ] **步骤 3：更新 MoviePilot 并验证**

使用现有已登录浏览器会话刷新插件市场，更新 Vue-农场和 Vue-面板。浏览器重载后确认：

- Vue-农场显示 `v0.2.14`，配置页没有“强制 IPv4”。
- Vue-面板显示 `v0.1.36`，配置接口不再返回 `force_ipv4`。
- 两个插件原有 Cookie、卡片配置、执行历史和调度数据仍在。
- 分别执行状态刷新；Vue-面板再选择一个不会造成额外资源消耗的启用卡片做实际请求，确认网络访问正常且日志没有新的地址族异常。

- [ ] **步骤 4：清理隔离工作区**

确认远端 `main` 包含全部提交后，移除工作树和功能分支，不删除主工作区原有未跟踪文件。
