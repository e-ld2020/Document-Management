#!/bin/zsh

# 3分動画/3分動画/ の中身を 3分動画/ に移動
source_dir="/Users/kaoru/Desktop/Document-Management/3分動画/3分動画"
target_dir="/Users/kaoru/Desktop/Document-Management/3分動画"

# ソースディレクトリ内のすべてをターゲットに移動
cd /Users/kaoru/Desktop/Document-Management

# git mv で移動（.gitkeep 以外）
for item in "$source_dir"/*; do
    basename_item=$(basename "$item")
    
    # .gitkeep はスキップ
    if [[ "$basename_item" == ".gitkeep" ]]; then
        continue
    fi
    
    old_path="3分動画/3分動画/$basename_item"
    new_path="3分動画/$basename_item"
    
    echo "Moving: $old_path → $new_path"
    git mv "$old_path" "$new_path"
done

# 空になった 3分動画/3分動画 フォルダを削除
echo "Removing empty directory: 3分動画/3分動画"
rmdir "$source_dir"

echo "Done!"
