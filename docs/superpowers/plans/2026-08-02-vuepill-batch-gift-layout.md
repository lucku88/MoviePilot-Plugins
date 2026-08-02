# Vue-魔丸批量赠送与资源区布局实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 精简兑换区说明，让物品栏和炼造工坊各占整行，并增加经过后端完整校验的批量赠送功能。

**架构：** 前端新增批量赠送弹窗和独立请求保护，后端新增一次预检、顺序提交、一次最终刷新的批量接口。现有单件赠送接口保持兼容，资源区只调整布局和响应式规则。

**技术栈：** Vue 3、Vuetify、Python、MoviePilot 插件 API、`unittest`、Vite。

---

### 任务 1：建立失败的后端批量赠送测试

**文件：**
- 修改：`tests/test_vuepill_lifecycle.py`
- 修改：`tests/test_vuepill_business_flows.py`

- [ ] 增加 `/gift-items` 路由契约测试和负载校验测试，断言重复物品、空数组、超过 20 项、非正整数及库存不足均在任何网站请求前失败。
- [ ] 增加全部成功测试，断言网站按请求顺序收到每个 `gift_item`，只刷新一次最终状态，并生成一条合并历史。
- [ ] 增加部分成功测试，断言第二项失败后第三项不会发送，响应包含 `partial: true` 和已成功项目。
- [ ] 运行：`python -m unittest tests.test_vuepill_lifecycle tests.test_vuepill_business_flows -v`，预期新增测试因 `/gift-items` 尚不存在而失败。

### 任务 2：实现后端批量赠送接口

**文件：**
- 修改：`plugins.v2/vuepill/__init__.py`

- [ ] 注册 `POST /gift-items` 路由。
- [ ] 实现 `_validate_gift_items_payload()`，返回规范化 UID 和不重复的物品列表。
- [ ] 实现批量预检，复用现有库存、可赠送状态和单项 500 上限。
- [ ] 顺序发送不可重试的 `gift_item`，处理中途失败、一次最终刷新和合并历史。
- [ ] 运行任务 1 的测试，预期全部通过。

### 任务 3：建立失败的前端布局与交互契约测试

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`

- [ ] 断言页面不再包含两句兑换说明和 `exchangeReserveHint`。
- [ ] 断言 `.resource-grid` 为单列，物品栏和炼造工坊各占整行，配方桌面双列、手机单列。
- [ ] 断言存在“批量赠送”按钮、批量弹窗、勾选项、数量输入、二次确认、独立请求保护和 `/gift-items` 请求。
- [ ] 运行：`python -m unittest tests.test_vuepill_frontend_contract -v`，预期因界面尚未实现而失败。

### 任务 4：实现前端批量赠送与布局

**文件：**
- 修改：`plugins.v2/vuepill/src/components/Page.vue`

- [ ] 删除兑换输入框提示和后端说明区。
- [ ] 将资源区外层改为单列，恢复全宽物品栏自动多列和工坊双列布局。
- [ ] 在物品栏标题加入批量赠送按钮，并实现共用 UID、逐项选择和数量输入的弹窗。
- [ ] 增加二次确认快照、异步请求保护、部分成功提示和安全关闭逻辑。
- [ ] 补充桌面、900px 和 600px 响应式样式。
- [ ] 运行任务 3 的测试，预期全部通过。

### 任务 5：同步版本和发布说明

**文件：**
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`plugins.v2/vuepill/package.json`
- 修改：`plugins.v2/vuepill/package-lock.json`
- 修改：`package.v2.json`
- 修改：`README.md`
- 修改：`tests/test_vuepill_release_metadata.py`

- [ ] 将版本统一升级为 `0.2.9`。
- [ ] 更新市场历史和 README，说明资源区整行布局和批量赠送。
- [ ] 更新发布测试中的版本断言。

### 任务 6：构建、验证和发布

**文件：**
- 更新：`plugins.v2/vuepill/dist/**`

- [ ] 运行：`python -m py_compile plugins.v2\vuepill\__init__.py`。
- [ ] 运行：`python -m unittest discover -s tests -p 'test_vuepill*.py' -v`。
- [ ] 运行前端构建并确认发布测试逐字节匹配。
- [ ] 在 MoviePilot 浅色、深色、桌面和 390px 宽度下检查布局与弹窗。
- [ ] 使用最小数量真实测试一次批量赠送，确认历史和状态刷新。
- [ ] 提交并推送 `main`，刷新插件市场后更新 MoviePilot 到 `0.2.9`。
