#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path

# リポジトリのルートパス
repo_root = Path("/Users/kaoru/Desktop/Document-Management")

# リネーム対象を収集（深さ優先で処理：ネストされたアイテムから先にリネーム）
# フォルダのみ処理、ファイルは変更しない
items_to_rename = []

for root, dirs, files in os.walk(repo_root, topdown=False):
    # 処理対象外ディレクトリをスキップ
    if '.git' in root or 'node_modules' in root or '__pycache__' in root:
        continue
    
    # フォルダのみ処理（ファイルは変更しない）
    for dirname in dirs:
        # 数字で始まるディレクトリをチェック
        # 例: "000 Magistoリンク", "100 Yabaai芸能", "00010 3分超速報"
        if re.match(r'^\d+[\s_-]', dirname):
            old_path = Path(root) / dirname
            # 先頭の数字とスペース/アンダースコア/ハイフンを削除
            new_name = re.sub(r'^\d+[\s_-]+', '', dirname)
            if new_name and new_name != dirname:
                new_path = Path(root) / new_name
                items_to_rename.append((old_path, new_path))

print(f"Total folders to rename: {len(items_to_rename)}\n")

success_count = 0
error_count = 0

for old_path, new_path in sorted(items_to_rename):
    # 既に新しいパスが存在していないか確認
    if new_path.exists() and str(old_path) != str(new_path):
        print(f"⊘ Skip (already exists): {old_path.name} → {new_path.name}")
        continue
    
    try:
        # Git tracked か確認
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(old_path)],
            cwd=repo_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Git tracked なら git mv
            subprocess.run(["git", "mv", str(old_path), str(new_path)], cwd=repo_root, check=True)
            print(f"✓ {old_path.name} → {new_path.name}")
            success_count += 1
        else:
            # 追跡されていなければ通常の mv
            os.rename(old_path, new_path)
            print(f"• {old_path.name} → {new_path.name} (untracked)")
            success_count += 1
    except Exception as e:
        print(f"✗ Error: {old_path.name} - {str(e)[:50]}")
        error_count += 1

print(f"\n✓ Success: {success_count}, ✗ Errors: {error_count}")
