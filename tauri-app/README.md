# JMComic Desktop App

这里是 JMComic 桌面客户端的 Tauri 应用目录。

## 目录

```text
tauri-app/
├── bridge.py           # Python 桥接层
├── build.sh            # macOS 一键构建脚本
├── src/index.html      # 前端界面
└── src-tauri/          # Rust / Tauri 后端
```

## 本地构建 macOS DMG

```bash
bash tauri-app/build.sh
```

构建产物：

```text
tauri-app/src-tauri/target/release/bundle/dmg/
```

## Windows MSI

Windows MSI 建议通过仓库根目录的 GitHub Actions 工作流生成：

```text
.github/workflows/desktop-release.yml
```

Windows 本机也可以执行：

```powershell
python -m pip install -e . pyinstaller
python -m PyInstaller --onefile --name jmcomic-bridge tauri-app/bridge.py --distpath tauri-app/dist --workpath tauri-app/build --specpath tauri-app
cd tauri-app/src-tauri
cargo tauri build --bundles msi
```

## 开发

```bash
cd tauri-app/src-tauri
cargo tauri dev
```
