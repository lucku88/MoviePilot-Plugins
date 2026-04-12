# MoviePilot-Plugins

个人维护的 MoviePilot 插件仓库，建议与官方仓库一起使用：
- [jxxghp/MoviePilot-Plugins](https://github.com/jxxghp/MoviePilot-Plugins)

仓库地址：
- [lucku88/MoviePilot-Plugins](https://github.com/lucku88/MoviePilot-Plugins/)

## 插件列表

| 插件 | 版本 | 说明 | 标签 |
| --- | --- | --- | --- |
| `SQ农场` | `v0.4.18` | 收菜、种植、出售、获取执行记录 | 站点 |
| `Vue-农场` | `v0.1.4` | 收菜、种植、出售、获取执行记录 | 站点 |
| `Vue-魔丸` | `v0.1.15` | 兑换、搬砖、清沙滩、炼造、获取执行记录 | 站点 |
| `SQ玩偶` | `v0.1.14` | 盲盒、回收、展出、获取执行记录 | 站点 |
| `SQ表情` | `v0.1.14` | 老虎机、开包、舞台演出、获取执行记录 | 站点 |
| `飞牛影视媒体库封面生成` | `v0.1.5` | 生成静态封面并回写飞牛影视 | 媒体服务器 |

## 插件说明

### 🌱 SQ农场
- 收菜、种植、出售、获取执行记录。

### 🌾 Vue-农场
- 收菜、种植、出售、获取执行记录。
- 用于和 `SQ农场` 对照测试新的 Vue 面板结构。

### ⚗️ Vue-魔丸
- 兑换、搬砖、清沙滩、炼造、获取执行记录。

### 🧸 SQ玩偶
- 盲盒、回收、展出、获取执行记录。

### 🎭 SQ表情
- 老虎机、开包、舞台演出、获取执行记录。

### 🎞️ 飞牛影视媒体库封面生成
- 生成静态封面并回写飞牛影视。

## 使用方式

1. 在 MoviePilot 中添加自定义插件仓库：`https://github.com/lucku88/MoviePilot-Plugins/`
2. 刷新插件仓库并安装需要的插件。
3. 在插件配置页启用插件，并按需同步站点 Cookie。
4. `SQ农场` / `Vue-农场` 如需验证码识别，再额外配置 OCR 地址。

## 仓库结构

```text
plugins.v2/
  fnmediacovergenerator/
  sqemoji/
  sqfarm/
  sqtoy/
  vuefarm/
  vuepill/
package.v2.json
README.md
LICENSE
```

## 说明

- 本仓库插件由个人维护。
- 站点页面或接口变更后，相关插件可能需要同步更新。
- 如果 MoviePilot 没有立即显示新版本，先刷新插件仓库，再重启容器。

## License

MIT
