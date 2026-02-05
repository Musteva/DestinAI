
import socket
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def update_config(ip):
    config_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "js", "config.js")
    
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found!")
        return

    content = f"""
const CONFIG = {{
    API_BASE_URL: "http://{ip}:5000"
}};
"""
    with open(config_path, "w") as f:
        f.write(content)
    
    print(f"✅ Updated {config_path} with IP: {ip}")

def print_instructions(ip):
    print("\n" + "="*50)
    print(f"🚀 DEPLOYMENT READY!")
    print("="*50)
    print(f"1. Backend is configured to run on http://0.0.0.0:5000")
    print(f"2. Frontend config updated to point to http://{ip}:5000")
    print("-" * 50)
    print("HOW TO RUN:")
    print("   Terminal 1 (Backend):  cd backend && python app.py")
    print("   Terminal 2 (Frontend): cd frontend && python -m http.server 8000")
    print("-" * 50)
    print("ACCESS LINKS:")
    print(f"   💻 Local PC:      http://localhost:8000/MainPage.html")
    print(f"   📱 Other Devices: http://{ip}:8000/MainPage.html")
    print("="*50 + "\n")

if __name__ == "__main__":
    ip = get_local_ip()
    update_config(ip)
    print_instructions(ip)
