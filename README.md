# MoviePilot-Plugins

MoviePilot 第三方插件仓库，当前收录个人维护的插件，后续新增插件也会继续放在这里统一维护。

> ⚠️ 注意：本仓库为个人维护仓库，推荐优先搭配 [官方插件仓库](https://github.com/jxxghp/MoviePilot-Plugins) 一起使用。

## 📦 插件列表

| 序号 | 插件名称 | 版本 | 功能描述 | 标签 |
|------|----------|------|----------|------|
| 1 | [🌱 SQ农场 (SQFarm)](#1--sq农场-sqfarm) | v0.4.5 | 支持 SQ 站点农场状态展示、一键收菜、种植、动态调度和 Cookie 同步 | 站点 |
| 2 | [🎞️ 飞牛影视媒体库封面生成 (FnMediaCoverGenerator)](#2-️-飞牛影视媒体库封面生成-fnmediacovergenerator) | v0.1.2 | 为飞牛影视媒体库生成静态封面，并支持自动替换 | 媒体服务器 |

### 1. 🌱 SQ农场 (SQFarm)
- 版本：v0.4.5
- 功能：支持 SQ 站点农场状态展示、一键收菜、种植、动态调度和 Cookie 同步。
- 标签：站点
- 特点：
  - 🌾 支持农场总览、背包、种子商店、坑位状态和执行历史展示
  - ⏰ 动态识别最近可收时间并注册下一次运行
  - 🍅 支持一键收菜、一键种植空地和手动点田块交互
  - 🍪 支持优先读取 MoviePilot 站点中的 `sq` Cookie
  - 🔎 支持 `trwebocr` 验证码识别，自动完成收菜流程
  - 📣 支持执行结果通知和历史记录回看
- 更新说明：
  <details>
  <summary>点击查看更新历史</summary>

  - v0.4.5: 简化状态页坑位文案与种子卡片显示，并统一扩展坑位为未解锁样式。
  - v0.4.4: 修复配置页在浅色模式下仍强制显示深色样式的问题。
  - v0.4.3: 修复配置页与状态页主题自动识别，并将状态页标题统一为“种菜赚魔力”。
  - v0.4.2: 修正主题自动识别，恢复选种子点田块交互，并按每个农场固定 10 个坑位展示。
  - v0.4.1: 重做 SQ农场页面与配置页布局，补齐外层留白，并适配浅色与深色主题。
  - v0.4.0: 统一命名为 SQ农场，新增自动售出与自动种植开关，并调整任务通知样式为分隔线报告。
  - v0.3.2: 取消固定轮询，改为启动时初始化一次并按最近可收时间动态注册下一次运行。
  - v0.3.1: 恢复状态页只读展示，修正优先种植下拉与 OCR 容器说明，并增强坑位显示对魔力解锁坑位的兼容。
  - v0.3.0: 新增页面交互、优先种植下拉、OCR 容器说明，并将收益改为售出减种植成本。
  - v0.2.1: 修复验证码图片相对地址导致的收菜失败，并提升插件版本便于 MoviePilot 更新。
  - v0.2.0: 升级为 Vue 面板，新增动态最近可收调度、站点 Cookie 同步和农场仪表盘。
  - v0.1.0: 首版发布，支持 MoviePilot V2 定时执行 SQ农场收菜、售卖和种植。
  </details>

### 2. 🎞️ 飞牛影视媒体库封面生成 (FnMediaCoverGenerator)
- 版本：v0.1.2
- 功能：为 MoviePilot 已配置的飞牛影视媒体库生成静态封面，并支持自动替换。
- 标签：媒体服务器
- 特点：
  - 🎨 复用成熟的拼贴封面样式与字体配置逻辑，并收敛为飞牛影视专用版本
  - 🧩 直接读取 MoviePilot 已配置的飞牛影视媒体服务器与媒体库，无需额外手填库信息
  - 🖼️ 保留统一的媒体库封面生成操作流：选媒体库、选风格、调字体、立即生成、查看历史
  - 🔁 仅生成静态 PNG/JPG/WebP 封面，并支持飞牛自动回写
  - 🔀 每次会从对应媒体库的封面源图列表中随机取图，避免长期固定同一批来源
  - 🔐 复用现有飞牛鉴权与上传链路，对接 `image/temp/upload` 与 `mdb/setPoster`
  - 🧹 支持图片缓存与字体缓存清理，便于重复调样式
- 说明：
  - 当前重点适配 MoviePilot 中已配置的飞牛影视 `trimemedia`
  - 如果飞牛回写失败，插件会保留本地输出结果与历史记录，便于手动核对

## 📖 使用说明

1. 在 MoviePilot 的自定义插件仓库中添加：
   - `https://github.com/lucku88/MoviePilot-Plugins/`
2. 刷新插件仓库并安装需要的插件，例如 `SQ农场`
3. 在插件配置页完成以下设置：
   - 启用站点 Cookie 同步，或手动填写 SQ Cookie
   - 配置 OCR 地址，例如 `http://ip:8089/api/tr-run/`
   - 选择是否自动售出、自动种植以及优先种植种子
4. 如果使用 `飞牛影视媒体库封面生成`：
   - 先在 MoviePilot 的媒体服务器里配置好飞牛影视账号
   - 在插件页选择飞牛影视媒体服务器、目标媒体库与静态风格
   - 按需调整字体、标题映射和分辨率
   - 先用“立即生成”验证输出效果，再决定是否开启自动替换和定时任务

## 🧩 OCR 说明

推荐额外部署 `trwebocr` 容器，再将 OCR 地址配置为 `http://ip:8089/api/tr-run/`：

```yaml
version: '3.8'
services:
  trwebocr:
    image: mmmz/trwebocr:latest
    container_name: trwebocr
    ports:
      - "8089:8089"
    restart: always
    volumes:
      - ./data:/app/data
    environment:
      - TZ=Asia/Shanghai
    network_mode: bridge
```

## 🗂️ 仓库结构

```text
plugins.v2/
  sqfarm/
  fnmediacovergenerator/
package.v2.json
README.md
LICENSE
```

## 🛠️ 开发说明

- 插件主文件：`plugins.v2/sqfarm/__init__.py`
- 状态页：`plugins.v2/sqfarm/src/components/Page.vue`
- 配置页：`plugins.v2/sqfarm/src/components/Config.vue`
- 市场配置：`package.v2.json`

`FnMediaCoverGenerator` 对应文件：

- 插件主文件：`plugins.v2/fnmediacovergenerator/__init__.py`
- 封面样式：`plugins.v2/fnmediacovergenerator/style/`
- 工具模块：`plugins.v2/fnmediacovergenerator/utils/`
- 市场配置：`package.v2.json`

后续如果要继续添加新插件，可以直接：

1. 在 `plugins.v2/` 下新增插件目录
2. 在 `package.v2.json` 中补充插件条目
3. 在本 README 的“插件列表”和详情章节追加说明

## ⚠️ 注意事项

1. 本仓库插件为个人维护，请先确认站点 Cookie 和 OCR 服务可用。
2. 如果 MoviePilot 未及时显示新版本，先刷新插件仓库，再重启容器。
3. 站点接口、验证码或页面结构变化时，插件可能需要同步更新。

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。
