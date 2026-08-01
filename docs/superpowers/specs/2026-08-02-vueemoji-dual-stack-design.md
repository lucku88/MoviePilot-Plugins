# Vue-表情移除优先 IPv4 设计

## 目标

让 Vue-表情与 Vue-农场、Vue-魔丸、Vue-玩偶保持一致，不再提供“优先 IPv4”设置，也不再持续强制修改 `urllib3` 的全局地址族选择。站点连接交给操作系统和 Python 网络库自动选择可用的 IPv4 或 IPv6。

## 行为

- 配置页删除“优先 IPv4”开关，默认配置和保存请求不再包含 `force_ipv4`。
- 后端删除 `_force_ipv4` 状态和强制 `socket.AF_INET` 的代码。
- 热更新时仅识别旧版留下的特定 IPv4 lambda，并一次性恢复为系统地址族选择；其他自定义选择器不修改，因此无需重启 MoviePilot。
- 读取旧配置时自动忽略 `force_ipv4`，不要求清空配置，不影响 Cookie、自动任务、通知、执行历史和动态调度。
- HTTP 重试、超时、Cookie 同步和动作确认逻辑保持不变。

## 发布

- Vue-表情升级到 `0.1.6`。
- 同步后端版本、`package.json`、`package-lock.json`、`package.v2.json` 和 `README.md`。
- 重新构建 `dist`，使 MoviePilot 市场安装包与源码一致。

## 测试

- 后端测试确认默认配置和持久化配置不含 `force_ipv4`。
- 后端测试确认不再强制 IPv4，构建 Session 时保留正常选择器，并能在热更新时清理旧版特定 IPv4 lambda。
- 前端契约测试确认配置源码不含 `config.force_ipv4` 和“优先 IPv4”。
- 发布测试确认所有版本文件一致且更新说明包含 IPv4、IPv6 和保留配置行为。
- 运行 Vue-表情相关测试、四插件公共重试测试、Python 编译、Vite 构建和 Git 格式检查。
