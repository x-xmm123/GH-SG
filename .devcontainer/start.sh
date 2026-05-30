#!/bin/bash

echo "启动入口触发: $(date)"

cd /workspaces/GH-SG/python-xray-argo || exit 1

mkdir -p .cache

# ===== 防止重复启动 app.py =====
if pgrep -f "app.py" > /dev/null; then
    echo "app.py 已在运行，跳过启动"
else
    echo "启动 app.py"
    nohup python app.py > app.log 2>&1 &
fi

# ===== 等待 sub.txt（带超时更安全）=====
TIMEOUT=600
COUNT=0

while [ ! -s .cache/sub.txt ]; do
    echo "等待 sub.txt..."
    sleep 5
    COUNT=$((COUNT+5))

    if [ $COUNT -ge $TIMEOUT ]; then
        echo "超时，退出等待"
        exit 1
    fi
done

echo "sub.txt 已生成"

# ===== 防止重复上传 =====
if pgrep -f "shangchuanusb.sh" > /dev/null; then
    echo "上传脚本已运行，跳过"
else
    cd /workspaces/GH-SG
    chmod +x shangchuanusb.sh
    nohup ./shangchuanusb.sh > usb.log 2>&1 &
fi

echo "启动流程完成"
