#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

repo_root = Path("/Users/kaoru/Desktop/Document-Management")
source_dir = repo_root / "3分動画" / "3分動画"
target_dir = repo_root / "3分動画"

if not source_dir.exists():
    print(f"Source directory does not exist: {source_dir}")
    exit(1)

# source_dir 内のすべてのアイテムを取得
items = list(source_dir.iterdir())

print(f"Found {len(items)} items to move")

for item in items:
    item_name = item.name
    
    # .gitkeep はスキップ
    if item_name == ".gitkeep":
        print(f"Skipping: {item_name}")
        continue
    
    old_path = source_dir / item_name
    new_path = target_dir / item_name
    
    try:
        # git mv で移動
        subprocess.run(
            ["git", "mv", str(old_path), str(new_path)],
            cwd=repo_root,
            check=True,
            capture_output=True
        )
        print(f"✓ Moved: {item_name}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {item_name} - {e.stderr.decode()}")
    except Exception as e:
        print(f"✗ Error: {item_name} - {str(e)}")

# 空になった source_dir を削除
try:
    os.rmdir(source_dir)
    print(f"✓ Removed empty directory: 3分動画/3分動画")
except Exception as e:
    print(f"Note: Could not remove directory - {e}")

print("\nDone!")
