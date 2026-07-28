# Vue-魔丸旧版升级重启门实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 让 `Vue-魔丸 v0.1.x` 首次热更新到 `v0.2.0` 时先等待 MoviePilot 重启，重启后再安全完成一次性重置，杜绝旧版在途任务晚写回。

**架构：** 插件模块在 `sys` 上保存仅当前 MoviePilot 进程有效的随机标识，并在插件数据中保存首次升级的来源进程标识。相同标识表示仍处于原热更新进程，只写安全默认配置并保持停用；标识变化表示 MoviePilot 已重启，此时才执行最终数据重置并写入配置代号 `2`。配置 API 只公开布尔状态，前端按状态显示条件提示，不暴露内部标识。

**技术栈：** Python、`unittest`、Vue 3、Vuetify、Vite、MoviePilot 插件 API。

---

### 任务 1：后端两阶段升级状态机

**文件：**
- 修改：`tests/test_vuepill_lifecycle.py`
- 修改：`plugins.v2/vuepill/__init__.py`

- [ ] **步骤 1：编写首次热更新失败测试**

新增测试模拟没有配置代号、没有旧迁移标记但存在旧配置和历史的 `v0.1.x`：第一次初始化后断言插件写入安全默认配置并保持关闭，旧历史和计划仍存在，配置代号仍为空，等待重启标记等于当前进程标识。

- [ ] **步骤 2：运行测试确认旧实现会提前重置**

运行：`python -m unittest tests.test_vuepill_lifecycle.VuePillLifecycleTests.test_legacy_upgrade_waits_for_restart_before_final_reset -v`

预期：FAIL，旧实现已经清空历史并写入配置代号 `2`。

- [ ] **步骤 3：实现等待重启状态**

在后端新增进程级稳定标识和私有等待键；将旧版首次升级模式拆成 `legacy-restart-prepare`、`legacy-restart-pending`、`legacy-restart-finalize`。准备和等待阶段统一应用安全默认配置、停止调度并返回，不清运行数据、不写配置代号。

- [ ] **步骤 4：编写并验证重启后最终重置测试**

新增测试让等待标记与当前进程标识不同，断言初始化会清空旧历史、状态和计划，写入配置代号 `2`、旧兼容标记，并清除等待标记。另加同进程重复初始化不注册 scheduler、不改变旧数据的测试。

- [ ] **步骤 5：保护配置保存与公开字段**

等待重启时 `_save_config()` 返回失败和明确提示；`_get_config()` 仅在公开读取时增加 `upgrade_restart_required: true`，持久化配置载荷不得包含该字段，也不得暴露进程标识。

- [ ] **步骤 6：运行后端测试并提交**

运行：

```powershell
python -m unittest tests.test_vuepill_lifecycle -v
python -m unittest tests.test_vue_autocatchup -v
python -m unittest tests.test_vue_retry_limits -v
python -m py_compile plugins.v2\vuepill\__init__.py
git diff --check
```

提交：`fix(Vue-魔丸): 首次升级重启后再完成重置`

### 任务 2：配置页条件提示与发布说明

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/components/Config.vue`
- 修改：`plugins.v2/vuepill/dist/**`
- 修改：`tests/test_vuepill_release_metadata.py`
- 修改：`README.md`
- 修改：`package.v2.json`

- [ ] **步骤 1：编写前端条件提示失败测试**

断言配置页读取只读字段 `upgrade_restart_required`，仅在其为 `true` 时显示“请重启 MoviePilot 完成 Vue-魔丸 v0.2.0 升级”，同时禁用保存和表单；字段不得进入 `CONFIG_FIELDS` 或保存载荷。

- [ ] **步骤 2：运行测试确认条件提示尚不存在**

运行：`python -m unittest tests.test_vuepill_frontend_contract -v`

预期：FAIL，源码尚未读取升级状态或显示提示。

- [ ] **步骤 3：实现最小前端提示并构建**

在 `Config.vue` 增加独立 `upgradeRestartRequired` 状态，`applyPublicConfig()` 读取后端布尔值；模板显示条件 `v-alert`，保存按钮和字段集在等待状态禁用。不要把该字段加入可保存白名单或默认配置。

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
npm run build
```

工作目录：`plugins.v2/vuepill`。

- [ ] **步骤 4：同步 README、市场说明和发布测试**

保持版本 `0.2.0`，说明首次从 `v0.1.x` 更新后需重启一次 MoviePilot，重启后完成重置；后续 `v0.2.x` 小更新继续保留配置、历史和计划。

- [ ] **步骤 5：运行发布测试并提交**

运行：`python -m unittest tests.test_vuepill_release_metadata -v`

提交：`docs(Vue-魔丸): 说明首次升级重启流程`

### 任务 3：最终复审与验证

**文件：**
- 验证：`plugins.v2/vuepill/**`
- 验证：`tests/test_vuepill_*.py`

- [ ] **步骤 1：请求独立代码审查**

重点审查真实 `v0.1.x` 热更新晚写回、等待标记原子性、同进程重复初始化、重启后失败重试和只读字段泄露。

- [ ] **步骤 2：分进程运行全部九个测试模块**

按原计划分别运行 `tests.test_vue_autocatchup`、`tests.test_vue_retry_limits`、七个 `tests.test_vuepill_*` 模块，避免全局替身污染。

- [ ] **步骤 3：验证版本、残留字段和工作区**

确认三处版本仍为 `0.2.0`，源码和 `dist` 不含 `force_ipv4`，`git diff --check main...HEAD` 无输出，工作区干净。

- [ ] **步骤 4：停止在本地功能分支**

不安装、不更新 MoviePilot、不推送 `main`，等待用户确认后续合并和发布。
