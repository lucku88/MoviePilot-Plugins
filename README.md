# MoviePilot-Plugins

个人 MoviePilot 插件仓库，目前仅保留 `SQFarm`。

仓库地址：

- `https://github.com/lucku88/MoviePilot-Plugins/`

## 插件列表

- `SQFarm`
  - SQ种菜插件
  - 自动收菜、识别验证码、售出背包作物并补种

## 仓库结构

```text
plugins.v2/
  sqfarm/
package.v2.json
```

## 使用说明

在 MoviePilot 的自定义插件仓库中填入：

- `https://github.com/lucku88/MoviePilot-Plugins/`

然后安装 `SQFarm` 插件。

插件需要配置：

- `Cookie`
- `OCR API 地址`

## 开发说明

插件主文件：

- `plugins.v2/sqfarm/__init__.py`
