# Vue 动态插件启动恢复实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 防止 MoviePilot 容器启动较慢时丢弃四个 Vue 插件的启动初始化和动态一次性任务，同时保持全部原有动态运行规则不变。

**架构：** 继续使用各插件现有的 `date` 动态服务，只在 APScheduler 参数中增加无限迟到宽限、积压合并和单实例限制。测试直接检查四个插件实际返回的服务定义，并保护农场社交 CRON 与表情挖角的原有触发方式。

**技术栈：** Python、MoviePilot 插件 API、APScheduler 3.11、`unittest`、JSON、Git。

---

## 文件结构

- 修改：`tests/test_vue_autocatchup.py`，让现有 MoviePilot 桩可以加载 Vue-农场。
- 创建：`tests/test_vue_startup_recovery.py`，覆盖四个插件动态任务的迟到宽限参数和非目标服务保护。
- 修改：`plugins.v2/vuefarm/__init__.py`，保护农场动态初始化和收菜任务。
- 修改：`plugins.v2/vuepill/__init__.py`，保护魔丸动态初始化、沙滩和搬砖任务。
- 修改：`plugins.v2/vuetoy/__init__.py`，保护玩偶动态初始化和展位任务。
- 修改：`plugins.v2/vueemoji/__init__.py`，保护表情主动态任务和自动挖角动态任务。
- 修改：四个插件的 `package.json` 与 `package-lock.json`，同步补丁版本。
- 修改：`package.v2.json`，同步市场版本与更新历史。
- 修改：`README.md`，同步版本表和四个插件的启动恢复说明。
- 修改：四个现有发布元数据测试，更新期望版本与最新历史说明。

### 任务 1：添加启动调度回归测试

**文件：**
- 修改：`tests/test_vue_autocatchup.py`
- 创建：`tests/test_vue_startup_recovery.py`

- [ ] **步骤 1：让通用加载器支持 Vue-农场**

在 `PLUGIN_INITS` 中加入：

```python
"vuefarm": REPO_ROOT / "plugins.v2" / "vuefarm" / "__init__.py",
```

- [ ] **步骤 2：编写失败的动态任务保护测试**

创建测试辅助断言：

```python
def assert_resilient_date_service(testcase, service):
    testcase.assertEqual("date", service["trigger"])
    testcase.assertIsNone(service["kwargs"]["misfire_grace_time"])
    testcase.assertTrue(service["kwargs"]["coalesce"])
    testcase.assertEqual(1, service["kwargs"]["max_instances"])
```

分别实例化 Vue-农场、Vue-魔丸、Vue-玩偶和 Vue-表情，将插件设置为启用和启动初始化待执行，断言主动态服务包含以上参数。

Vue-表情另外启用自动挖角并设置未来检查时间，断言 `VueEmoji_recruit` 仍为 `date` 服务且同样包含保护参数。

农场启用社交功能后，断言 `VueFarm_social` 仍使用 CRON 触发器，未被改成 `date` 服务。

- [ ] **步骤 3：运行测试确认旧代码失败**

运行：

```powershell
python -m unittest tests.test_vue_startup_recovery -v
```

预期：FAIL，失败原因是动态服务 `kwargs` 中没有 `misfire_grace_time`、`coalesce` 或 `max_instances`。

- [ ] **步骤 4：提交失败测试**

```powershell
git add tests/test_vue_autocatchup.py tests/test_vue_startup_recovery.py
git commit -m "test(Vue插件): 覆盖启动任务迟到保护"
```

### 任务 2：为四个插件增加动态任务迟到保护

**文件：**
- 修改：`plugins.v2/vuefarm/__init__.py`
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`plugins.v2/vuetoy/__init__.py`
- 修改：`plugins.v2/vueemoji/__init__.py`

- [ ] **步骤 1：修改 Vue-农场动态服务**

将 `VueFarm_auto` 的调度参数调整为：

```python
"kwargs": {
    "run_date": next_run,
    "misfire_grace_time": None,
    "coalesce": True,
    "max_instances": 1,
},
```

不要修改 `VueFarm_social`。

- [ ] **步骤 2：修改 Vue-魔丸动态服务**

将 `VuePill_auto` 使用相同的 4 个调度参数。不要修改动作选择、预刷新或补跑逻辑。

- [ ] **步骤 3：修改 Vue-玩偶动态服务**

将 `VueToy_auto` 使用相同的 4 个调度参数。不要修改展位保护、收回或外展逻辑。

- [ ] **步骤 4：修改 Vue-表情动态服务**

将 `VueEmoji_auto` 和 `VueEmoji_recruit` 都使用相同的 4 个调度参数。保持两项服务现有的 `run_date` 计算和独立服务 ID 不变。

- [ ] **步骤 5：运行调度测试确认通过**

运行：

```powershell
python -m unittest tests.test_vue_startup_recovery tests.test_vue_autocatchup -v
```

预期：全部通过，旧有 28 个自动补跑测试不发生回归。

- [ ] **步骤 6：提交后端修复**

```powershell
git add plugins.v2/vuefarm/__init__.py plugins.v2/vuepill/__init__.py plugins.v2/vuetoy/__init__.py plugins.v2/vueemoji/__init__.py
git commit -m "fix(Vue插件): 防止启动时丢失动态任务"
```

### 任务 3：同步四个插件发布版本

**文件：**
- 修改：`plugins.v2/vuefarm/__init__.py`
- 修改：`plugins.v2/vuefarm/package.json`
- 修改：`plugins.v2/vuefarm/package-lock.json`
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`plugins.v2/vuepill/package.json`
- 修改：`plugins.v2/vuepill/package-lock.json`
- 修改：`plugins.v2/vuetoy/__init__.py`
- 修改：`plugins.v2/vuetoy/package.json`
- 修改：`plugins.v2/vuetoy/package-lock.json`
- 修改：`plugins.v2/vueemoji/__init__.py`
- 修改：`plugins.v2/vueemoji/package.json`
- 修改：`plugins.v2/vueemoji/package-lock.json`
- 修改：`package.v2.json`
- 修改：`README.md`
- 修改：`tests/test_vuefarm_backend.py`
- 修改：`tests/test_vuepill_release_metadata.py`
- 修改：`tests/test_vuetoy_release_metadata.py`
- 修改：`tests/test_vueemoji_release_metadata.py`

- [ ] **步骤 1：更新版本号**

使用以下版本：

```text
Vue-农场  0.2.17
Vue-魔丸  0.2.16
Vue-玩偶  0.2.9
Vue-表情  0.1.18
```

- [ ] **步骤 2：增加市场历史说明**

四条最新历史都应说明：

```text
修复 MoviePilot 容器重启或更新后，启动初始化和动态一次性任务可能因调度器启动较慢而被判定为错过的问题；任务迟到后仍会执行一次状态刷新，并沿用现有规则判断是否补跑。小版本升级继续保留配置、Cookie、执行历史和动态调度计划。
```

根据插件名称调整主语，不添加未实现的业务变化。

- [ ] **步骤 3：更新 README**

更新顶部版本表，并在四个插件各自章节最前面增加新版本说明。说明动态运行规则未改成固定周期。

- [ ] **步骤 4：更新发布元数据测试**

更新四个测试中的期望版本，并让最新历史断言包含：

```python
for phrase in ("容器重启", "动态", "错过", "保留配置"):
    self.assertIn(phrase, latest_note)
```

Vue-魔丸测试需要在 `EXPECTED_HISTORY_KEYS` 首位增加 `v0.2.16`，并保留对旧历史内容的完整断言。

- [ ] **步骤 5：运行发布元数据测试**

运行：

```powershell
python -m unittest tests.test_vuefarm_backend tests.test_vuepill_release_metadata tests.test_vuetoy_release_metadata tests.test_vueemoji_release_metadata -v
```

预期：全部通过。

- [ ] **步骤 6：提交发布元数据**

```powershell
git add README.md package.v2.json plugins.v2/vuefarm plugins.v2/vuepill plugins.v2/vuetoy plugins.v2/vueemoji tests/test_vuefarm_backend.py tests/test_vuepill_release_metadata.py tests/test_vuetoy_release_metadata.py tests/test_vueemoji_release_metadata.py
git commit -m "chore(Vue插件): 发布启动恢复补丁"
```

### 任务 4：完整验证并合入 main

**文件：**
- 验证：四个插件后端、测试与发布元数据

- [ ] **步骤 1：运行 Python 编译检查**

```powershell
python -m py_compile plugins.v2\vuefarm\__init__.py plugins.v2\vuepill\__init__.py plugins.v2\vuetoy\__init__.py plugins.v2\vueemoji\__init__.py
```

预期：退出码为 0，无输出。

- [ ] **步骤 2：运行相关测试集合**

```powershell
python -m unittest tests.test_vue_startup_recovery tests.test_vue_autocatchup tests.test_vuefarm_backend tests.test_vuepill_lifecycle tests.test_vuetoy_backend tests.test_vueemoji_backend tests.test_vue_retry_limits tests.test_vuefarm_backend tests.test_vuepill_release_metadata tests.test_vuetoy_release_metadata tests.test_vueemoji_release_metadata -v
```

预期：0 个失败、0 个错误。

- [ ] **步骤 3：验证 JSON 和差异格式**

```powershell
python -c "import json; json.load(open('package.v2.json', encoding='utf-8')); print('package.v2.json OK')"
git diff --check main...HEAD
git status --short
```

预期：JSON 可解析，差异格式检查无输出，工作树没有未提交文件。

- [ ] **步骤 4：将分支提交合入主工作区**

在主工作区逐个 `cherry-pick` 本分支的新提交。如果 `package.v2.json` 与用户未提交修改冲突，保留用户修改并只合入四个 Vue 插件条目。

- [ ] **步骤 5：推送远端**

```powershell
git push origin main
```

- [ ] **步骤 6：MoviePilot 实机验证**

刷新插件市场并更新四个插件，然后通过 API 检查：

- 四个插件仍为启用状态。
- 四个主动态服务和表情挖角服务已登记下一次运行时间。
- 状态页动态时间与更新前保存的业务规则一致。
- 不主动调用收菜、搬砖、赠送、外展或挖角接口。

如需验证容器重启，只检查启动日志和任务登记，不执行真实游戏动作。
