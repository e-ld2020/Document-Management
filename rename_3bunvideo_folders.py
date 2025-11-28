#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path

repo_root = Path("/Users/kaoru/Desktop/Document-Management")
target_dir = repo_root / "3分動画"

# target_dir 内のフォルダをリネーム
items_to_rename = []

for item in target_dir.iterdir():
    if item.is_dir():
        dirname = item.name
        # 数字で始まるフォルダをチェック
        if re.match(r'^\d+[\s_-]', dirname):
            # 先頭の数字とスペース/アンダースコア/ハイフンを削除
            new_name = re.sub(r'^\d+[\s_-]+', '', dirname)
            if new_name and new_name != dirname:
                items_to_rename.append((item, target_dir / new_name))

print(f"Total folders to rename: {len(items_to_rename)}\n")

success_count = 0
error_count = 0

for old_path, new_path in sorted(items_to_rename):
    try:
        # git mv で移動
        subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            cwd=repo_root,
            check=True,
            capture_output=True
        )
        print(f"✓ {old_path.name} → {new_path.name}")
        success_count += 1
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {old_path.name} - {e.stderr.decode()}")
        error_count += 1
    except Exception as e:
        print(f"✗ Error: {old_path.name} - {str(e)}")
        error_count += 1

print(f"\n✓ Success: {success_count}, ✗ Errors: {error_count}")
