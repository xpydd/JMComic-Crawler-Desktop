#!/usr/bin/env python3
import sys
import os
import json
import re
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import jmcomic


def default_save_dir():
    path = Path.home() / 'Desktop'
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def make_option(save_dir=None):
    option = jmcomic.JmOption.default()
    base_dir = save_dir.strip() if isinstance(save_dir, str) else save_dir
    option.dir_rule.base_dir = os.path.abspath(os.path.expanduser(base_dir or default_save_dir()))
    os.makedirs(option.dir_rule.base_dir, exist_ok=True)
    return option


def normalize_ids(raw_ids):
    ids = [
        item[1:] if item.lower().startswith(('p', 'a')) else item
        for item in re.split(r'[\s,，]+', raw_ids.strip())
        if item
    ]
    return list(dict.fromkeys(ids))


def emit_json(func, *args):
    with redirect_stdout(sys.stderr):
        result = func(*args)
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write('\n')


def download(album_id, save_dir=None):
    try:
        option = make_option(save_dir)
        jmcomic.download_album(album_id, option)
        return {"success": True, "message": f"本子 {album_id} 下载完成"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def download_chapter(photo_id, save_dir=None):
    try:
        option = make_option(save_dir)
        jmcomic.download_photo(photo_id, option)
        return {"success": True, "message": f"章节 {photo_id} 下载完成"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def download_chapters(raw_photo_ids, save_dir=None):
    try:
        ids = normalize_ids(raw_photo_ids)
        if not ids:
            return {"success": False, "message": "章节ID为空"}

        option = make_option(save_dir)
        for photo_id in ids:
            jmcomic.download_photo(photo_id, option)

        return {"success": True, "message": f"已下载 {len(ids)} 个章节: {', '.join(ids)}"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def view(album_id):
    try:
        option = make_option()
        client = option.new_jm_client()
        album = client.get_album_detail(album_id)
        cover_url = jmcomic.JmcomicText.get_album_cover_url(album.id)

        info = {
            "id": album.id,
            "title": album.name,
            "author": ", ".join(album.authors),
            "tags": album.tags,
            "views": album.views,
            "likes": album.likes,
            "comments": album.comment_count,
            "pages": album.page_count,
            "cover_url": cover_url,
            "chapters": [
                {
                    "id": pid,
                    "title": title.strip(),
                    "cover_url": jmcomic.JmcomicText.get_album_cover_url(pid),
                }
                for pid, _index, title in album.episode_list
            ],
        }
        return info
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "参数不足"}))
        sys.exit(1)

    action = sys.argv[1]
    target_id = sys.argv[2]
    save_dir = sys.argv[3] if len(sys.argv) > 3 else None

    if action == "download":
        emit_json(download, target_id, save_dir)
    elif action == "download_chapter":
        emit_json(download_chapter, target_id, save_dir)
    elif action == "download_chapters":
        emit_json(download_chapters, target_id, save_dir)
    elif action == "view":
        emit_json(view, target_id)
    else:
        print(json.dumps({"error": "未知操作"}))
