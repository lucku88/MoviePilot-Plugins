# Vue-农场批量验证码收菜设计

## 目标

让 Vue-农场默认使用批量验证码收菜，并支持 MoviePilot 内置 OCR 或用户自建 TRWebOCR；OCR 失败后可选用 MoviePilot AI 辅助识别，全部失败后快速逐块收菜并复查，避免成熟作物长时间暴露。

## 配置

- `enable_ocr_harvest` 默认 `true`，关闭后直接逐块收菜。
- `ocr_provider` 默认 `moviepilot`，可选 `moviepilot` 或 `trwebocr`。
- MoviePilot OCR 使用 `settings.OCR_HOST` 的 `/captcha/base64` 接口，不需要填写地址。
- TRWebOCR 使用现有 `ocr_api_url` 配置。
- `use_ai_captcha` 默认 `false`，只有 OCR 失败后才调用 AI；AI 不可用时自动跳过。
- `harvest_time_budget_seconds` 默认 `45`，作为本次成熟收菜的总保护时间。

## 执行顺序

1. 成熟田出现后优先进入批量验证码收菜。
2. 批量阶段最多尝试 3 次，并受总时间限制；批量阶段必须预留逐块收菜时间。
3. OCR 全部失败后，如果打开 AI 且 MoviePilot AI 可用，再尝试 AI 验证码识别。
4. OCR 和 AI 都失败，或批量收菜后复查仍有成熟田，立即逐块收菜。
5. 逐块收菜不添加人为等待，每次请求使用剩余时间作为超时上限；结束后重新抓取田地状态复查漏收。
6. 保护时间耗尽仍有成熟田时，保留现有短重试调度，下一轮继续收菜。

## 兼容与安全

- 旧配置中启用的 TRWebOCR 地址继续保留，但新配置默认选择 MoviePilot OCR。
- 旧版关闭批量收菜的配置保持关闭，不强制改变用户已有明确选择；没有旧配置时默认开启。
- AI 验证码图片统一转换为站点完整 URL，并清理识别结果中的空格和特殊字符。
- 不自动安装或更新 OCR 容器、MoviePilot 插件或 AI 服务。

## 验证

- 测试 MoviePilot OCR 请求格式、TRWebOCR 请求格式、OCR 失败后 AI 降级、AI 失败后逐块兜底。
- 测试批量阶段受时间预算限制、逐块阶段使用剩余时间、收菜后复查漏收。
- 运行后端单元测试、Python 编译检查和 Vue 前端构建。
