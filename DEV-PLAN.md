# JMComic Desktop DEV PLAN

## 1. 目标
- 本轮开发目标：以现有 Tauri 桌面客户端为基础，补齐主路径、状态反馈、打包和验证闭环
- 主验收结果：用户可以在 macOS 桌面应用中查看本子详情，并下载本子或章节到指定目录

## 2. 技术判断
- 项目类型：Python 核心库 + Tauri 桌面客户端
- 技术栈：Python、PyInstaller、Rust、Tauri 1.x、HTML/CSS/JavaScript
- 关键依赖：`jmcomic` 本地源码、`curl-cffi`、`pillow`、`pycryptodome`、`pyyaml`、Tauri resource 打包

## 3. 波次计划
### Wave 1：需求基线与实现对照
- 目标：确认现有代码覆盖 Product Spec 的哪些验收项
- 输入：`Product-Spec.md`、`Design-Brief.md`、`tauri-app/src/index.html`、`tauri-app/bridge.py`、`tauri-app/src-tauri/src/main.rs`
- 产出：`/check` 覆盖清单
- 风险：没有真实网络环境时，只能验证代码路径，不能证明目标站点可访问
- 验证：运行 `/check`，明确已完成、部分完成和缺失项

### Wave 2：主路径修正
- 目标：修复查看详情、下载本子、下载章节三条主路径中未接通或返回格式不一致的问题
- 输入：Wave 1 覆盖清单
- 产出：前端调用、Tauri 命令、Python 桥接层返回值一致
- 风险：桥接程序输出可能混入日志，导致前端 JSON 解析失败
- 验证：对 `view`、`download`、`download_chapter` 分别执行最小命令行检查

### Wave 3：状态与错误补齐
- 目标：补齐输入校验、loading、错误态、成功态和资源缺失提示
- 输入：Design Brief 状态矩阵
- 产出：用户能区分“未输入”“网络失败”“桥接资源缺失”“下载失败”“下载成功”
- 风险：错误信息来自 Python / Rust / 前端三层，可能不统一
- 验证：手动触发空输入、无效 ID、错误保存目录、缺失 bridge resource

### Wave 4：打包与发布前检查
- 目标：确保 macOS 打包链路稳定，并更新运行说明
- 输入：`tauri-app/build.sh`、`tauri-app/src-tauri/tauri.conf.json`
- 产出：可安装 macOS 包和明确的构建说明
- 风险：PyInstaller 产物、Tauri resource 路径和芯片架构不匹配
- 验证：执行 `tauri-app/build.sh`，检查 bundle 产物和应用内桥接调用

## 4. 横切事项
- 环境变量：第一版不要求用户配置环境变量；开发者可继续使用 `JM_OPTION_PATH` 验证 Python CLI
- AI / API 接入：无 AI；外部接口来自 JMComic 站点和现有 Python 客户端
- 状态补齐：前端统一承载 loading、错误、成功；桥接层统一返回 JSON 或明确错误字符串
- 测试门槛：Python 核心库保持现有测试；桌面端至少保留 bridge 命令级自检和一次 Tauri 构建验证

## 5. 完成定义
- [ ] `/check` 能按 Spec 输出覆盖清单
- [ ] 查看详情主路径可走通
- [ ] 下载本子主路径可走通
- [ ] 下载章节主路径可走通
- [ ] 关键状态已覆盖
- [ ] macOS 构建方式明确
- [ ] 可交给 `dev-builder` 或 `bug-fixer`
