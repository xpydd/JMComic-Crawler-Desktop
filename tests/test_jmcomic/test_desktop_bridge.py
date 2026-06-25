import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


def load_bridge():
    bridge_path = Path(__file__).parents[2] / 'tauri-app' / 'bridge.py'
    spec = importlib.util.spec_from_file_location('desktop_bridge', bridge_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeAlbum:
    id = album_id = '350234'
    name = 'Example Album'
    authors = ['Author A', 'Author B']
    tags = ['tag-a', 'tag-b']
    views = '1K'
    likes = '2K'
    comment_count = 3
    page_count = 42
    episode_list = [('350234', '1', 'Chapter One'), ('350235', '2', 'Chapter Two')]


class FakeClient:
    def get_album_detail(self, album_id):
        assert album_id == '350234'
        return FakeAlbum()


class FakeOption:
    def new_jm_client(self):
        return FakeClient()


class TestDesktopBridge(TestCase):
    def test_view_uses_album_episode_list_for_chapters(self):
        bridge = load_bridge()

        with patch.object(bridge.jmcomic.JmOption, 'default', return_value=FakeOption()):
            result = bridge.view('350234')

        self.assertNotIn('error', result)
        self.assertEqual(result['id'], '350234')
        self.assertEqual(result['title'], 'Example Album')
        self.assertEqual(result['author'], 'Author A, Author B')
        self.assertEqual(result['chapters'], [
            {'id': '350234', 'title': 'Chapter One'},
            {'id': '350235', 'title': 'Chapter Two'},
        ])
