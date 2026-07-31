# Vue-魔丸思齐农场风格状态页实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将 Vue-魔丸状态页恢复为 Vue-思齐农场 v1.0.3 的统一卡片风格，去除技术状态文案，并修正配置页数字输入值的垂直对齐。

**架构：** 保留现有 Vue-魔丸 API、数据字段和操作函数，只改 `Page.vue` 的展示结构及主题 CSS。搬砖和沙滩合并到一张“动态任务”卡片中，内部复用思齐农场 `neu-action-card` 列表样式；数字输入框使用独立共享类修正 Vuetify 内部对齐。现有 Python 合约测试负责锁定源码结构、发布版本和构建产物。

**技术栈：** Vue 3、Vuetify 3、Vite、Python `unittest`、MoviePilot 插件市场元数据。

---

## 文件结构

- 修改：`tests/test_vuepill_frontend_contract.py`，增加思齐农场风格结构、业务状态文案和数字输入对齐合约。
- 修改：`plugins.v2/vuepill/src/components/Page.vue`，重排动态任务区并同步参考插件视觉规则。
- 修改：`plugins.v2/vuepill/src/components/Config.vue`，为数字输入统一添加垂直对齐类和 CSS。
- 修改：`tests/test_vuepill_release_metadata.py`，将发布版本及更新说明期望更新到 `0.2.6`。
- 修改：`plugins.v2/vuepill/__init__.py`、`plugins.v2/vuepill/package.json`、`plugins.v2/vuepill/package-lock.json`、`package.v2.json`、`README.md`，同步版本和发布说明。
- 重建：`plugins.v2/vuepill/dist/assets/**`，提交可直接安装的前端产物。

### 任务 1：先锁定界面合约

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`

- [ ] **步骤 1：编写状态页结构失败测试**

增加测试，要求页面包含 `schedule-board`、`schedule-action-list`、搬砖与沙滩两条 `neu-action-card`，并禁止 `dynamic-schedule-card`、`schedule-card--brick`、`schedule-card--beach` 和“后端标记”文字。

```python
def test_dynamic_tasks_use_siqifarm_interaction_card_style(self):
    self.assert_page_contains(
        'class="siqi-card schedule-board mb-3"',
        'class="schedule-action-list"',
        'neu-action-card--brick',
        'neu-action-card--beach',
        '今日已完成',
        '冷却中',
        '可以搬砖',
        '可以清理',
    )
    for forbidden in (
        'dynamic-schedule-card',
        'schedule-card--brick',
        'schedule-card--beach',
        '后端标记可执行',
        '后端标记不可执行',
    ):
        self.assertNotIn(forbidden, self.page)
```

- [ ] **步骤 2：编写参考风格和输入对齐失败测试**

断言卡片标题高度为 44px、概览卡恢复参考插件的浅色状态底板；配置页所有数字字段带 `siqi-number-input`，其输入区、输入值和前置图标统一垂直居中。

```python
def test_page_matches_siqifram_card_density(self):
    self.assertRegex(self.compact_page, r"\.siqi-card-title\{[^}]*min-height:44px")
    for tone in ("orange", "green", "blue", "red"):
        self.assertRegex(
            self.compact_page,
            rf"\.stat-{tone}\{{[^}}]*background:rgba\(",
        )

def test_numeric_config_fields_are_vertically_centered(self):
    self.assertGreaterEqual(self.config.count("siqi-number-input"), 6)
    self.assertRegex(
        self.compact_config,
        r"\.siqi-number-input:deep\(\.v-field__input\)\{[^}]*align-items:center",
    )
    self.assertRegex(
        self.compact_config,
        r"\.siqi-number-input:deep\(\.v-field__prepend-inner\)\{[^}]*align-self:center",
    )
```

- [ ] **步骤 3：运行测试并确认按预期失败**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：新增测试因旧渐变调度卡、旧技术文案和缺少 `siqi-number-input` 而失败。

### 任务 2：实现思齐农场风格状态页

**文件：**
- 修改：`plugins.v2/vuepill/src/components/Page.vue`

- [ ] **步骤 1：增加用户可读状态计算**

在现有 `brick`、`beach` 计算属性旁增加：

```javascript
const brickStatusLabel = computed(() => {
  if (brick.value.ready === true) return '可以搬砖'
  const daily = Number(brick.value.daily_bricks || 0)
  const limit = Number(brick.value.daily_limit || 0)
  if (limit > 0 && daily >= limit) return '今日已完成'
  if (brick.value.available_count === 0) return '暂无砖块'
  return '等待刷新'
})

const beachStatusLabel = computed(() => {
  if (beachActionable.value) return '可以清理'
  if (beach.value.next_ready_time || /冷却/.test(String(beach.value.status_text || ''))) return '冷却中'
  return '等待刷新'
})
```

- [ ] **步骤 2：将两块调度卡重排为一张参考风格卡**

创建带 `siqi-card-title` 的“动态任务”卡片，卡片内容使用两条 `neu-action-card`。每条包括图标、标题、真实后端说明、业务状态、关键数值和原操作按钮；保持原 `moveBricks`、`cleanBeach`、加载状态及禁用条件不变。

- [ ] **步骤 3：同步 Vue-思齐农场基础密度和主题样式**

将标题栏恢复为 `min-height:44px`；概览卡恢复参考插件的低饱和色底板；删除调度渐变 CSS，增加 `schedule-action-list`、`neu-action-card--brick`、`neu-action-card--beach`、状态文字和元数据样式。移动端让操作项改为两行布局，按钮保持可点击且不覆盖文字。

- [ ] **步骤 4：运行前端合约测试**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：状态页新增测试通过，既有 API、赠送、执行历史和移动端合约继续通过。

### 任务 3：修正配置页数字输入对齐

**文件：**
- 修改：`plugins.v2/vuepill/src/components/Config.vue`

- [ ] **步骤 1：给六个数字输入增加共享类**

在 `schedule_buffer_seconds`、`reserve_magic_pill_count`、`random_delay_max_seconds`、`http_timeout`、`http_retry_times`、`http_retry_delay` 的 `class` 中加入 `siqi-number-input`。

- [ ] **步骤 2：添加 Vuetify 内部对齐规则**

```css
.siqi-number-input :deep(.v-field__input){min-height:44px;align-items:center;padding-top:8px;padding-bottom:8px}
.siqi-number-input :deep(input){align-self:center;line-height:24px}
.siqi-number-input :deep(.v-field__prepend-inner){align-self:center;padding-top:0}
```

- [ ] **步骤 3：运行配置页合约测试**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：数字字段对齐测试和既有配置校验、Cookie 自动同步测试全部通过。

### 任务 4：发布 `0.2.6`

**文件：**
- 修改：`tests/test_vuepill_release_metadata.py`
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`plugins.v2/vuepill/package.json`
- 修改：`plugins.v2/vuepill/package-lock.json`
- 修改：`package.v2.json`
- 修改：`README.md`

- [ ] **步骤 1：先更新发布元数据测试**

将 `EXPECTED_VERSION` 改为 `0.2.6`，新增 `EXPECTED_HISTORY_V026`，并把历史键首项改为 `v0.2.6`。更新说明明确包含“状态页直接对齐 Vue-思齐农场 v1.0.3”“去除后端标记文案”“数字输入垂直居中”“保留配置和动态调度”。

- [ ] **步骤 2：运行发布测试并确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_release_metadata.VuePillReleaseMetadataTest.test_release_versions_are_consistently_v025 tests.test_vuepill_release_metadata.VuePillReleaseMetadataTest.test_market_history_and_readme_describe_the_v025_release -v
```

预期：源码和市场仍为 `0.2.5`，测试失败。

- [ ] **步骤 3：同步所有版本和说明**

将后端、两个 npm 元数据和市场版本更新到 `0.2.6`；`package.v2.json` 历史首项增加对应说明；README 表格和 Vue-魔丸说明首项更新到 `v0.2.6`。小版本升级不清除任何配置。

### 任务 5：构建与完整验证

**文件：**
- 重建：`plugins.v2/vuepill/dist/assets/**`

- [ ] **步骤 1：安装锁定依赖并构建**

运行：

```powershell
npm ci
npm run build
```

工作目录：`plugins.v2/vuepill`

预期：Vite 构建成功，生成新的 Page、Config 和 `remoteEntry.js` 引用。

- [ ] **步骤 2：运行后端编译和 Vue-魔丸测试**

运行：

```powershell
python -m py_compile plugins.v2\vuepill\__init__.py plugins.v2\vuepill\page_parser.py plugins.v2\vuepill\site_client.py plugins.v2\vuepill\crafting.py
python -m unittest tests.test_vuepill_frontend_contract tests.test_vuepill_release_metadata tests.test_vuepill_parser tests.test_vuepill_client tests.test_vuepill_crafting tests.test_vuepill_business_flows tests.test_vuepill_lifecycle -v
```

预期：全部通过。

- [ ] **步骤 3：运行发布完整性和差异检查**

运行：

```powershell
python -c "import json; json.load(open('package.v2.json', encoding='utf-8')); print('package.v2.json OK')"
git diff --check
git status --short
```

预期：JSON 可解析、无空白错误，变更只包含 Vue-魔丸源码、测试、版本元数据、构建产物和本计划。

- [ ] **步骤 4：提交并推送**

```powershell
git add -- plugins.v2/vuepill tests/test_vuepill_frontend_contract.py tests/test_vuepill_release_metadata.py package.v2.json README.md docs/superpowers/plans/2026-08-01-vuepill-siqifarm-status.md
git commit -m "fix(Vue-魔丸): 对齐思齐农场状态页风格"
git push origin main
```

预期：`origin/main` 更新到新提交，用户刷新插件市场后可看到 `v0.2.6` 更新按钮。
