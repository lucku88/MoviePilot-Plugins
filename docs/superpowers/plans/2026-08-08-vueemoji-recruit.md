# Vue-表情自动挖角实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为 Vue-表情 增加独立、可配置、按网站 `can_steal` 判断的自动访问舞台和挖角任务。

**架构：** 保留现有舞台、老虎机和开包的 `VueEmoji_auto` 动态任务，新增 `VueEmoji_recruit` date 服务和独立的下一次检查持久化数据。每轮先读取本人页面与额度，再随机访问配置数量的舞台；仅成功挖到符合等级的演员时写历史和通知。

**技术栈：** Python MoviePilot 插件、Requests、APScheduler date/CronTrigger、Vue 3、Vuetify、Vite、unittest。

---

### 任务 1：补齐后端行为测试

**文件：**
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/tests/test_vueemoji_backend.py`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/tests/test_vueemoji_frontend_contract.py`

- [ ] **步骤 1：编写失败测试**

在后端测试中加入默认配置、等级清洗、时间段、候选槽位、成功/无目标/额度耗尽、服务注册和超时确认测试；前端契约加入新字段、`/recruit`、多选控件和状态卡断言。测试直接调用 `VueEmoji._run_recruit_cycle()`，使用固定的页面桩：`view_stage` 返回顶层 `can_steal` 和 `rows[].slots[]`，`steal_actor` 返回成功。

- [ ] **步骤 2：运行测试确认红灯**

运行：`python -m unittest tests.test_vueemoji_backend tests.test_vueemoji_frontend_contract -v`

预期：新增断言失败，因为当前插件没有挖角配置、方法、服务和页面控件。

### 任务 2：实现独立挖角后端

**文件：**
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/__init__.py`

- [ ] **步骤 1：增加配置和持久化字段**

增加 `auto_recruit`、`recruit_tiers`、`recruit_time_windows`、`recruit_interval_minutes`、`recruit_visit_count` 属性；默认值分别为 `False`、`[1,2,3,4]`、`07:00-23:00`、`30`、`10`。实现 `_normalize_recruit_tiers()`、`_active_recruit_window()`、`_is_in_recruit_time_window()`、`_next_recruit_check_ts()`，所有输入都限制在规格范围内。

- [ ] **步骤 2：注册 API 和独立服务**

增加 `POST /recruit`，调用 `_recruit_api()`；在 `get_service()` 中保留原主服务，并在自动挖角打开时增加 `id="VueEmoji_recruit"` 的 date 服务，函数为 `_recruit_worker`，不复用主任务的 `next_run_time`。

- [ ] **步骤 3：实现候选选择和安全动作确认**

增加 `_collect_recruit_slots()`、`_choose_recruit_slot()`、`_recruit_action_marker_values()`。候选必须同时满足非本人、顶层 `can_steal`、槽位 `can_steal` 和配置等级；按等级、积分、魔力降序选一个。把 `steal_actor` 接入现有 `_post_action_confirmed()` 的状态确认分支，确认额度或演员库存已变化后不重复提交。

- [ ] **步骤 4：实现一轮扫描和调度**

增加 `_run_recruit_cycle(force=False)`：读取页面状态和额度，最多访问 `recruit_visit_count` 人；只读访问用 `_request_with_retry()`，实际挖角使用确认动作；没有目标不写成功历史、不通知；额度耗尽排到下一天；网络连续失败使用现有错误计数上限。成功结果按实际演员等级统计，保存 `recruit_last_result`、`recruit_next_check_ts` 等状态并调用 `_reregister_plugin()`。

- [ ] **步骤 5：运行后端测试确认通过**

运行：`python -m unittest tests.test_vueemoji_backend -v`

预期：全部通过，并且原有动作确认、IPv4 清理、日志解析测试不回归。

### 任务 3：接入 Vue 配置页和状态页

**文件：**
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/src/components/Config.vue`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/src/components/Page.vue`

- [ ] **步骤 1：配置页加入控件**

在现有自动化策略增加“自动挖角”开关；在参数设置增加演员等级多选、检查时间段、访问间隔和每轮访问人数，使用当前 `siqi-*` 卡片、输入框和主题变量，不写固定深色颜色。

- [ ] **步骤 2：状态页加入挖角状态**

动态运行卡保留原有主任务时间，在下面增加紧凑挖角信息卡，显示开关、下次检查、时间段、筛选等级、额度和最近结果；增加手动“检查挖角”按钮调用 `/recruit`，不调用主 `/run`。

- [ ] **步骤 3：运行前端契约测试**

运行：`python -m unittest tests.test_vueemoji_frontend_contract -v`

预期：新控件、状态字段和接口存在，旧页面风格契约继续通过。

### 任务 4：版本、文档和构建

**文件：**
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/__init__.py`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/package.json`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/package-lock.json`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/package.v2.json`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/README.md`
- 修改：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/tests/test_vueemoji_release_metadata.py`

- [ ] **步骤 1：升级版本元数据**

将 Vue-表情 从 `0.1.12` 升到 `0.1.13`，市场历史和 README 置顶说明自动挖角、默认关闭和小版本保留配置。

- [ ] **步骤 2：构建前端**

在 `plugins.v2/vueemoji` 运行：`npm run build`。确认 `dist/assets/assets/remoteEntry.js`、暴露的 Page/Config 文件和样式资源已更新。

- [ ] **步骤 3：运行发布元数据测试**

运行：`python -m unittest tests.test_vueemoji_release_metadata -v`

预期：后端、两个 package、市场索引、README 和 dist 版本/资源一致。

### 任务 5：完整验证、真实只读接口检查与发布

**文件：**
- 检查：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/__init__.py`
- 检查：`D:/01 Application/Codex/GitHub/MoviePilot-Plugins/plugins.v2/vueemoji/dist/`

- [ ] **步骤 1：运行静态和单元验证**

运行：`python -m py_compile plugins.v2/vueemoji/__init__.py`; `python -m unittest tests.test_vueemoji_backend tests.test_vueemoji_frontend_contract tests.test_vueemoji_release_metadata tests.test_vue_autocatchup -v`; `git diff --check`。

- [ ] **步骤 2：做真实只读访问验证**

使用现有 MoviePilot 浏览器会话读取已配置 Cookie，只调用 `GET /siqi_emoji.php` 和 `POST action=view_stage, random=1`，确认返回 JSON、`rows`/`can_steal` 能解析；不调用 `steal_actor`，不消耗额度。

- [ ] **步骤 3：检查工作区并提交**

运行：`git status --short`，确认只有 Vue-表情、测试、版本、README 和设计/计划文档相关修改；提交：`git commit -m "feat(Vue-表情): 增加独立自动挖角"`。

- [ ] **步骤 4：推送主分支**

运行：`git push origin main`，然后汇报提交号、测试结果和 MoviePilot 需要手动刷新市场后再更新插件的操作提示。
