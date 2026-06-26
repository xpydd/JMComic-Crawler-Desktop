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
