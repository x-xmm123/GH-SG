import os
import re
import json
import time
import base64
import shutil
import asyncio
import requests
import platform
import socket
import subprocess
import threading
import hashlib
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# Environment variables
UPLOAD_URL = os.environ.get('UPLOAD_URL', '')
PROJECT_URL = os.environ.get('PROJECT_URL', '')
AUTO_ACCESS = os.environ.get('AUTO_ACCESS', 'false').lower() == 'true'
FILE_PATH = os.environ.get('FILE_PATH', '.cache')
SUB_PATH = os.environ.get('SUB_PATH', 'sub')
UUID = os.environ.get('UUID', '20e6e496-cf19-45c8-b883-14f5e11cd9f1')
NEZHA_SERVER = os.environ.get('NEZHA_SERVER', '')
NEZHA_PORT = os.environ.get('NEZHA_PORT', '')
NEZHA_KEY = os.environ.get('NEZHA_KEY', '')
ARGO_DOMAIN = os.environ.get('ARGO_DOMAIN', '')
ARGO_AUTH = os.environ.get('ARGO_AUTH', '')
ARGO_PORT = int(os.environ.get('ARGO_PORT', '8001'))
CFIP = os.environ.get('CFIP', 'saas.sin.fan')
CFPORT = int(os.environ.get('CFPORT', '443'))
NAME = os.environ.get('NAME', '')
CHAT_ID = os.environ.get('CHAT_ID', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
DEFAULT_PORT = int(os.environ.get('SERVER_PORT') or os.environ.get('PORT') or 3000)
PORT = DEFAULT_PORT

# GitHub upload config
GITHUB_OWNER = os.environ.get('GITHUB_OWNER', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')
GITHUB_BRANCH = os.environ.get('GITHUB_BRANCH', 'main')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_FILE_NAME = os.environ.get('GITHUB_FILE_NAME', 'sub.txt')


def get_available_port(preferred_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', preferred_port))
            return preferred_port
        except OSError:
            sock.bind(('0.0.0.0', 0))
            return sock.getsockname()[1]


# Create running folder
def create_directory():
    print('\033c', end='')
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
        print(f"{FILE_PATH} is created")
    else:
        print(f"{FILE_PATH} already exists")


# Global variables
npm_path = os.path.join(FILE_PATH, 'npm')
php_path = os.path.join(FILE_PATH, 'php')
web_path = os.path.join(FILE_PATH, 'web')
bot_path = os.path.join(FILE_PATH, 'bot')
sub_path = os.path.join(FILE_PATH, 'sub.txt')
list_path = os.path.join(FILE_PATH, 'list.txt')
boot_log_path = os.path.join(FILE_PATH, 'boot.log')
config_path = os.path.join(FILE_PATH, 'config.json')


# Delete nodes
def delete_nodes():
    try:
        if not UPLOAD_URL:
            return
        if not os.path.exists(sub_path):
            return
        try:
            with open(sub_path, 'r') as file:
                file_content = file.read()
        except:
            return None
        decoded = base64.b64decode(file_content).decode('utf-8')
        nodes = [line for line in decoded.split('\n') if any(protocol in line for protocol in ['vless://', 'vmess://', 'trojan://', 'hysteria2://', 'tuic://'])]
        if not nodes:
            return
        try:
            requests.post(f"{UPLOAD_URL}/api/delete-nodes", data=json.dumps({"nodes": nodes}), headers={"Content-Type": "application/json"})
        except:
            return None
    except Exception as e:
        print(f"Error in delete_nodes: {e}")
        return None


# Clean up old files (including old sub.txt)
def cleanup_old_files():
    paths_to_delete = ['web', 'bot', 'npm', 'php', 'boot.log', 'list.txt', 'sub.txt']
    for file in paths_to_delete:
        file_path = os.path.join(FILE_PATH, file)
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Hello World')
        elif self.path == f'/{SUB_PATH}':
            try:
                with open(sub_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


# Determine system architecture
def get_system_architecture():
    architecture = platform.machine().lower()
    if 'arm' in architecture or 'aarch64' in architecture:
        return 'arm'
    else:
        return 'amd'


# Download file based on architecture
def download_file(file_name, file_url):
    file_path = os.path.join(FILE_PATH, file_name)
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Download {file_name} successfully")
        return True
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Download {file_name} failed: {e}")
        return False


# Get files for architecture
def get_files_for_architecture(architecture):
    if architecture == 'arm':
        base_files = [
            {"fileName": "web", "fileUrl": "https://arm64.ssss.nyc.mn/web"},
            {"fileName": "bot", "fileUrl": "https://arm64.ssss.nyc.mn/2go"}
        ]
    else:
        base_files = [
            {"fileName": "web", "fileUrl": "https://amd64.ssss.nyc.mn/web"},
            {"fileName": "bot", "fileUrl": "https://amd64.ssss.nyc.mn/2go"}
        ]
    if NEZHA_SERVER and NEZHA_KEY:
        if NEZHA_PORT:
            npm_url = "https://arm64.ssss.nyc.mn/agent" if architecture == 'arm' else "https://amd64.ssss.nyc.mn/agent"
            base_files.insert(0, {"fileName": "npm", "fileUrl": npm_url})
        else:
            php_url = "https://arm64.ssss.nyc.mn/v1" if architecture == 'arm' else "https://amd64.ssss.nyc.mn/v1"
            base_files.insert(0, {"fileName": "php", "fileUrl": php_url})
    return base_files


# Authorize files with execute permission
def authorize_files(file_paths):
    for relative_file_path in file_paths:
        absolute_file_path = os.path.join(FILE_PATH, relative_file_path)
        if os.path.exists(absolute_file_path):
            try:
                os.chmod(absolute_file_path, 0o775)
                print(f"Empowerment success for {absolute_file_path}: 775")
            except Exception as e:
                print(f"Empowerment failed for {absolute_file_path}: {e}")


# Configure Argo tunnel
def argo_type():
    if not ARGO_AUTH or not ARGO_DOMAIN:
        print("ARGO_DOMAIN or ARGO_AUTH variable is empty, use quick tunnels")
        return
    if "TunnelSecret" in ARGO_AUTH:
        with open(os.path.join(FILE_PATH, 'tunnel.json'), 'w') as f:
            f.write(ARGO_AUTH)
        tunnel_id = ARGO_AUTH.split('"')[11]
        tunnel_yml = f"""
tunnel: {tunnel_id}
credentials-file: {os.path.join(FILE_PATH, 'tunnel.json')}
protocol: http2

ingress:
  - hostname: {ARGO_DOMAIN}
    service: http://localhost:{ARGO_PORT}
    originRequest:
      noTLSVerify: true
  - service: http_status:404
"""
        with open(os.path.join(FILE_PATH, 'tunnel.yml'), 'w') as f:
            f.write(tunnel_yml)
    else:
        print("Use token connect to tunnel,please set the {ARGO_PORT} in cloudflare")


# Execute shell command and return output
def exec_cmd(command):
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return stdout + stderr
    except Exception as e:
        print(f"Error executing command: {e}")
        return str(e)


# Upload sub.txt to GitHub (converted from Bash script)
def upload_sub_txt_to_github():
    """
    将本地 sub.txt 上传到 GitHub 指定仓库。
    - 如果 GITHUB_TOKEN 为空则跳过
    - 如果本地 sub.txt 不存在则跳过
    - 如果云端文件与本地相同则跳过
    - 否则创建或更新文件
    """
    if not GITHUB_TOKEN or not GITHUB_OWNER or not GITHUB_REPO:
        print("ℹ️ GitHub 配置不完整，跳过 GitHub 上传")
        return

    if not os.path.exists(sub_path):
        print("⚠️ 本地 sub.txt 不存在，跳过 GitHub 上传")
        return

    # 1. 读取本地文件 & 计算 git blob SHA
    with open(sub_path, "rb") as f:
        file_bytes = f.read()

    size = len(file_bytes)
    sha1 = hashlib.sha1()
    sha1.update(f"blob {size}\0".encode())
    sha1.update(file_bytes)
    local_sha = sha1.hexdigest()

    # 2. 获取云端文件信息
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_FILE_NAME}?ref={GITHUB_BRANCH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    remote_sha = ""
    try:
        resp = requests.get(api_url, headers=headers)
        if resp.status_code == 200:
            remote_sha = resp.json().get("sha", "")
        else:
            remote_sha = ""
    except Exception as e:
        print(f"⚠️ 获取 GitHub 文件信息失败: {e}")
        remote_sha = ""

    # 3. 判断是否需要上传
    if remote_sha and local_sha == remote_sha:
        print("✅ GitHub 上文件与本地相同，跳过上传")
        return

    print("🔄 文件已修改或是新文件，开始 GitHub 上传...")

    # 4. 构造提交信息 & base64 内容
    commit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"北京 {commit_time}"
    content = base64.b64encode(file_bytes).decode("utf-8")

    # 5. 构造请求体
    data = {
        "message": message,
        "content": content,
        "branch": GITHUB_BRANCH,
    }
    if remote_sha:
        data["sha"] = remote_sha
        print("🔄 GitHub 上该文件已过期，进行覆盖...")
    else:
        print("📝 GitHub 上没有该文件，创建新文件...")

    # 6. 发起 PUT 请求
    try:
        resp = requests.put(api_url, headers=headers, data=json.dumps(data))
        if resp.status_code in (200, 201):
            print("✅ GitHub 上传成功！")
        else:
            print(f"❌ GitHub 上传失败: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ GitHub 上传异常: {e}")


# Download and run necessary files
async def download_files_and_run():
    global private_key, public_key
    architecture = get_system_architecture()
    files_to_download = get_files_for_architecture(architecture)
    if not files_to_download:
        print("Can't find a file for the current architecture")
        return

    # Download all files
    download_success = True
    for file_info in files_to_download:
        if not download_file(file_info["fileName"], file_info["fileUrl"]):
            download_success = False
    if not download_success:
        print("Error downloading files")
        return

    # Authorize files
    files_to_authorize = ['npm', 'web', 'bot'] if NEZHA_PORT else ['php', 'web', 'bot']
    authorize_files(files_to_authorize)

    # Check TLS
    port = NEZHA_SERVER.split(":")[-1] if ":" in NEZHA_SERVER else ""
    if port in ["443", "8443", "2096", "2087", "2083", "2053"]:
        nezha_tls = "true"
    else:
        nezha_tls = "false"

    # Configure nezha
    if NEZHA_SERVER and NEZHA_KEY:
        if not NEZHA_PORT:
            # Generate config.yaml for v1
            config_yaml = f"""
client_secret: {NEZHA_KEY}
debug: false
disable_auto_update: true
disable_command_execute: false
disable_force_update: true
disable_nat: false
disable_send_query: false
gpu: false
insecure_tls: false
ip_report_period: 1800
report_delay: 4
server: {NEZHA_SERVER}
skip_connection_count: false
skip_procs_count: false
temperature: false
tls: {nezha_tls}
use_gitee_to_upgrade: false
use_ipv6_country_code: false
uuid: {UUID}"""
            with open(os.path.join(FILE_PATH, 'config.yaml'), 'w') as f:
                f.write(config_yaml)

    # Generate configuration file
    config = {
        "log": {
            "access": "/dev/null",
            "error": "/dev/null",
            "loglevel": "none",
        },
        "inbounds": [
            {
                "port": ARGO_PORT,
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": UUID, "flow": "xtls-rprx-vision"}],
                    "decryption": "none",
                    "fallbacks": [
                        {"dest": 3001},
                        {"path": "/vless-argo", "dest": 3002},
                        {"path": "/vmess-argo", "dest": 3003},
                        {"path": "/trojan-argo", "dest": 3004},
                    ],
                },
                "streamSettings": {"network": "tcp"},
            },
            {
                "port": 3001,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {"clients": [{"id": UUID}], "decryption": "none"},
                "streamSettings": {"network": "ws", "security": "none"},
            },
            {
                "port": 3002,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {"clients": [{"id": UUID, "level": 0}], "decryption": "none"},
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {"path": "/vless-argo"},
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls", "quic"],
                    "metadataOnly": False,
                },
            },
            {
                "port": 3003,
                "listen": "127.0.0.1",
                "protocol": "vmess",
                "settings": {"clients": [{"id": UUID, "alterId": 0}]},
                "streamSettings": {
                    "network": "ws",
                    "wsSettings": {"path": "/vmess-argo"},
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls", "quic"],
                    "metadataOnly": False,
                },
            },
            {
                "port": 3004,
                "listen": "127.0.0.1",
                "protocol": "trojan",
                "settings": {"clients": [{"password": UUID}]},
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {"path": "/trojan-argo"},
                },
                "sniffing": {
                    "enabled": True,
                    "destOverride": ["http", "tls", "quic"],
                    "metadataOnly": False,
                },
            },
        ],
        "outbounds": [
            {"protocol": "freedom", "tag": "direct"},
            {"protocol": "blackhole", "tag": "block"},
        ],
    }
    with open(os.path.join(FILE_PATH, 'config.json'), 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, ensure_ascii=False, indent=2)

    # Run nezha
    if NEZHA_SERVER and NEZHA_PORT and NEZHA_KEY:
        tls_ports = ['443', '8443', '2096', '2087', '2083', '2053']
        nezha_tls = '--tls' if NEZHA_PORT in tls_ports else ''
        command = f"nohup {os.path.join(FILE_PATH, 'npm')} -s {NEZHA_SERVER}:{NEZHA_PORT} -p {NEZHA_KEY} {nezha_tls} >/dev/null 2>&1 &"
        try:
            exec_cmd(command)
            print('npm is running')
            time.sleep(1)
        except Exception as e:
            print(f"npm running error: {e}")
    elif NEZHA_SERVER and NEZHA_KEY:
        command = f"nohup {FILE_PATH}/php -c \"{FILE_PATH}/config.yaml\" >/dev/null 2>&1 &"
        try:
            exec_cmd(command)
            print('php is running')
            time.sleep(1)
        except Exception as e:
            print(f"php running error: {e}")
    else:
        print('NEZHA variable is empty, skipping running')

    # Run sbX
    command = f"nohup {os.path.join(FILE_PATH, 'web')} -c {os.path.join(FILE_PATH, 'config.json')} >/dev/null 2>&1 &"
    try:
        exec_cmd(command)
        print('web is running')
        time.sleep(1)
    except Exception as e:
        print(f"web running error: {e}")

    # Run cloudflared
    if os.path.exists(os.path.join(FILE_PATH, 'bot')):
        if re.match(r'^[A-Z0-9a-z=]{120,250}$', ARGO_AUTH):
            args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 run --token {ARGO_AUTH}"
        elif "TunnelSecret" in ARGO_AUTH:
            args = f"tunnel --edge-ip-version auto --config {os.path.join(FILE_PATH, 'tunnel.yml')} run"
        else:
            args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {os.path.join(FILE_PATH, 'boot.log')} --loglevel info --url http://localhost:{ARGO_PORT}"
        try:
            exec_cmd(f"nohup {os.path.join(FILE_PATH, 'bot')} {args} >/dev/null 2>&1 &")
            print('bot is running')
            time.sleep(2)
        except Exception as e:
            print(f"Error executing command: {e}")

    time.sleep(5)

    # Extract domains and generate sub.txt
    await extract_domains()


# Extract domains from cloudflared logs
async def extract_domains():
    argo_domain = None
    if ARGO_AUTH and ARGO_DOMAIN:
        argo_domain = ARGO_DOMAIN
        print(f'ARGO_DOMAIN: {argo_domain}')
        await generate_links(argo_domain)
    else:
        try:
            with open(boot_log_path, 'r') as f:
                file_content = f.read()
            lines = file_content.split('\n')
            argo_domains = []
            for line in lines:
                domain_match = re.search(r'https?://([^ ]*trycloudflare\.com)/?', line)
                if domain_match:
                    domain = domain_match.group(1)
                    argo_domains.append(domain)
            if argo_domains:
                argo_domain = argo_domains[0]
                print(f'ArgoDomain: {argo_domain}')
                await generate_links(argo_domain)
            else:
                print('ArgoDomain not found, re-running bot to obtain ArgoDomain')
                # Remove boot.log and restart bot
                if os.path.exists(boot_log_path):
                    os.remove(boot_log_path)
                try:
                    exec_cmd('pkill -f "[b]ot" > /dev/null 2>&1')
                except:
                    pass
                time.sleep(1)
                args = f'tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {FILE_PATH}/boot.log --loglevel info --url http://localhost:{ARGO_PORT}'
                exec_cmd(f'nohup {os.path.join(FILE_PATH, "bot")} {args} >/dev/null 2>&1 &')
                print('bot is running.')
                time.sleep(6)
                await extract_domains()
        except Exception as e:
            print(f'Error reading boot.log: {e}')


# Upload nodes to subscription service
def upload_nodes():
    if UPLOAD_URL and PROJECT_URL:
        subscription_url = f"{PROJECT_URL}/{SUB_PATH}"
        json_data = {
            "subscription": [subscription_url]
        }
        try:
            response = requests.post(
                f"{UPLOAD_URL}/api/add-subscriptions",
                json=json_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print('Subscription uploaded successfully')
        except Exception as e:
            pass
    elif UPLOAD_URL:
        if not os.path.exists(list_path):
            return
        with open(list_path, 'r') as f:
            content = f.read()
        nodes = [line for line in content.split('\n') if any(protocol in line for protocol in ['vless://', 'vmess://', 'trojan://', 'hysteria2://', 'tuic://'])]
        if not nodes:
            return
        json_data = json.dumps({"nodes": nodes})
        try:
            response = requests.post(
                f"{UPLOAD_URL}/api/add-nodes",
                data=json_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print('Nodes uploaded successfully')
        except:
            return None
    else:
        return


# Send notification to Telegram
def send_telegram():
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        with open(sub_path, 'r') as f:
            message = f.read()
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        escaped_name = re.sub(r'([_*\[\]()~>#+=|{}.!\-])', r'\\\1', NAME)
        params = {
            "chat_id": CHAT_ID,
            "text": f"**{escaped_name}节点推送通知**\n{message}",
            "parse_mode": "MarkdownV2"
        }
        requests.post(url, params=params)
        print('Telegram message sent successfully')
    except Exception as e:
        print(f'Failed to send Telegram message: {e}')


# Generate links and subscription content
async def generate_links(argo_domain):
    meta_info = subprocess.run(
        ['curl', '-sm', '5', '-H', 'User-Agent: Mozilla/5.0', 'https://api.ip.sb/geoip'],
        capture_output=True, text=True
    )
    geo_data = json.loads(meta_info.stdout)
    country_code = geo_data.get('country_code', 'Unknown')
    isp = geo_data.get('isp', 'Unknown').replace(' ', '_').strip()

    if NAME and NAME.strip():
        ISP = f"{country_code}_{NAME.strip()}"
    else:
        ISP = f"{country_code}_{isp}"

    time.sleep(2)

    VMESS = {
        "v": "2", "ps": f"{ISP}", "add": CFIP, "port": CFPORT,
        "id": UUID, "aid": "0", "scy": "none", "net": "ws",
        "type": "none", "host": argo_domain, "path": "/vmess-argo?ed=2560",
        "tls": "tls", "sni": argo_domain, "alpn": "", "fp": "chrome"
    }

    list_txt = f"""
vless://{UUID}@openai.com:{CFPORT}?encryption=none&security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Fvless-argo%3Fed%3D2560#{ISP}
vmess://{base64.b64encode(json.dumps(VMESS).encode('utf-8')).decode('utf-8')}
trojan://{UUID}@5h.com:{CFPORT}?security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Ftrojan-argo%3Fed%3D2560#{ISP}
"""

    with open(os.path.join(FILE_PATH, 'list.txt'), 'w', encoding='utf-8') as list_file:
        list_file.write(list_txt)

    sub_txt = base64.b64encode(list_txt.encode('utf-8')).decode('utf-8')

    with open(sub_path, 'w', encoding='utf-8') as sub_file:
        sub_file.write(sub_txt)

    print(sub_txt)
    print(f"{FILE_PATH}/sub.txt saved successfully")

    # Additional actions
    send_telegram()
    upload_nodes()

    # Upload sub.txt to GitHub (only after new sub.txt is written)
    upload_sub_txt_to_github()

    return sub_txt


# Add automatic access task
def add_visit_task():
    if not AUTO_ACCESS or not PROJECT_URL:
        print("Skipping adding automatic access task")
        return
    try:
        response = requests.post(
            'https://keep.gvrander.eu.org/add-url',
            json={"url": PROJECT_URL},
            headers={"Content-Type": "application/json"}
        )
        print('automatic access task added successfully')
    except Exception as e:
        print(f"Failed to add URL: {e}")


# Clean up files after 90 seconds
def clean_files():
    def _cleanup():
        time.sleep(90)
        files_to_delete = [boot_log_path, config_path, list_path, web_path, bot_path, php_path, npm_path]
        if NEZHA_PORT:
            files_to_delete.append(npm_path)
        elif NEZHA_SERVER and NEZHA_KEY:
            files_to_delete.append(php_path)
        for file in files_to_delete:
            try:
                if os.path.exists(file):
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    else:
                        os.remove(file)
            except:
                pass
        print('\033c', end='')
        print('App is running')
        print('Thank you for using this script, enjoy!')

    threading.Thread(target=_cleanup, daemon=True).start()


# Main function to start the server
async def start_server():
    delete_nodes()       # 1. 先用旧 sub.txt 删除节点
    cleanup_old_files()  # 2. 清理旧文件（包括旧的 sub.txt）
    create_directory()   # 3. 创建目录
    argo_type()
    await download_files_and_run()  # 4. 下载运行，最终在 generate_links() 中生成新 sub.txt 并上传 GitHub
    add_visit_task()

    global PORT
    new_port = get_available_port(PORT)
    if new_port != PORT:
        print(f"Port {PORT} is unavailable, switched to available port {new_port}")
        PORT = new_port

    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    clean_files()


def run_server():
    server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
    print(f"Server is running on port {PORT}")
    print(f"Running done！")
    print(f"\nLogs will be delete in 90 seconds,you can copy the above nodes!")
    server.serve_forever()


def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    run_async()
