from json import loads
from pathlib import Path
from unittest import TestCase


class TestDesktopTauriApi(TestCase):
    def test_frontend_uses_global_invoke_api(self):
        root = Path(__file__).parents[2]
        html = (root / 'tauri-app' / 'src' / 'index.html').read_text(encoding='utf-8')
        config = loads((root / 'tauri-app' / 'src-tauri' / 'tauri.conf.json').read_text(encoding='utf-8'))

        self.assertIn('window.__TAURI__.tauri.invoke', html)
        self.assertTrue(config['build']['withGlobalTauri'])
