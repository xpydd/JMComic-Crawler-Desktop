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
