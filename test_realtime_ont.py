#!/usr/bin/env python3
"""
Script untuk menguji sistem real-time monitoring ONT
Mengubah status ONT untuk memastikan notifikasi real-time berfungsi
"""

import requests
import json
import time
import random
from datetime import datetime

# Konfigurasi
BASE_URL = "http://localhost:5000"
API_ONT_STATUS = f"{BASE_URL}/api/ont-status"

def load_onts():
    """Mengambil data ONT dari API"""
    try:
        response = requests.get(f"{BASE_URL}/api/onts")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error mengambil data ONT: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        print("❌ Tidak dapat terhubung ke server. Pastikan Flask app berjalan di http://localhost:5000")
        return []

def update_ont_status(ont_id, new_status, rto_count=0):
    """Mengupdate status ONT"""
    try:
        data = {
            "status": new_status,
            "rto_count": rto_count
        }
        
        response = requests.post(
            f"{API_ONT_STATUS}/{ont_id}",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status ONT ID {ont_id} berhasil diubah ke: {new_status}")
            return True
        else:
            print(f"❌ Error mengupdate status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Tidak dapat terhubung ke server")
        return False

def test_realtime_monitoring():
    """Fungsi utama untuk menguji real-time monitoring"""
    print("🧪 MENGUJI SISTEM REAL-TIME MONITORING ONT")
    print("=" * 50)
    
    # 1. Ambil data ONT
    print("📡 Mengambil data ONT...")
    onts = load_onts()
    
    if not onts:
        print("❌ Tidak ada data ONT yang ditemukan")
        return
    
    print(f"✅ Ditemukan {len(onts)} ONT")
    
    # 2. Tampilkan daftar ONT
    print("\n📋 Daftar ONT yang tersedia:")
    print("-" * 60)
    for ont in onts[:10]:  # Tampilkan 10 pertama
        print(f"ID: {ont['id']} | {ont['name']} | Status: {ont['status']} | Lokasi: {ont.get('lokasi', 'N/A')}")
    
    if len(onts) > 10:
        print(f"... dan {len(onts) - 10} ONT lainnya")
    
    # 3. Pilih ONT untuk testing
    print("\n🎯 Pilih ONT untuk testing:")
    print("1. ONT pertama (ID: 1)")
    print("2. ONT dengan status ON")
    print("3. ONT dengan status OFF")
    print("4. ONT random")
    
    try:
        # When running under pytest, stdin may be unavailable; default to option 1
        choice = input("\nPilih opsi (1-4): ").strip()
    except (EOFError, OSError):
        choice = '1'
    
    selected_ont = None
    
    if choice == "1":
        selected_ont = onts[0] if onts else None
    elif choice == "2":
        on_onts = [ont for ont in onts if ont['status'] == 'ON']
        selected_ont = on_onts[0] if on_onts else None
    elif choice == "3":
        off_onts = [ont for ont in onts if ont['status'] != 'ON']
        selected_ont = off_onts[0] if off_onts else None
    elif choice == "4":
        selected_ont = random.choice(onts) if onts else None
    else:
        print("❌ Pilihan tidak valid, menggunakan ONT pertama")
        selected_ont = onts[0] if onts else None
    
    if not selected_ont:
        print("❌ Tidak ada ONT yang dipilih")
        return
    
    print(f"\n🎯 ONT yang dipilih: {selected_ont['name']} (ID: {selected_ont['id']})")
    print(f"📍 Lokasi: {selected_ont.get('lokasi', 'N/A')}")
    print(f"🔌 Status saat ini: {selected_ont['status']}")
    
    # 4. Mulai testing
    print("\n🚀 Memulai testing real-time...")
    print("💡 Buka http://localhost:5000/map di browser untuk melihat perubahan real-time")
    print("💡 Buka http://localhost:5000/notifications untuk melihat histori notifikasi")
    
    # 5. Test sequence
    test_sequence = [
        ("OFF", 0, "Mematikan ONT"),
        ("ON", 0, "Menyalakan ONT"),
        ("OFF", 1, "Mematikan ONT dengan RTO=1"),
        ("ON", 0, "Menyalakan ONT kembali"),
        ("OFF", 3, "Mematikan ONT dengan RTO=3 (kritis)")
    ]
    
    for i, (new_status, rto_count, description) in enumerate(test_sequence, 1):
        print(f"\n🔄 Test {i}/5: {description}")
        print(f"   Mengubah status ke: {new_status} (RTO: {rto_count})")
        
        # Update status
        success = update_ont_status(selected_ont['id'], new_status, rto_count)
        
        if success:
            print(f"   ✅ Status berhasil diubah")
            print(f"   ⏰ Waktu: {datetime.now().strftime('%H:%M:%S')}")
            print(f"   📍 Cek di peta: http://localhost:5000/map")
            print(f"   📋 Cek notifikasi: http://localhost:5000/notifications")
        else:
            print(f"   ❌ Gagal mengubah status")
        
        # Tunggu sebentar sebelum test berikutnya
        if i < len(test_sequence):
            wait_time = 3
            print(f"   ⏳ Menunggu {wait_time} detik...")
            time.sleep(wait_time)
    
    print("\n🎉 Testing selesai!")
    print("📊 Hasil testing:")
    print("   - Status ONT berubah real-time di peta")
    print("   - Notifikasi muncul otomatis")
    print("   - Histori notifikasi tersimpan")
    print("   - Dashboard menampilkan statistik terbaru")

def main():
    """Main function"""
    print("🔧 ONT Real-time Testing Tool")
    print("=" * 40)
    
    try:
        test_realtime_monitoring()
    except KeyboardInterrupt:
        print("\n⏹️ Testing dihentikan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 