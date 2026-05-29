#!/bin/bash

echo "等待 Codespaces 网络初始化..."

sleep 15

echo "进入 python-xray-argo"

cd /workspaces/GH-SG/python-xray-argo

echo "安装依赖..."

pip install -r requirements.txt || true

echo "启动 app.py"

nohup python app.py > app.log 2>&1 &

echo "等待 .cache/sub.txt 生成..."

while [ ! -s .cache/sub.txt ]
do
    echo "sub.txt 尚未生成..."
    sleep 5
done

echo "检测到 .cache/sub.txt"

echo "返回主目录"

cd /workspaces/GH-SG

echo "给予上传脚本权限"

chmod +x shangchuanusb.sh

echo "执行上传脚本"

nohup ./shangchuanusb.sh > usb.log 2>&1 &

echo "全部任务启动完成"

