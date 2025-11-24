name: Planner Task Automation

on:
  push:
    paths:
      - '**/*.md'
      - '**/*.txt'
  workflow_dispatch:

jobs:
  create-task:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: チェックアウト
        uses: actions/checkout@v4

      - name: 自動修復とタスク作成
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          # ▼▼▼ ID設定 ▼▼▼
          GROUP_ID: 'fb5d0dcd-f554-4ed2-bc57-5df1dfcf6ea3'
          PLAN_ID: 'E4IcGEnHOUalieUARPGTcvoAHqmv'
          TARGET_BUCKET_NAME: '00010 3分超速報'
        run: |
          # 1. Azureにログイン
          echo "Logging into Azure..."
          az login --service-principal \
            --username "$AZURE_CLIENT_ID" \
            --password "$AZURE_CLIENT_SECRET" \
            --tenant "$AZURE_TENANT_ID" \
            --allow-no-subscriptions > /dev/null

          # 2. 【自己修復】ロボット自身をチームに強制加入させる
          echo "Checking Service Principal ID..."
          SP_OBJECT_ID=$(az ad sp show --id "$AZURE_CLIENT_ID" --query id -o tsv)
          
          echo "Adding App ($SP_OBJECT_ID) to Group ($GROUP_ID)..."
          # 既にメンバーでもエラーにならないように || true をつける
          az ad group member add --group "$GROUP_ID" --member-id "$SP_OBJECT_ID" || true
          echo "✅ Member add command executed."

          # 反映待ち（念のため10秒待機）
          sleep 10

          # 3. トークン取得
          TOKEN=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)

          # 4. バケット一覧を取得
          echo "Searching bucket ID for: $TARGET_BUCKET_NAME"
          RESPONSE=$(curl -s -X GET -H "Authorization: Bearer $TOKEN" \
            "https://graph.microsoft.com/v1.0/planner/plans/$PLAN_ID/buckets")
          
          # バケットID検索
          BUCKET_ID=$(echo $RESPONSE | jq -r --arg NAME "$TARGET_BUCKET_NAME" '.value[] | select(.name==$NAME) | .id')

          if [ -z "$BUCKET_ID" ] || [ "$BUCKET_ID" == "null" ]; then
            echo "❌ バケットが見つかりません。以下の一覧から名前を確認してください:"
            echo $RESPONSE | jq -r '.value[].name'
            exit 1
          fi
          echo "✅ Found Bucket ID: $BUCKET_ID"

          # 5. タスクを作成
          TASK_TITLE="${{ github.event.head_commit.message }}"
          if [ -z "$TASK_TITLE" ]; then TASK_TITLE="自動修復テストタスク"; fi

          echo "Creating task: $TASK_TITLE"
          TASK_RES=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
            -d "{
                  \"planId\": \"$PLAN_ID\",
                  \"bucketId\": \"$BUCKET_ID\",
                  \"title\": \"$TASK_TITLE\"
                }" \
            "https://graph.microsoft.com/v1.0/planner/tasks")
          
          TASK_ID=$(echo $TASK_RES | jq -r '.id')
          
          if [ -z "$TASK_ID" ] || [ "$TASK_ID" == "null" ]; then
             echo "❌ タスク作成に失敗しました。"
             echo "Response: $TASK_RES"
             exit 1
          fi
          echo "✅ Created Task ID: $TASK_ID"

          # 6. チェックリスト追加
          ETAG=$(echo $TASK_RES | jq -r '.["@odata.etag"]')
          curl -s -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
            -H "If-Match: $ETAG" \
            -d '{
                  "checklist": {
                    "95e2": { "@odata.type": "microsoft.graph.plannerChecklistItem", "title": "ネタ出し", "isChecked": true },
                    "3f8a": { "@odata.type": "microsoft.graph.plannerChecklistItem", "title": "記事（台本）", "isChecked": false },
                    "a2b1": { "@odata.type": "microsoft.graph.plannerChecklistItem", "title": "サムネイル", "isChecked": false },
                    "c4d5": { "@odata.type": "microsoft.graph.plannerChecklistItem", "title": "画像集め", "isChecked": false }
                  }
                }' \
            "https://graph.microsoft.com/v1.0/planner/tasks/$TASK_ID/details"

          echo "🎉 All Done!"
