#!/usr/bin/env python3
"""
Script sederhana untuk testing ping ke beberapa IP
Membantu debug masalah ping di sistem monitoring ONT
"""

import platform
import subprocess
import time

def ping_simple(ip):
    """Ping helper: jalankan ping sederhana ke IP tertentu dan kembalikan bool sukses"""
    print(f"🔍 Testing ping ke {ip}...")
    
    try:
        if platform.system().lower() == "windows":
            command = f"ping -n 1 -w 1000 {ip}"
        else:
            command = f"ping -c 1 -W 1 {ip}"
        
        print(f"📡 Command: {command}")
        
        # Jalankan ping
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        print(f"📤 Exit Code: {result.returncode}")
        print(f"📥 Output:")
        print("-" * 40)
        print(result.stdout)
        print("-" * 40)
        
        # Analisis hasil
        if platform.system().lower() == "windows":
            if "Reply from" in result.stdout or "bytes=" in result.stdout:
                print("✅ PING BERHASIL - IP merespons")
                return True
            else:
                print("❌ PING GAGAL - IP tidak merespons")
                return False
        else:
            if result.returncode == 0:
                print("✅ PING BERHASIL - IP merespons")
                return True
            else:
                print("❌ PING GAGAL - IP tidak merespons")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_local_network():
    """Test ping ke jaringan lokal"""
    print("🌐 TESTING PING KE JARINGAN LOKAL")
    print("=" * 50)
    
    # Test IP lokal
    local_ips = [
        "127.0.0.1",        # Loopback
        "192.168.1.1",      # Router umum
        "10.0.0.1",         # Router alternatif
        "8.8.8.8",          # Google DNS
        "1.1.1.1"           # Cloudflare DNS
    ]
    
    for ip in local_ips:
        print(f"\n📍 Testing {ip}:")
        success = ping_simple(ip)
        time.sleep(1)  # Jeda antar ping

def test_ont_ips():
    """Test ping ke IP dari data ONT"""
    print("\n📡 TESTING PING KE IP ONT")
    print("=" * 50)
    
    try:
        import json
        
        # Baca file onts.json
        with open("onts.json", "r", encoding='utf-8') as f:
            onts = json.load(f)
        
        print(f"📋 Ditemukan {len(onts)} ONT")
        
        # Test beberapa IP pertama
        test_count = min(5, len(onts))  # Test maksimal 5 IP
        
        for i in range(test_count):
            ont = onts[i]
            ip = ont.get('ip', '')
            name = ont.get('name', 'Unknown')
            
            if ip and ip.strip():
                print(f"\n🔍 Testing ONT: {name} ({ip})")
                success = ping_simple(ip)
                time.sleep(2)  # Jeda lebih lama untuk IP eksternal
            else:
                print(f"⚠️  {name}: IP kosong, skip")
                
    except FileNotFoundError:
        print("❌ File onts.json tidak ditemukan")
    except json.JSONDecodeError:
        print("❌ File onts.json tidak valid")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🧪 PING TESTING TOOL")
    print("=" * 50)
    print(f"🖥️  OS: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    print("=" * 50)
    
    # Test 1: Ping jaringan lokal
    test_local_network()
    
    # Test 2: Ping IP ONT
    test_ont_ips()
    
    print("\n🎯 TESTING SELESAI!")
    print("💡 Jika ping lokal berhasil tapi ONT gagal, kemungkinan:")
    print("   - IP ONT tidak valid")
    print("   - Firewall memblokir")
    print("   - Jaringan tidak terhubung")
    print("   - IP berada di subnet yang berbeda")

if __name__ == "__main__":
    main()
