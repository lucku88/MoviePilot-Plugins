# Vue-魔丸任务优先状态页实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将 Vue-魔丸状态页实现为已确认的任务优先工作台，并发布 `v0.2.7`，同时保留全部后端业务、配置、Cookie、执行历史和动态调度计划。

**架构：** 后端 `/status` 不变；前端安全解析现有根级调度字段，并在页头生成自动运行摘要。页面继续使用一个 `Page.vue`，但将自动任务、物品和配方分别使用清晰的 CSS Grid；状态提取仍集中在 `asyncGuards.js`，所有普通刷新和手动操作共用同一回填路径。

**技术栈：** Python 3 `unittest`、Vue 3、Vuetify 3、Vite 4、Node.js、MoviePilot 插件 API、Playwright CLI。

---

## 文件职责

- 修改 `plugins.v2/vuepill/src/utils/asyncGuards.js`：从直接或嵌套状态响应中安全提取调度摘要字段。
- 修改 `plugins.v2/vuepill/src/components/Page.vue`：接收调度字段，重排状态页并实现响应式样式。
- 修改 `tests/test_vuepill_frontend_contract.py`：覆盖状态字段回填、布局顺序、网格列数、手机规则和旧功能保护。
- 修改 `tests/test_vuepill_release_metadata.py`：将发布契约升级到 `v0.2.7`。
- 修改 `plugins.v2/vuepill/__init__.py`、`plugins.v2/vuepill/package.json`、`plugins.v2/vuepill/package-lock.json`：同步版本号。
- 修改 `package.v2.json`、`README.md`：更新插件市场和用户可见更新说明。
- 更新 `plugins.v2/vuepill/dist/**`：提交由 Vite 生成的前端产物。

## 任务 1：安全保留状态响应中的调度字段

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/utils/asyncGuards.js`

- [ ] **步骤 1：添加失败的调度字段提取测试**

在 `VuePillFrontendContractTest` 中新增测试，使用完整的最小 `pill_status`，验证直接 `/status` 响应和动作接口嵌套 `status` 响应都能返回 `statusMeta`：

```python
def test_status_payload_keeps_scheduler_metadata(self):
    script = f"""
import assert from 'node:assert/strict'
import {{ extractStatusPayload }} from {ASYNC_GUARD_PATH.as_uri()!r}

const pillStatus = {{
  overview: [],
  brick: {{}},
  beach: {{}},
  exchange: {{}},
  inventory: {{ items: [] }},
  recipes: [],
  history: [],
}}
const direct = extractStatusPayload({{
  enabled: true,
  next_run_time: '2026-08-02 11:26:58',
  next_trigger_time: '2026-08-02 11:25:58',
  next_trigger_action: '清沙滩',
  pill_status: pillStatus,
  history: [],
}})
assert.deepEqual(direct.statusMeta, {{
  enabled: true,
  next_run_time: '2026-08-02 11:26:58',
  next_trigger_time: '2026-08-02 11:25:58',
  next_trigger_action: '清沙滩',
}})

const nested = extractStatusPayload({{
  pill_status: pillStatus,
  status: {{
    enabled: false,
    next_run_time: '',
    next_trigger_time: '',
    next_trigger_action: '',
    pill_status: pillStatus,
    history: [],
  }},
}})
assert.deepEqual(nested.statusMeta, {{
  enabled: false,
  next_run_time: '',
  next_trigger_time: '',
  next_trigger_action: '',
}})
assert.deepEqual(
  extractStatusPayload({{ pill_status: pillStatus }}).statusMeta,
  {{}},
)
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    self.assertEqual(0, result.returncode, result.stderr or result.stdout)
```

同时把现有 `extractStatusPayload()` 深度相等断言补上 `statusMeta: {}`，使返回结构固定。

- [ ] **步骤 2：运行单测并确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract.VuePillFrontendContractTest.test_status_payload_keeps_scheduler_metadata -v
```

预期：`FAIL`，错误说明 `statusMeta` 为 `undefined`。

- [ ] **步骤 3：实现安全的元数据提取**

在 `asyncGuards.js` 中增加白名单和提取函数。嵌套 `status` 优先，直接响应只补充嵌套状态没有的字段；无效类型和访问器属性被忽略：

```javascript
const STATUS_META_RULES = Object.freeze({
  enabled: value => typeof value === 'boolean',
  next_run_time: value => typeof value === 'string',
  next_trigger_time: value => typeof value === 'string',
  next_trigger_action: value => typeof value === 'string',
})

function extractStatusMeta(response, nestedStatus) {
  const meta = {}
  for (const source of [nestedStatus, response]) {
    if (!source) continue
    for (const [key, isValid] of Object.entries(STATUS_META_RULES)) {
      if (Object.prototype.hasOwnProperty.call(meta, key)) continue
      const value = ownDataValue(source, key)
      if (value !== MISSING && isValid(value)) meta[key] = value
    }
  }
  return meta
}
```

将 `extractStatusPayload()` 的返回值改为：

```javascript
return {
  pillStatus,
  history,
  statusMeta: extractStatusMeta(response, nestedStatus),
}
```

- [ ] **步骤 4：运行状态提取和完整前端契约测试**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：全部 `OK`。

- [ ] **步骤 5：提交调度字段提取**

```powershell
git add plugins.v2/vuepill/src/utils/asyncGuards.js tests/test_vuepill_frontend_contract.py
git commit -m "feat(Vue-魔丸): 保留状态调度摘要字段"
```

## 任务 2：实现页头自动运行摘要和双列任务卡

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/components/Page.vue`

- [ ] **步骤 1：添加失败的页头与任务布局契约**

新增测试：

```python
def test_task_first_header_and_schedule_grid(self):
    self.assert_page_contains(
        'class="schedule-summary"',
        "scheduleSummary",
        "next_trigger_time",
        "next_trigger_action",
        "Object.assign(status, update.statusMeta || {})",
        "自动运行正常",
        "等待识别下一次任务",
    )
    self.assertRegex(
        self.compact_page,
        r"\.schedule-action-list\{[^}]*display:grid[^}]*grid-template-columns:repeat\(2,minmax\(0,1fr\)\)",
    )
    self.assertRegex(
        self.compact_page,
        r"@media\(max-width:700px\)\{.*?\.schedule-action-list\{[^}]*grid-template-columns:1fr",
    )
```

更新 `test_status_sections_follow_required_order`，保留顺序：顶部栏、概览、动态任务、兑换、物品、炼造、历史。

- [ ] **步骤 2：运行新测试并确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract.VuePillFrontendContractTest.test_task_first_header_and_schedule_grid -v
```

预期：`FAIL`，页面尚无 `schedule-summary`，任务仍为单列。

- [ ] **步骤 3：扩展页面状态容器和统一回填**

将状态容器扩展为：

```javascript
const status = reactive({
  enabled: false,
  next_run_time: '',
  next_trigger_time: '',
  next_trigger_action: '',
  pill_status: {},
  history: [],
})
```

在 `applyStatusPayload()` 中先保留根级字段，再更新业务状态：

```javascript
Object.assign(status, update.statusMeta || {})
status.pill_status = update.pillStatus
if (update.history) status.history = update.history
```

增加时间压缩和摘要计算：

```javascript
function compactScheduleTime(value) {
  const text = String(value || '').trim()
  const matched = text.match(/^\d{4}-(\d{2})-(\d{2})\s+(\d{2}:\d{2})/)
  return matched ? `${matched[1]}-${matched[2]} ${matched[3]}` : text
}

const scheduleSummary = computed(() => {
  if (!status.enabled) return { active: false, text: '自动运行未启用' }
  const nextTime = status.next_trigger_time || status.next_run_time
  if (!nextTime) return { active: false, text: '等待识别下一次任务' }
  const action = status.next_trigger_action || '任务'
  return {
    active: true,
    text: `自动运行正常 · 下一项：${action} ${compactScheduleTime(nextTime)}`,
  }
})
```

- [ ] **步骤 4：在页头渲染摘要**

将摘要放在操作按钮组之前：

```vue
<div
  class="schedule-summary"
  :class="{ 'schedule-summary--active': scheduleSummary.active }"
>
  <v-icon
    :icon="scheduleSummary.active ? 'mdi-check-circle-outline' : 'mdi-clock-outline'"
    size="15"
  />
  <span>{{ scheduleSummary.text }}</span>
</div>
```

摘要只在桌面端显示；手机端通过 CSS 隐藏，按钮和标题保持现有行为。

- [ ] **步骤 5：将搬砖和沙滩改为双列任务卡**

保留现有判断和请求函数，只调整卡片按钮文案：

```vue
{{ brick.ready === true ? '立即搬砖' : brickStatusLabel }}
```

```vue
{{ beachActionable ? '清理沙滩' : beachStatusLabel }}
```

核心 CSS：

```css
.schedule-action-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.neu-action-card{grid-template-columns:32px minmax(0,1fr);align-items:start}
.schedule-action{grid-column:1/-1;width:100%}
.schedule-summary{display:inline-flex;align-items:center;gap:6px;max-width:360px;padding:7px 10px;border-radius:10px;background:rgba(var(--v-theme-on-surface),.05);color:rgba(var(--v-theme-on-surface),.56);font-size:11px;font-weight:700;white-space:nowrap}
.schedule-summary--active{background:rgba(34,197,94,.11);color:#22c55e}
@media(max-width:700px){.schedule-action-list{grid-template-columns:1fr}.schedule-summary{display:none}}
```

- [ ] **步骤 6：运行前端契约测试**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：全部 `OK`，搬砖、沙滩的可执行判断测试仍通过。

- [ ] **步骤 7：提交任务优先首屏**

```powershell
git add plugins.v2/vuepill/src/components/Page.vue tests/test_vuepill_frontend_contract.py
git commit -m "style(Vue-魔丸): 重排任务优先首屏"
```

## 任务 3：将物品栏和炼造工坊改为全宽网格

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/components/Page.vue`

- [ ] **步骤 1：添加失败的资源网格测试**

新增测试：

```python
def test_inventory_and_workshop_use_full_width_compact_grids(self):
    self.assertRegex(
        self.compact_page,
        r"\.resource-grid\{[^}]*grid-template-columns:1fr",
    )
    self.assertRegex(
        self.compact_page,
        r"\.inventory-grid\{[^}]*grid-template-columns:repeat\(7,minmax\(0,1fr\)\)",
    )
    self.assertRegex(
        self.compact_page,
        r"\.recipe-grid\{[^}]*grid-template-columns:repeat\(3,minmax\(0,1fr\)\)",
    )
    self.assert_page_contains(
        "inventoryCounts",
        "ingredientCount",
        "ingredientEnough",
        "gift-item--static",
        'v-if="canGiftItem(item)"',
    )
```

保留现有测试：零上限不显示、材料不足文案不重复显示、兑换和炼造数量以后端上限为准。

- [ ] **步骤 2：运行新测试并确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract.VuePillFrontendContractTest.test_inventory_and_workshop_use_full_width_compact_grids -v
```

预期：`FAIL`，当前物品和炼造仍左右并排且物品是长条列表。

- [ ] **步骤 3：计算材料拥有量**

在 `inventoryItems` 后增加：

```javascript
const inventoryCounts = computed(() => {
  const counts = new Map()
  inventoryItems.value.forEach((item) => {
    const name = String(item?.name || '').trim()
    if (name) counts.set(name, Math.max(0, Number(item?.count || 0)))
  })
  return counts
})

function ingredientCount(name) {
  return inventoryCounts.value.get(String(name || '').trim()) || 0
}

function ingredientEnough(name, required) {
  return ingredientCount(name) >= Math.max(0, Number(required || 0))
}
```

- [ ] **步骤 4：压缩物品卡并隐藏重复的不可赠送文字**

物品按钮保留原有点击、禁用和无障碍标签，只调整 class 和状态文字：

```vue
:class="{
  'gift-item--available': canGiftItem(item),
  'gift-item--static': !canGiftItem(item),
}"
```

```vue
<span v-if="canGiftItem(item)" class="gift-item__state">赠送</span>
```

不要删除 `:disabled="!canGiftItem(item)"` 和现有 `aria-label`，避免不可赠送物品误触发接口。

- [ ] **步骤 5：在配方材料中显示拥有量/需求量**

将材料标签改为：

```vue
<span
  v-for="(required, name) in recipe.ingredients || {}"
  :key="`${recipe.craft_id}-${name}`"
  :class="{ 'ingredient-ready': ingredientEnough(name, required) }"
>
  {{ name }} {{ ingredientCount(name) }}/{{ required }}
</span>
```

继续保留：

```vue
<template v-if="Number(recipe.max_count || 0) > 0"> · 最多 {{ recipe.max_count }}</template>
```

最大值为 `0` 时不新增任何“材料不足”或“上限为 0”文案。

- [ ] **步骤 6：实现桌面和响应式网格**

核心 CSS：

```css
.resource-grid{display:grid;grid-template-columns:1fr;gap:12px}
.inventory-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px}
.gift-item{min-height:96px;display:flex;flex-direction:column;justify-content:center;gap:4px;text-align:center}
.gift-item:disabled{cursor:default;opacity:1}
.gift-item__state{color:#f59e0b;font-size:10px;font-weight:800}
.recipe-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.recipe-ingredients .ingredient-ready{background:rgba(34,197,94,.10);color:#22c55e}
@media(max-width:1100px){.inventory-grid{grid-template-columns:repeat(5,minmax(0,1fr))}.recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.inventory-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.recipe-grid{grid-template-columns:1fr}}
```

- [ ] **步骤 7：运行前端契约测试**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：全部 `OK`；赠送确认、赠礼统计、后端上限和历史格式测试均不回归。

- [ ] **步骤 8：提交资源工作区布局**

```powershell
git add plugins.v2/vuepill/src/components/Page.vue tests/test_vuepill_frontend_contract.py
git commit -m "style(Vue-魔丸): 收紧物品与炼造网格"
```

## 任务 4：补齐骨架屏、主题和手机布局保护

**文件：**
- 修改：`tests/test_vuepill_frontend_contract.py`
- 修改：`plugins.v2/vuepill/src/components/Page.vue`

- [ ] **步骤 1：添加失败的响应式和视觉噪音测试**

扩展现有移动端测试：

```python
def test_task_first_layout_has_mobile_and_theme_guards(self):
    self.assert_page_contains(
        "@media(max-width:1100px)",
        "@media(max-width:700px)",
        "overflow-x:hidden",
        "rgba(var(--v-theme-on-surface)",
        "rgba(var(--v-theme-surface)",
    )
    self.assertNotIn("当前不可赠送</span>", self.page)
    self.assertNotIn("后端上限", self.page)
    self.assertNotIn("后端返回最大可炼造数量为 0", self.page)
```

把兑换概览测试更新为要求“最多兑换”，同时继续断言使用 `exchange.max_count`。

- [ ] **步骤 2：运行新增测试并确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract.VuePillFrontendContractTest.test_task_first_layout_has_mobile_and_theme_guards -v
```

预期：`FAIL`，页面仍包含“后端上限”，且骨架与新网格未完全一致。

- [ ] **步骤 3：同步骨架屏结构和中性主题**

- 概览骨架继续为四项。
- 第一操作区骨架使用任务双卡和兑换卡。
- 物品骨架使用 7 格，配方骨架使用 3 格。
- 概览卡主体改为主题表面色，颜色集中在左侧细线、图标和数字。
- 区块标题只保留轻微主题色，不使用固定深色或固定白色背景。

兑换第三项标题改为：

```vue
<div class="exchange-stat"><span>最多兑换</span><strong>{{ exchange.max_count ?? 0 }}</strong><small>颗</small></div>
```

- [ ] **步骤 4：收紧手机端规则**

在 `@media(max-width:700px)` 中保证：

```css
.overview-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.primary-grid{grid-template-columns:1fr}
.schedule-action-list{grid-template-columns:1fr}
.inventory-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.recipe-grid{grid-template-columns:1fr}
.schedule-summary{display:none}
```

保留 `@media(max-width:600px)` 中现有顶部按钮、对话框和历史时间细节，确保现有测试和 MoviePilot 窄弹窗兼容。

- [ ] **步骤 5：运行前端契约测试和 Vue 构建**

运行：

```powershell
python -m unittest tests.test_vuepill_frontend_contract -v
```

预期：全部 `OK`。

运行：

```powershell
npm run build
```

工作目录：`plugins.v2/vuepill`

预期：Vite 构建成功，无 Vue 模板或 CSS 编译错误。

- [ ] **步骤 6：提交响应式收尾和当前构建产物**

```powershell
git add plugins.v2/vuepill/src/components/Page.vue tests/test_vuepill_frontend_contract.py plugins.v2/vuepill/dist
git commit -m "style(Vue-魔丸): 完善多主题与手机布局"
```

## 任务 5：发布 Vue-魔丸 v0.2.7

**文件：**
- 修改：`tests/test_vuepill_release_metadata.py`
- 修改：`plugins.v2/vuepill/__init__.py`
- 修改：`plugins.v2/vuepill/package.json`
- 修改：`plugins.v2/vuepill/package-lock.json`
- 修改：`package.v2.json`
- 修改：`README.md`
- 更新：`plugins.v2/vuepill/dist/**`

- [ ] **步骤 1：先把发布测试升级为 v0.2.7**

将版本常量改为：

```python
EXPECTED_VERSION = "0.2.7"
```

增加固定历史文案：

```python
EXPECTED_HISTORY_V027 = (
    "状态页改为任务优先工作台：第一屏集中显示自动任务、下一触发动作和兑换；"
    "物品栏改为全宽紧凑网格，炼造工坊改为三列配方布局，并继续适配浅色、深色和手机页面。"
    "v0.2.x 小版本升级保留现有配置、Cookie、执行历史和动态调度计划。"
)
```

把 `"v0.2.7"` 放在 `EXPECTED_HISTORY_KEYS` 首位，测试方法名改为 `test_release_versions_are_consistently_v027` 和 `test_market_history_and_readme_describe_the_v027_release`，并断言 README 包含：

```python
"| `Vue-魔丸` | `v0.2.7` |"
"任务优先工作台"
"物品栏改为全宽紧凑网格"
"炼造工坊改为三列配方布局"
```

- [ ] **步骤 2：运行发布测试并确认失败**

运行：

```powershell
python -m unittest tests.test_vuepill_release_metadata.VuePillReleaseMetadataTest.test_release_versions_are_consistently_v027 tests.test_vuepill_release_metadata.VuePillReleaseMetadataTest.test_market_history_and_readme_describe_the_v027_release -v
```

预期：`FAIL`，当前源码和市场索引仍为 `0.2.6`。

- [ ] **步骤 3：同步所有版本和市场说明**

修改为 `0.2.7`：

```python
plugin_version = "0.2.7"
```

```json
"version": "0.2.7"
```

`package-lock.json` 顶层和 `packages[""]` 两处版本同时更新。`package.v2.json` 的 `VuePill.version` 更新为 `0.2.7`，并在历史首位加入与测试完全一致的 `v0.2.7` 文案。README 表格和 Vue-魔丸章节同步更新。

- [ ] **步骤 4：重新构建最终 dist**

运行：

```powershell
npm run build
```

工作目录：`plugins.v2/vuepill`

预期：构建成功，`dist/assets/assets/remoteEntry.js` 和带哈希的 Page 资源更新。

- [ ] **步骤 5：运行发布契约测试**

运行：

```powershell
python -m unittest tests.test_vuepill_release_metadata -v
```

预期：全部 `OK`，包括临时目录 clean build 与已提交 `dist` 字节一致检查。

- [ ] **步骤 6：提交 v0.2.7 发布**

```powershell
git add plugins.v2/vuepill/__init__.py plugins.v2/vuepill/package.json plugins.v2/vuepill/package-lock.json plugins.v2/vuepill/dist package.v2.json README.md tests/test_vuepill_release_metadata.py
git commit -m "chore(Vue-魔丸): 发布 v0.2.7"
```

## 任务 6：完整回归、真实浏览器验收与推送

**文件：**
- 验证：`plugins.v2/vuepill/**`
- 验证：`tests/test_vuepill_*.py`
- 验证：`tests/test_vue_autocatchup.py`
- 验证：`tests/test_vue_retry_limits.py`

- [ ] **步骤 1：运行 Python 编译检查**

```powershell
python -m py_compile plugins.v2/vuepill/__init__.py plugins.v2/vuepill/page_parser.py plugins.v2/vuepill/site_client.py plugins.v2/vuepill/crafting.py
```

预期：无输出，退出码 `0`。

- [ ] **步骤 2：运行 Vue-魔丸完整测试集**

```powershell
python -m unittest tests.test_vuepill_parser tests.test_vuepill_client tests.test_vuepill_crafting tests.test_vuepill_business_flows tests.test_vuepill_lifecycle tests.test_vuepill_frontend_contract tests.test_vuepill_release_metadata tests.test_vue_autocatchup tests.test_vue_retry_limits -v
```

预期：全部 `OK`。

- [ ] **步骤 3：检查 JSON、差异和工作树范围**

```powershell
python -c "import json; json.load(open('package.v2.json', encoding='utf-8')); print('package.v2.json OK')"
```

```powershell
git diff --check
```

```powershell
git status --short
```

预期：JSON 可解析；`git diff --check` 无输出；已提交改动仅属于设计文档、实现计划和 Vue-魔丸发布，不暂存 `.playwright-cli/`、`.superpowers/`、`output/` 或其他既有未跟踪文件。

- [ ] **步骤 4：在测试谷歌浏览器中验收桌面和手机**

更新 MoviePilot 中的 Vue-魔丸后，在现有 `vuetoy` Playwright 会话打开插件状态页。分别设置：

```powershell
npx --yes --package @playwright/cli playwright-cli -s=vuetoy resize 1440 1000
```

```powershell
npx --yes --package @playwright/cli playwright-cli -s=vuetoy resize 390 844
```

每次尺寸变化后执行 `snapshot` 和 `screenshot`。验收：

- 桌面首屏同时看到四项概览、双列搬砖/沙滩和兑换。
- 物品栏宽屏为 7 列，炼造为 3 列。
- 手机为两列概览、单列任务、三列物品、单列炼造，无横向滚动。
- 浅色和深色 MoviePilot 主题下文字、边框、按钮均清晰。
- 刷新、兑换数量校验、赠送弹窗、赠礼统计、炼造禁用状态和历史时间显示正常。

- [ ] **步骤 5：推送 main**

```powershell
git push origin main
```

预期：推送成功，远端 `main` 包含 `v0.2.7` 发布提交。
