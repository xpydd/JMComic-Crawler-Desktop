# JMComic Crawler Desktop

JMComic Crawler Desktop 是基于 Tauri 的桌面下载器，把本仓库里的 `jmcomic` Python 能力封装成图形界面。用户不需要写脚本或记命令，只输入本子 ID / 章节 ID，就能查看详情、选择保存目录并下载到本地。

> 本项目仅提供技术封装。请自行确认下载内容的版权、年龄限制和所在地法律要求。

## 功能

- 查看本子详情、封面、作者、标签、页数和章节列表
- 下载整本本子
- 下载单个章节
- 输入多个章节 ID 批量下载，重复 ID 自动去重
- 从详情页勾选多个章节批量下载
- 在设置里选择并持久化默认保存目录
- 已配置保存目录时直接下载，未配置时确认后默认保存到桌面
- 操作日志显示查看和下载耗时
- macOS 桌面安装包，Windows 安装包通过 GitHub Actions 生成

## 下载与安装

### macOS

当前本地构建产物：

```text
tauri-app/src-tauri/target/release/bundle/dmg/JMComic桌面版_0.1.0_aarch64.dmg
```

双击 `.dmg` 后把应用拖入 Applications 即可。

### Windows

Windows 安装包需要在 Windows 环境构建。本仓库提供 GitHub Actions 工作流：

```text
.github/workflows/desktop-release.yml
```

推送 tag 后会生成 Windows `.msi` 和 macOS `.dmg` 构建产物。

## 使用

1. 打开 JMComic 桌面版
2. 在设置里选择默认保存目录
3. 输入本子 ID，点击「查看详情」
4. 下载整本，或选择 / 输入章节后批量下载
5. 在右侧日志查看进度、耗时和错误信息

## 本地开发

### 环境要求

- macOS 或 Windows
- Python 3.9+
- Rust stable
- Tauri CLI：`cargo install tauri-cli`
- PyInstaller：`python3 -m pip install pyinstaller`

项目会直接复用仓库源码里的 `jmcomic` 包，不需要额外安装发布版 `jmcomic`。

### macOS 构建

```bash
bash tauri-app/build.sh
```

构建成功后，DMG 位于：

```text
tauri-app/src-tauri/target/release/bundle/dmg/
```

### Windows 构建

建议使用 GitHub Actions 或 Windows 本机：

```powershell
python -m pip install pyinstaller
python -m PyInstaller --onefile --name jmcomic-bridge tauri-app/bridge.py --distpath tauri-app/dist --workpath tauri-app/build --specpath tauri-app
cd tauri-app/src-tauri
cargo tauri build --bundles msi
```

Windows 产物位于：

```text
tauri-app/src-tauri/target/release/bundle/msi/
```

## 测试

```bash
python3 -m unittest tests.test_jmcomic.test_desktop_bridge tests.test_jmcomic.test_desktop_runtime_contract tests.test_jmcomic.test_desktop_tauri_api -v
cd tauri-app/src-tauri && cargo test
```

## 项目结构

```text
tauri-app/
├── bridge.py                 # Python 桥接层
├── build.sh                  # macOS 本地构建脚本
├── src/index.html            # 桌面端界面
└── src-tauri/
    ├── Cargo.toml            # Tauri/Rust 配置
    ├── tauri.conf.json       # 应用配置与打包资源
    └── src/main.rs           # Tauri 命令和桥接调用
```

## 发布 0.1.0

本地 macOS 构建：

```bash
bash tauri-app/build.sh
```

GitHub Actions 发布构建：

```bash
git tag v0.1.0
git push origin master --tags
```

然后在 GitHub Actions 的 `Desktop Release` 工作流中下载 macOS / Windows 构建产物。

## 致谢

- [JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
- [Tauri](https://tauri.app/)
