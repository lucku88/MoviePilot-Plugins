# MoviePilot-Plugins

MoviePilot 第三方插件仓库，当前收录个人维护的插件，后续新增插件也会继续放在这里统一维护。

> ⚠️ 注意：本仓库为个人维护仓库，推荐优先搭配 [官方插件仓库](https://github.com/jxxghp/MoviePilot-Plugins) 一起使用。

## 📦 插件列表

| 序号 | 插件名称 | 版本 | 功能描述 | 标签 |
|------|----------|------|----------|------|
| 1 | [🌱 SQ农场 (SQFarm)](#1--sq农场-sqfarm) | v0.4.5 | 支持 SQ 站点农场状态展示、一键收菜、种植、动态调度和 Cookie 同步 | 站点 |
| 2 | [🖼️ 媒体库封面生成魔改 (MediaCoverRemix)](#2-️-媒体库封面生成魔改-mediacoverremix) | v0.1.4 | 读取 MoviePilot 已配置的飞牛影视媒体库，生成拼贴风格封面并尝试自动替换 | 媒体服务器 |

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

### 2. 🖼️ 媒体库封面生成魔改 (MediaCoverRemix)
- 版本：v0.1.4
- 功能：读取 MoviePilot 已配置的飞牛影视媒体库，按媒体库现有 `image_list` 生成新的拼贴风格封面，并尝试自动回写到飞牛影视。
- 标签：媒体服务器
- 特点：
  - 🧩 直接读取 MoviePilot 中的媒体服务器和媒体库列表
  - 🎨 复用 Jellyfin Library Poster 的拼贴视觉思路，生成横版媒体库封面
  - 🖼️ 提供 Vue 配置页与数据页，支持预览最近一次生成结果
  - 🧪 内置飞牛 `trimemedia` 运行时探测，便于排查鉴权与回写链路
  - 🔁 已按飞牛前端实际上传参数补齐临时图片上传请求，并增强回写失败时的脱敏诊断信息
  - 🔁 支持手动执行、保存后立即执行和 Cron 定时生成
- 说明：
  - 当前重点适配飞牛影视 `trimemedia`
  - 自动替换依赖 MoviePilot 运行时里能取到飞牛服务的连接信息与鉴权信息
  - 如果回写失败，插件仍会保留本地生成的封面文件与预览结果

## 📖 使用说明

1. 在 MoviePilot 的自定义插件仓库中添加：
   - `https://github.com/lucku88/MoviePilot-Plugins/`
2. 刷新插件仓库并安装需要的插件，例如 `SQ农场`
3. 在插件配置页完成以下设置：
   - 启用站点 Cookie 同步，或手动填写 SQ Cookie
   - 配置 OCR 地址，例如 `http://ip:8089/api/tr-run/`
   - 选择是否自动售出、自动种植以及优先种植种子
4. 如果使用 `媒体库封面生成魔改`：
   - 先填写 MoviePilot 地址与 API Token
   - 选择飞牛影视媒体服务器和需要处理的媒体库
   - 按需设置标题映射规则、封面尺寸和定时任务
   - 先用“立即生成”验证封面生成与飞牛回写是否正常

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
  mediacoverremix/
package.v2.json
README.md
LICENSE
```

## 🛠️ 开发说明

- 插件主文件：`plugins.v2/sqfarm/__init__.py`
- 状态页：`plugins.v2/sqfarm/src/components/Page.vue`
- 配置页：`plugins.v2/sqfarm/src/components/Config.vue`
- 市场配置：`package.v2.json`

`MediaCoverRemix` 对应文件：

- 插件主文件：`plugins.v2/mediacoverremix/__init__.py`
- 状态页：`plugins.v2/mediacoverremix/src/components/Page.vue`
- 配置页：`plugins.v2/mediacoverremix/src/components/Config.vue`
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
