# Vue-面板新增功能卡片说明

这份文档是给后续继续扩展 `plugins.v2/vuepanel` 用的。

目标是让 AI 或人工在不重做整体架构的前提下，按现有 Vue-面板 的卡片化方式继续新增功能模块。新增后的模块需要满足下面几点：

- 每个功能都是独立卡片。
- 卡片支持配置、日志、复制。
- 配置全部走前端状态页弹窗，不依赖插件配置页。
- 支持单卡启用、单卡定时、单卡通知。
- 执行结果能写入状态、日志和通知。

## 一、先理解现有结构

### 1. 主要文件

- `plugins.v2/vuepanel/__init__.py`
  作用：后端核心逻辑，负责卡片配置、调度、执行、刷新、日志记录、通知拼装。

- `plugins.v2/vuepanel/src/components/Page.vue`
  作用：前端主页面，负责卡片展示、配置弹窗、日志弹窗、复制弹窗，以及保存卡片配置。

- `plugins.v2/vuepanel/src/components/Config.vue`
  作用：插件配置页的提示页。现在这里只保留说明，不再承载真实配置逻辑。

- `plugins.v2/vuepanel/package.json`
  作用：前端包版本。

- `package.v2.json`
  作用：市场版本和更新历史。

- `plugins.v2/vuepanel/dist/`
  作用：前端构建产物。改完 `src` 后必须重新构建。

### 2. 当前已有模块

目前 `Vue-面板` 已经内置三类模块，可直接拿来参考：

- `siqi_sign`
- `hnr_claim`
- `newapi_checkin`

推荐优先参考顺序：

1. `siqi_sign`
2. `hnr_claim`
3. `newapi_checkin`

其中：

- `siqi_sign` 适合参考“普通网页签到”的实现。
- `hnr_claim` 适合参考“先读取页面，再批量执行领取”的实现。
- `newapi_checkin` 适合参考“API 接口签到 + 自定义字段 UID”的实现。

## 二、新增一个功能卡片时必须改哪些位置

### 第一步：在后端注册模块元信息

文件：

- `plugins.v2/vuepanel/__init__.py`

找到 `MODULES`，新增一个模块定义，例如：

```python
{
    "key": "your_module_key",
    "label": "功能名称",
    "icon": "🛰️",
    "description": "显示在卡片名称下面的功能说明。",
    "summary": "lowercase summary",
    "default_site_name": "默认站点名称",
    "default_site_url": "https://example.com",
    "singleton": False,
    "tone": "azure",
}
```

字段说明：

- `key`
  后端唯一模块标识，建议全小写，下划线命名。

- `label`
  默认卡片名称。

- `icon`
  卡片和日志里显示的模块图标。

- `description`
  默认说明文案，会显示在卡片标题下方，也会作为复制卡片的默认说明。

- `summary`
  英文小写摘要，主要用于卡片副标题。

- `default_site_name`
  默认站点名称。

- `default_site_url`
  默认站点地址。

- `singleton`
  当前面板统一按可复制卡片处理，保持 `False` 即可。

- `tone`
  当前主要用于模块默认色调来源，可沿用已有值，如 `azure`、`emerald`、`amber`、`rose`、`violet`、`slate`。

### 第二步：补默认说明

同文件里找到 `_default_module_note()`，给新模块补一条说明：

```python
"your_module_key": "填写 Cookie 后即可启用，执行时会调用 xxx 接口完成操作。",
```

这段说明会作为：

- 默认卡片说明
- 复制卡片说明默认值
- 部分空状态兜底说明

### 第三步：如果模块需要额外字段，先扩配置模型

当前卡片公共字段主要有：

- `id`
- `title`
- `module_key`
- `site_name`
- `site_url`
- `enabled`
- `auto_run`
- `notify`
- `cron`
- `tone`
- `cookie`
- `uid`
- `note`

如果新模块只需要这些字段，例如只要 `Cookie` 或 `Cookie + site_url`，通常不需要扩模型。

如果还需要新字段，例如：

- 用户名
- API Key
- Token
- Client ID
- 二次校验参数

那就要同时修改下面几处。

后端：

- `plugins.v2/vuepanel/__init__.py`

需要检查并修改：

- `_normalize_card()`
- `_fixed_card_template()` / `_collection_card_template()`
- `_build_dashboard()` 里卡片状态附加字段
- `_placeholder_state()` / `_result_to_state()` 如果前端日志或状态要读这个字段

前端：

- `plugins.v2/vuepanel/src/components/Page.vue`

需要检查并修改：

- `createCardDraft()`
- `normalizeCard()`
- 配置弹窗表单区域
- 复制逻辑如果要复制该字段

原则：

- 后端存什么，前端就要能编辑和回传。
- 前端新增了什么字段，`normalizeCard()` 就必须保留它。

## 三、后端执行逻辑怎么接进去

### 第一步：实现刷新方法

在 `plugins.v2/vuepanel/__init__.py` 新增一个检查当前状态的方法，命名建议：

```python
def _inspect_your_module(self, card: Dict[str, Any]) -> Dict[str, Any]:
```

这个方法用于：

- 点击“刷新状态”
- 保存配置后的状态刷新
- 首次进入状态页时拉状态

这个方法不要真的执行破坏性动作，尽量只做“读取当前状态”。

返回值必须走统一结果结构，推荐直接用：

- `_success_result(...)`
- `_warning_result(...)`
- `_info_result(...)`
- `_error_result(...)`
- 或 `_build_result(...)`

### 第二步：实现执行方法

新增真正执行任务的方法，命名建议：

```python
def _run_your_module(self, card: Dict[str, Any]) -> Dict[str, Any]:
```

这个方法用于：

- 手动点击执行
- 卡片定时自动执行
- 保存配置后勾选“立即运行一次”

### 第三步：挂到分发逻辑

在下面两个方法里都要加分支：

- `_inspect_card()`
- `_execute_card()`

示例：

```python
if module_key == "your_module_key":
    return self._inspect_your_module(card)
```

和：

```python
if module_key == "your_module_key":
    return self._run_your_module(card)
```

## 四、执行结果怎么写，前端和通知才能自动接上

### 统一返回结果结构

后端所有模块都要返回统一结构，字段核心是：

```python
{
    "success": True,
    "level": "success",
    "status_title": "签到成功",
    "status_text": "签到成功 $0.09",
    "metrics": [],
    "detail_lines": [],
    "notify_text": "签到成功 $0.09",
}
```

重点说明：

- `status_title`
  用于日志状态短标题。

- `status_text`
  用于卡片中段状态说明，也会进入日志详情。

- `detail_lines`
  用于日志页展开信息。

- `notify_text`
  用于通知文案。
  如果不想通知显示这条内容，可以返回空字符串 `""`。

### 通知规则

当前通知拼装规则已经统一，不要单独重写：

- 成功时前缀 `✅️`
- 失败时前缀 `❌️`
- 通知内容来自 `notify_text`
- 如果 `notify_text` 为空，就不会发该卡片的通知内容

所以新增模块时，要重点设计 `notify_text`：

- 有实际操作且成功：写简短结果
- 有收益：保留收益
- 没收益：不要强行加统计
- 没发生实际动作：可返回空字符串，跳过通知

示例：

```python
notify_text="今日已签到"
notify_text="领取成功 200 魔力"
notify_text="签到成功 $0.09"
notify_text=""
```

## 五、日志为什么通常不用额外写前端

因为当前 Vue-面板 已经把日志打通了：

- 执行或刷新后，后端会写 `state`
- `_append_history()` 会把记录写进 `history`
- 前端日志弹窗会从 `history` 和卡片状态里自动显示

因此新增模块时，通常只要保证以下字段有内容即可：

- `status_title`
- `status_text`
- `detail_lines`
- `level`

不要单独给日志写一套新接口，除非这个模块真的需要独立实时流式日志。

## 六、前端什么时候需要改 `Page.vue`

### 情况 A：只用现有字段

如果新模块只需要：

- Cookie
- 网站名称
- 网站地址
- Cron
- 通知开关
- 启用开关
- 功能说明

那么前端通常不用新增表单控件。

你只需要：

1. 后端 `MODULES` 增加模块
2. 后端补执行逻辑
3. 刷新状态页

卡片就会自动出现。

### 情况 B：需要新字段

比如要新增：

- `token`
- `account`
- `channel_id`

那就要改 `Page.vue`。

至少需要修改：

#### 1. `createCardDraft()`

让编辑态有这个字段。

#### 2. `normalizeCard()`

让保存时该字段不会丢。

#### 3. 配置弹窗表单

在基础设置区域新增输入框。

#### 4. 如果复制卡片也要带这个字段

确认复制逻辑用的是完整卡片对象。

当前复制逻辑基本会带上所有保留字段，但前提是 `normalizeCard()` 不能把新字段丢掉。

## 七、推荐的开发顺序

每次新增模块，推荐按这个顺序走：

1. 在 `MODULES` 里注册模块元信息。
2. 在 `_default_module_note()` 补默认说明。
3. 如果需要新字段，先改后端和前端卡片结构。
4. 实现 `_inspect_xxx()`。
5. 实现 `_run_xxx()`。
6. 在 `_inspect_card()` 和 `_execute_card()` 里挂分支。
7. 给执行结果补好 `notify_text`。
8. 进入前端检查卡片是否出现。
9. 测试：
   - 刷新状态
   - 手动执行
   - 复制卡片
   - 删除复制卡片
   - 定时执行
   - 日志显示
   - 通知文案
10. 更新版本号并构建。

## 八、版本号和构建怎么做

每次功能变更后，至少同步下面三个地方：

- `plugins.v2/vuepanel/__init__.py`
- `plugins.v2/vuepanel/package.json`
- `package.v2.json`

然后执行：

```powershell
cd "D:\01 Application\Codex\GitHub\MoviePilot-Plugins\plugins.v2\vuepanel"
npm run build
```

如果改了后端，再额外做一次语法检查：

```powershell
cd "D:\01 Application\Codex\GitHub\MoviePilot-Plugins"
python -m py_compile plugins.v2\vuepanel\__init__.py
```

## 九、让 AI 帮你新增功能卡片时，建议直接给它这段要求

可以直接把下面模板发给 AI：

```text
请修改 D:\01 Application\Codex\GitHub\MoviePilot-Plugins\plugins.v2\vuepanel

目标：给 Vue-面板 新增一个独立功能卡片

功能信息：
- module_key: your_module_key
- 卡片名称: 功能名称
- 图标: 🛰️
- 默认站点名称: 默认站点
- 默认站点地址: https://example.com
- 卡片说明: 这里写显示在卡片标题下方的说明

执行规则：
- 刷新状态时：这里写 inspect 逻辑
- 手动执行时：这里写 run 逻辑
- 定时执行时：沿用卡片 cron

配置字段：
- 需要的字段：cookie / uid / token / account / 其他字段
- 哪些是必填：xxx

通知规则：
- 成功时显示什么
- 失败时显示什么
- 没有实际动作时是否跳过通知
- 有收益时如何显示收益

实现要求：
- 按 Vue-面板 现有卡片架构扩展
- 不要恢复插件配置页
- 所有配置都走前端状态页卡片弹窗
- 卡片支持配置、日志、复制
- 结果要进入日志和通知
- 更新版本号
- 构建前端 dist
```

## 十、AI 扩展时最容易漏掉的点

下面这些点最容易忘：

- 忘记在 `MODULES` 注册，导致卡片根本不出现。
- 忘记在 `_inspect_card()` / `_execute_card()` 分发，导致点按钮没反应。
- 前端新增字段后，`normalizeCard()` 没保留，保存一次就丢。
- 只写了 `status_text`，没写 `notify_text`，结果通知过长或不符合预期。
- 改了 `src` 但没执行 `npm run build`，MoviePilot 里还是旧前端。
- 改了功能但没同步 `package.v2.json`，市场版本看起来没更新。

## 十一、推荐的验收清单

每次新增卡片后，最少要手测这些：

- 卡片能正常显示。
- 网站 logo 能显示或有回退图标。
- 配置弹窗能保存。
- 保存后卡片说明会同步更新。
- 手动刷新有状态返回。
- 手动执行有日志记录。
- 复制后的卡片能独立修改。
- 默认卡片不可删除，复制卡片可删除。
- 开启 `auto_run` 且设置 `cron` 后，调度能注册。
- 通知文案符合“精简结果”规则。

## 十二、当前设计原则

后面继续扩展时，保持下面原则不要变：

- 一个功能就是一张卡片。
- 多站点靠复制卡片解决，不再做“一个卡片塞多个站点”。
- 插件配置页不承载真实配置，只保留提示。
- 所有真实交互都在前端状态页完成。
- 主题适配、卡片风格、弹窗排版继续沿用现在的 Vue-面板。
