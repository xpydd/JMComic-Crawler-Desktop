import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
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
    def __init__(self):
        self.dir_rule = type('DirRule', (), {'base_dir': None})()

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
            {
                'id': '350234',
                'title': 'Chapter One',
                'cover_url': result['chapters'][0]['cover_url'],
            },
            {
                'id': '350235',
                'title': 'Chapter Two',
                'cover_url': result['chapters'][1]['cover_url'],
            },
        ])
        self.assertIn('/media/albums/350234', result['cover_url'])
        self.assertIn('/media/albums/350234', result['chapters'][0]['cover_url'])

    def test_download_chapters_accepts_multiple_ids(self):
        bridge = load_bridge()
        called = []

        def fake_download_photo(photo_id, option):
            called.append((photo_id, option.dir_rule.base_dir))

        with patch.object(bridge.jmcomic.JmOption, 'default', return_value=FakeOption()), \
                patch.object(bridge.jmcomic, 'download_photo', side_effect=fake_download_photo):
            result = bridge.download_chapters('1, 2\np3', '/tmp/jm')

        self.assertEqual(result['success'], True)
        self.assertEqual(called, [('1', '/tmp/jm'), ('2', '/tmp/jm'), ('3', '/tmp/jm')])

    def test_download_chapters_deduplicates_ids(self):
        bridge = load_bridge()
        called = []

        def fake_download_photo(photo_id, option):
            called.append(photo_id)

        with patch.object(bridge.jmcomic.JmOption, 'default', return_value=FakeOption()), \
                patch.object(bridge.jmcomic, 'download_photo', side_effect=fake_download_photo):
            result = bridge.download_chapters('1, 1\np2 p2', '/tmp/jm')

        self.assertEqual(result['success'], True)
        self.assertEqual(called, ['1', '2'])

    def test_make_option_defaults_to_writable_desktop_dir(self):
        bridge = load_bridge()

        with TemporaryDirectory() as home, \
                patch.object(bridge.jmcomic.JmOption, 'default', return_value=FakeOption()), \
                patch.object(bridge.Path, 'home', return_value=Path(home)):
            option = bridge.make_option()

            self.assertEqual(option.dir_rule.base_dir, str(Path(home) / 'Desktop'))
            self.assertTrue(Path(option.dir_rule.base_dir).is_dir())

    def test_emit_json_keeps_logs_out_of_stdout(self):
        bridge = load_bridge()

        with patch('sys.stdout') as stdout, patch('sys.stderr') as stderr:
            bridge.emit_json(lambda *_: (print('log line'), {'ok': True})[1], 'x')

        output = ''.join(call.args[0] for call in stdout.write.call_args_list)
        payload = json.loads(output)
        self.assertEqual(payload, {'ok': True})
        stderr.write.assert_called()
