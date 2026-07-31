# Vue-魔丸自动 Cookie 与页面精简实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 按 `Vue-思齐农场 v1.0.3` 的样式自动展示 MoviePilot 站点 Cookie，同时避免自动值被保存成旧 Cookie，并精简炼造卡片与状态页操作栏。

**架构：** 后端配置 GET 接口返回即时解析的 Cookie 和“自动填入”标记，但持久化配置仍只保存手动 Cookie。前端跟踪 Cookie 是否被用户编辑，保存时把未编辑的自动值还原为空字符串。页面显示调整只改变 Vue 模板，不扩大后端动作范围。

**技术栈：** Python、`unittest`、Vue 3、Vuetify、Vite、MoviePilot 插件 API。

---

### 任务 1：自动 Cookie 配置协议

**文件：**
- 修改：`tests/test_vuepill_lifecycle.py`
- 修改：`plugins.v2/vuepill/__init__.py`

- [ ] 增加失败测试：配置 GET 在没有手动 Cookie 时返回 MoviePilot 最新 Cookie，并带 `cookie_auto_filled: true`。
- [ ] 增加失败测试：公开配置读取后执行 `_update_config()`，持久化的 `cookie` 仍为空字符串。
- [ ] 增加失败测试：手动 Cookie 返回 `cookie_auto_filled: false`，且仍优先于站点 Cookie。
- [ ] 运行指定测试，确认因新协议尚不存在而失败。
- [ ] 新增独立配置 GET 处理方法，只为配置页解析最新 Cookie；内部 `_get_config()` 继续只返回手动值。
- [ ] 运行指定测试，确认通过。

### 任务 2：Cookie 输入框保存语义与页面精简

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/components/Config.vue`
- 修改：`plugins.v2/vuepill/src/components/Page.vue`

- [ ] 增加失败测试：自动 Cookie 未编辑时保存载荷为 `cookie: ''`，手动编辑时保存新值，清空时恢复自动同步。
- [ ] 增加失败测试：状态页不存在顶部立即执行按钮与 `runNow`；材料不足和零上限提示不再渲染。
- [ ] 运行前端契约测试，确认因页面尚未修改而失败。
- [ ] 在 `Config.vue` 增加自动填入和编辑状态，保持思齐农场同款隐藏/眼睛样式。
- [ ] 在 `Page.vue` 删除顶部执行按钮和死代码，零上限时隐藏数量，材料不足时不显示原因条。
- [ ] 运行前端契约测试，确认通过。

### 任务 3：发布、构建与验证

**文件：**
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`plugins.v2/vuepill/package.json`
- 修改：`plugins.v2/vuepill/package-lock.json`
- 修改：`plugins.v2/vuepill/dist/**`
- 修改：`package.v2.json`
- 修改：`README.md`
- 修改：`tests/test_vuepill_release_metadata.py`

- [ ] 先把发布测试期望升级到 `0.2.4`，运行并确认失败。
- [ ] 同步全部版本和发布说明，构建正式 `dist`。
- [ ] 分别运行 Vue-魔丸测试模块、Python 编译、JSON 解析、干净前端构建和 `git diff --check`。
- [ ] 检查变更只涉及 Vue-魔丸、测试、版本元数据和本设计/计划文档。
- [ ] 使用中文提交信息提交并推送 `origin main`，提醒用户手动刷新市场并更新插件。

