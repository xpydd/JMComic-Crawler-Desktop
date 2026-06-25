#!/usr/bin/env python3
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import jmcomic

def download(album_id, save_dir=None):
    try:
        option = jmcomic.JmOption.default()
        if save_dir:
            option.dir_rule.base_dir = save_dir
        jmcomic.download_album(album_id, option)
        return {"success": True, "message": f"本子 {album_id} 下载完成"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def download_chapter(photo_id, save_dir=None):
    try:
        option = jmcomic.JmOption.default()
        if save_dir:
            option.dir_rule.base_dir = save_dir
        jmcomic.download_photo(photo_id, option)
        return {"success": True, "message": f"章节 {photo_id} 下载完成"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def view(album_id):
    try:
        client = jmcomic.JmOption.default().new_jm_client()
        album = client.get_album_detail(album_id)

        info = {
            "id": album.id,
            "title": album.name,
            "author": ", ".join(album.authors),
            "tags": album.tags,
            "views": album.views,
            "likes": album.likes,
            "comments": album.comment_count,
            "pages": album.page_count,
            "chapters": [{"id": pid, "title": title.strip()} for pid, _index, title in album.episode_list]
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
        result = download(target_id, save_dir)
        print(json.dumps(result, ensure_ascii=False))
    elif action == "download_chapter":
        result = download_chapter(target_id, save_dir)
        print(json.dumps(result, ensure_ascii=False))
    elif action == "view":
        result = view(target_id)
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps({"error": "未知操作"}))
