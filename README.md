# MoviePilot-Plugins

个人维护的 MoviePilot 插件仓库，当前收录以下插件。

建议搭配官方仓库一起使用：
- [jxxghp/MoviePilot-Plugins](https://github.com/jxxghp/MoviePilot-Plugins)

仓库地址：
- [lucku88/MoviePilot-Plugins](https://github.com/lucku88/MoviePilot-Plugins/)

## 插件列表

| 插件 | 版本 | 说明 | 标签 |
| --- | --- | --- | --- |
| `SQ农场` | `v0.4.12` | 收菜、卖出、种植、动态调度 | 站点 |
| `SQ魔丸` | `v0.1.10` | 搬砖、清沙滩、炼造、兑换 | 站点 |
| `SQ玩偶` | `v0.1.10` | 盲盒、展柜、外展、自动回收 | 站点 |
| `SQ表情` | `v0.1.12` | 老虎机、开包、舞台演出、执行记录 | 站点 |
| `飞牛影视媒体库封面生成` | `v0.1.5` | 生成静态封面并回写飞牛影视 | 媒体服务器 |

## 插件说明

### 🌱 SQ农场

- 用途：自动收菜、自动卖出、自动种植。
- 页面：农场状态、地块状态、背包、执行历史。
- 依赖：SQ 站点 Cookie。
- 备注：如站点需要验证码，建议配置 OCR。

### ⚗️ SQ魔丸

- 用途：自动搬砖、自动清沙滩、自动炼造魔丸、自动兑换魔力。
- 页面：搬砖状态、沙滩状态、物品栏、执行历史。
- 依赖：SQ 站点 Cookie。

### 🧸 SQ玩偶

- 用途：自动回收、自展位补展、随机外展、查看盲盒和展柜。
- 页面：盲盒商店、我的盲盒、玩偶柜子、我的展柜、外展记录、执行历史。
- 依赖：SQ 站点 Cookie。

### 🎭 SQ表情

- 用途：自动老虎机、自动开包、自动收下、自动舞台演出。
- 页面：老虎机、我的表情包、表情图鉴、演出舞台、最近记录。
- 依赖：SQ 站点 Cookie。

### 🎞️ 飞牛影视媒体库封面生成

- 用途：为飞牛影视媒体库生成静态封面，并支持回写。
- 页面：媒体库选择、风格选择、封面生成、历史记录。
- 依赖：MoviePilot 中已配置好的飞牛影视媒体服务器。

## 使用方式

1. 在 MoviePilot 中添加自定义插件仓库：
   `https://github.com/lucku88/MoviePilot-Plugins/`
2. 刷新插件仓库并安装需要的插件。
3. 在插件配置页启用插件，并按需同步站点 Cookie。
4. `SQ农场` 如需验证码识别，再额外配置 OCR 地址。

## 仓库结构

```text
plugins.v2/
  fnmediacovergenerator/
  sqemoji/
  sqfarm/
  sqpill/
  sqtoy/
package.v2.json
README.md
LICENSE
```

## 说明

- 本仓库插件由个人维护。
- 站点页面或接口变化后，相关插件可能需要同步更新。
- 如果 MoviePilot 没有立即显示新版本，先刷新插件仓库，再重启容器。

## License

MIT
