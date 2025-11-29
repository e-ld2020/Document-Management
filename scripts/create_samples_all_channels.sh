#!/usr/bin/env bash
root_dir="/Users/kaoru/Desktop/Document-Management/3分動画"
samples=("1129_1本目 test みかん.md" "1129_2本目 test みかん.md" "1129_3本目 test みかん.md" "1129_4本目 test みかん.md")

tmpl_setting="/Users/kaoru/Desktop/Document-Management/setting/00_TEMPLATE_複製用.md"
tmpl_system="/Users/kaoru/Desktop/Document-Management/System/Templates/3分チーム用テンプレート.md"

read -r -d '' default_tmpl <<'TEMPLATE'
完成動画：


辞書登録して欲しい単語：


ネタ元：


記事：


タイトル：


概要：


画像：
※1MBを超える際は圧縮してください。
※画像はダウンロードしたら必ず削除してください（容量を喰うため）


サムネ：
TEMPLATE

cd "$root_dir" || { echo "3分動画 フォルダが見つかりません"; exit 1; }

for channel in */ ; do
  [ -d "$channel" ] || continue
  if [ -f "${channel}_TEMPLATE.md" ]; then
    tmpl="${channel}_TEMPLATE.md"
  elif [ -f "$tmpl_setting" ]; then
    tmpl="$tmpl_setting"
  elif [ -f "$tmpl_system" ]; then
    tmpl="$tmpl_system"
  else
    tmpl=""
  fi

  for s in "${samples[@]}"; do
    target="${channel}${s}"
    if [ -e "$target" ]; then
      echo "skip (exists): $target"
      continue
    fi
    if [ -n "$tmpl" ]; then
      cp "$tmpl" "$target"
    else
      printf "%s\n" "$default_tmpl" > "$target"
    fi
    echo "created: $target"
  done
done

echo "Done. 次に git add / commit / push を実行してください。"
