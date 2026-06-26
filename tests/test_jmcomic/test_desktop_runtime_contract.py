import json
from pathlib import Path
from unittest import TestCase


class TestDesktopRuntimeContract(TestCase):
    def test_bridge_resource_path_matches_bundle_config(self):
        root = Path(__file__).parents[2]
        config = json.loads((root / 'tauri-app' / 'src-tauri' / 'tauri.conf.json').read_text(encoding='utf-8'))
        resource = config['tauri']['bundle']['resources'][0]
        main_rs = (root / 'tauri-app' / 'src-tauri' / 'src' / 'main.rs').read_text(encoding='utf-8')

        self.assertIn(resource, main_rs)

    def test_choose_save_dir_persists_selection_immediately(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')
        start = html.index('async function chooseSaveDir()')
        end = html.index('function getSaveDir()')
        choose_save_dir_body = html[start:end]

        self.assertIn("localStorage.setItem('defaultSaveDir', dir);", choose_save_dir_body)

    def test_save_dir_picker_uses_frontend_dialog_api(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')
        main_rs = (root / 'tauri-app' / 'src-tauri' / 'src' / 'main.rs').read_text(encoding='utf-8')
        start = html.index('async function chooseSaveDir()')
        end = html.index('function getSaveDir()')
        choose_save_dir_body = html[start:end]

        self.assertIn('window.__TAURI__.dialog.open', choose_save_dir_body)
        self.assertIn('directory: true', choose_save_dir_body)
        self.assertNotIn("tauri.invoke('choose_save_dir')", choose_save_dir_body)
        self.assertNotIn('blocking::FileDialogBuilder', main_rs)
        self.assertNotIn('fn choose_save_dir', main_rs)

    def test_album_rendering_is_batched_and_lazy_loads_images(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('requestAnimationFrame', html)
        self.assertIn('loading="lazy"', html)
        self.assertIn('decoding="async"', html)

    def test_bridge_commands_run_off_the_tauri_command_thread(self):
        root = Path(__file__).parents[2]
        main_rs = (root / 'tauri-app' / 'src-tauri' / 'src' / 'main.rs').read_text(encoding='utf-8')

        self.assertIn('spawn_blocking', main_rs)
        self.assertIn('async fn download_album', main_rs)
        self.assertIn('async fn view_album', main_rs)

    def test_frontend_truncates_noisy_messages(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('function formatMessage', html)
        self.assertIn('max = 1200', html)

    def test_download_confirms_only_when_save_dir_is_missing(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('function shouldConfirmDownload(saveDir)', html)
        self.assertIn('return !saveDir;', html)
        self.assertIn('shouldConfirmDownload(saveDir) && !confirm', html)

    def test_download_actions_guard_against_duplicate_submits(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('let isBusy = false;', html)
        self.assertIn('function beginLoading()', html)
        self.assertIn('if (isBusy) return false;', html)
        self.assertIn('if (!beginLoading()) return;', html)

    def test_frontend_uses_sidebar_workspace_layout(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('class="app-shell"', html)
        self.assertIn('class="sidebar"', html)
        self.assertIn('class="workspace-grid"', html)
        self.assertIn('class="side-panel"', html)
        self.assertIn('class="command-card primary-flow"', html)

    def test_frontend_uses_accessible_svg_icons_not_emoji(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('<svg', html)
        self.assertIn('aria-label="打开设置"', html)
        self.assertIn('aria-hidden="true"', html)
        for emoji in ['📚', '⚙️', '🔍', '⬇️', '📄', '📋', '⏳', '✅', '❌']:
            self.assertNotIn(emoji, html)

    def test_frontend_visible_copy_is_chinese_only(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        for text in ['Desktop crawler', '>Workspace<', '>Album<', '>Chapters<', '>Result<', '>Save path<', '>Activity<', '>Album detail<', '>Chapter list<']:
            self.assertNotIn(text, html)

    def test_frontend_uses_compact_workspace_spacing(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')

        self.assertIn('grid-template-columns: 200px minmax(0, 1fr);', html)
        self.assertIn('padding: 14px;', html)
        self.assertIn('height: 180px;', html)
        self.assertIn('min-height: 200px;', html)
