# Release 0.1.0

## 1. 范围
- 发布 JMComic 桌面下载器第一版。
- 提供 macOS DMG 本地构建产物。
- 提供 GitHub Actions 工作流，用于生成 macOS DMG 和 Windows MSI。

## 2. 用户可见变化
- 图形界面输入本子 ID 查看详情。
- 支持整本下载、单章节下载、批量章节下载。
- 支持在设置中选择默认保存目录。
- 已配置保存目录时直接下载；未配置时确认后默认保存到桌面。
- 操作日志显示查看和下载耗时。
- 界面已调整为紧凑双栏桌面布局。

## 3. 技术变更
- Tauri 前端使用原生 HTML/CSS/JavaScript。
- Rust 后端通过 Tauri command 调用 PyInstaller 打包后的 Python 桥接层。
- Python 桥接层复用仓库内 `jmcomic` 包。
- Windows 桥接资源使用 `jmcomic-bridge.exe`，macOS 使用 `jmcomic-bridge`。

## 4. 配置与环境变量
- 无必需环境变量。
- 下载保存目录使用浏览器 `localStorage` 持久化。

## 5. 已知风险
- Windows 安装包需要在 Windows runner 或 Windows 本机生成，当前 macOS 本机无法直接产出 Windows MSI。
- 下载和详情查询依赖目标站点可访问性与网络环境。
- macOS 产物当前未做 Apple Developer ID 签名和 notarization，首次打开可能需要用户手动确认。

## 6. 回滚方式
- 回滚 Git tag 或发布说明中的安装包。
- 代码层回滚到发布前一个稳定提交。
