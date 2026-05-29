GH-SG 项目部署运行教程
✨ 项目简介：本项目为自动化运维脚本合集，包含程序启动、进程监控、后台保活、环境持久化配置功能，一键部署、自动保活、稳定运行。
💡 所有命令支持一键复制，点击代码框右侧复制按钮即可直接终端粘贴执行。
---
🚀 一、主程序启动命令
进入项目目录、安装依赖、赋予执行权限并启动主程序
```bash
cd /workspaces/GH-SG/python-xray-argo && pip install -r requirements.txt && chmod +x app.py && nohup python app.py > app.log 2>&1 &
```
🔧 二、监控脚本授权命令
校验监控脚本语法、授权可执行权限，输出 ok 即授权成功
```bash
cd /workspaces/GH-SG && nohup bash -n jiankongjincheng.sh > jiankong.log 2>&1 & chmod +x jiankongjincheng.sh && echo ok
```
📊 三、启动进程监控服务
后台监控 app.py 进程，60秒轮询检测，日志输出至 monitor.log
```bash
nohup ./jiankongjincheng.sh -n "app.py" -c "python3 /workspaces/GH-SG/app.py" -l /workspaces/GH-SG/monitor.log -i 60 > monitor_daemon.log 2>&1 &
```
🛡️ 四、开启进程保活服务
赋予保活脚本权限并启动常驻保活，防止程序意外退出
```bash
cd /workspaces/GH-SG/python-xray-argo && chmod +x keep_alive.sh && nohup ./keep_alive.sh > keep_alive.log 2>&1 &
```
   五、开启自动上传服务
将sub.txt文件每次更新，自动上传至github。
```bash
cd /workspaces/GH-SG && chmod +x shangchuanusb.sh && nohup ./shangchuanusb.sh > upload.log 2>&1 &
```
   
⚙️ 六、环境持久化配置（开机自启）
将所有脚本写入系统环境配置，重启环境自动加载生效
```bash
echo "/workspaces/GH-SG/shangchuanusb.sh" >> /etc/profile
echo "/workspaces/GH-SG/jiankongjincheng.sh" >> /etc/profile
echo "/workspaces/GH-SG/keep_alive.sh" >> /etc/profile
```
---
✅ 推荐执行顺序
执行 主程序启动命令 初始化环境与依赖
执行 监控脚本授权命令赋予脚本权限
启动 进程监控服务 实时守护进程
启动 保活服务 保障程序常驻运行
配置 环境持久化 实现重启自动生效
📝 补充说明
监控间隔：默认 60秒 检测一次进程状态，可自行修改参数 -i 后数值
日志文件：所有监控日志统一输出至 `/workspaces/gh\-jd/monitor\.log`
权限问题：若执行报错，可重新运行 chmod 授权命令修复权限
持久化生效：修改 /etc/profile 后，可执行 `source /etc/profile` 立即生效
🔄 快速重载环境配置
```bash
source /etc/profile
```
