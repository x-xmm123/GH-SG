#!/bin/bash

LOCAL_FILE="/workspaces/GH-SG/python-xray-argo/.cache/sub.txt"
OWNER="xxsa520"
REPO="GH-SG"
BRANCH="main"
TOKEN="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"
FILE_NAME="sub.txt"

# 1. 获取云端文件完整信息
API_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/contents/$FILE_NAME?ref=$BRANCH")

# 2. 提取 SHA（如果文件不存在则为空）
SHA=$(echo "$API_RESPONSE" | python3 -c "import json,sys;obj=json.load(sys.stdin);print(obj.get('sha',''))" 2>/dev/null || echo "")

# 3. 计算本地 SHA
size=$(stat -c %s "$LOCAL_FILE")
local_sha=$( (echo -n "blob $size"; echo -ne "\0"; cat "$LOCAL_FILE") | sha1sum | awk '{print $1}')

# 4. 判断是否需要上传
if [ -n "$SHA" ] && [ "$local_sha" = "$SHA" ]; then
  echo "✅ 文件未修改，跳过上传"
  exit 0
fi

echo "🔄 文件已修改或是新文件，开始上传..."

# 5. 上传（稳定格式）
COMMIT_TIME=$(TZ=Asia/Shanghai date "+%Y-%m-%d %H:%M:%S")
CONTENT=$(base64 -w 0 "$LOCAL_FILE")

# 构建 JSON 数据
if [ -z "$SHA" ]; then
  # 新文件，不提供 sha 字段
  JSON_DATA='{
    "message":"北京 '"$COMMIT_TIME"'",
    "content":"'"$CONTENT"'",
    "branch":"'"$BRANCH"'"
  }'
  echo "📝 GitHub 上没有该文件，创建新文件..."
else
  # 文件存在但已修改，提供 sha 字段用于覆盖
  JSON_DATA='{
    "message":"北京 '"$COMMIT_TIME"'",
    "content":"'"$CONTENT"'",
    "sha":"'"$SHA"'",
    "branch":"'"$BRANCH"'"
  }'
  echo "🔄 GitHub 上该文件已过期，进行覆盖..."
fi

curl -s -X PUT \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$JSON_DATA" \
  "https://api.github.com/repos/$OWNER/$REPO/contents/$FILE_NAME"

echo -e "\n✅ 上传成功！"
