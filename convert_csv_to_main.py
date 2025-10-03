#!/usr/bin/env python3
"""
Script untuk mengkonversi csvjson.json menjadi file utama onts.json
Menggantikan data sebelumnya dengan data dari CSV
"""

import json
from datetime import datetime

def load_csv_data():
    """Memuat data dari csvjson.json"""
    try:
        with open('csvjson.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("File csvjson.json tidak ditemukan")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON dari csvjson.json: {e}")
        return []

def convert_csv_to_onts_format(csv_data):
    """Mengkonversi data CSV ke format ONT yang sesuai"""
    converted_data = []
    
    print("Mengkonversi data CSV ke format ONT...")
    
    for index, item in enumerate(csv_data, 1):
        # Skip jika data tidak lengkap
        if not item.get('ID') or not item.get('Nama'):
            print(f"  ⚠️  Skip item {index}: data tidak lengkap")
            continue
            
        # Konversi format
        converted_item = {
            "id": index,  # ID baru berurutan
            "id_pelanggan": item.get('ID', '').strip(),  # ID -> id_pelanggan
            "name": item.get('Nama', '').strip(),  # Nama -> name
            "lokasi": item.get('Lokasi', '').strip(),  # Lokasi -> lokasi
            "ip": item.get('IP', '').strip(),  # IP -> ip
            "latitude": 0,  # Default latitude
            "longitude": 0,  # Default longitude
            "status": "ON",  # Default status
            "rto_count": 0  # Default rto_count
        }
        
        # Konversi latitude dan longitude
        lat = item.get('Latitude', '')
        lon = item.get('Longitude', '')
        
        if lat and str(lat).strip():
            try:
                converted_item['latitude'] = float(str(lat).strip())
            except ValueError:
                print(f"  ⚠️  Latitude invalid untuk item {index}: {lat}")
                converted_item['latitude'] = 0
        else:
            converted_item['latitude'] = 0
            
        if lon and str(lon).strip():
            try:
                converted_item['longitude'] = float(str(lon).strip())
            except ValueError:
                print(f"  ⚠️  Longitude invalid untuk item {index}: {lon}")
                converted_item['longitude'] = 0
        else:
            converted_item['longitude'] = 0
        
        converted_data.append(converted_item)
        print(f"  ✓ Item {index}: {converted_item['name']} ({converted_item['id_pelanggan']})")
    
    return converted_data

def backup_existing_data():
    """Membuat backup data existing"""
    try:
        with open('onts.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_filename = f'onts-backup-before-csv-{timestamp}.json'
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Backup data existing: {backup_filename}")
        return len(existing_data)
    except FileNotFoundError:
        print("ℹ️  File onts.json tidak ditemukan, tidak ada backup yang dibuat")
        return 0
    except Exception as e:
        print(f"⚠️  Error membuat backup: {e}")
        return 0

def save_new_data(data):
    """Menyimpan data baru ke onts.json"""
    try:
        # Tulis ke file sementara lalu replace untuk mencegah file korup/otomatis menimpa tanpa backup
        import os
        temp_path = '.tmp-onts.json'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        # Buat backup otomatis dari file lama jika ada
        try:
            if os.path.exists('onts.json'):
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                backup_filename = f'onts-backup-before-csv-{timestamp}.json'
                with open('onts.json', 'r', encoding='utf-8') as oldf, open(backup_filename, 'w', encoding='utf-8') as bf:
                    bf.write(oldf.read())
                print(f"✓ Backup existing dibuat: {backup_filename}")
        except Exception as e:
            print(f"⚠️  Gagal membuat backup sebelum menyimpan: {e}")

        os.replace(temp_path, 'onts.json')
        print(f"✓ Data baru tersimpan ke onts.json")
        return True
    except Exception as e:
        print(f"❌ Error menyimpan data: {e}")
        return False

def validate_data(data):
    """Validasi data yang sudah dikonversi"""
    print("\n=== Validasi Data ===")
    
    # Statistik umum
    total_items = len(data)
    valid_coords = len([item for item in data if item['latitude'] != 0 and item['longitude'] != 0])
    valid_ips = len([item for item in data if item['ip'].strip()])
    unique_ids = len(set(item['id_pelanggan'] for item in data))
    
    print(f"Total item: {total_items}")
    print(f"Item dengan koordinat valid: {valid_coords}")
    print(f"Item dengan IP: {valid_ips}")
    print(f"Unique ID Pelanggan: {unique_ids}")
    
    # Cek duplikat
    id_pelanggan_list = [item['id_pelanggan'] for item in data]
    duplicates = [x for x in set(id_pelanggan_list) if id_pelanggan_list.count(x) > 1]
    
    if duplicates:
        print(f"⚠️  Ditemukan {len(duplicates)} ID Pelanggan yang duplikat:")
        for dup in duplicates[:10]:  # Tampilkan 10 pertama
            print(f"  - {dup}")
        if len(duplicates) > 10:
            print(f"  ... dan {len(duplicates) - 10} lainnya")
    else:
        print("✅ Tidak ada ID Pelanggan yang duplikat")
    
    # Cek data dengan koordinat 0,0
    invalid_coords = [item for item in data if item['latitude'] == 0 and item['longitude'] == 0]
    if invalid_coords:
        print(f"⚠️  {len(invalid_coords)} item dengan koordinat 0,0 (mungkin perlu diperbaiki)")
    
    # Cek data dengan IP kosong
    empty_ips = [item for item in data if not item['ip'].strip()]
    if empty_ips:
        print(f"⚠️  {len(empty_ips)} item dengan IP kosong")

def main():
    print("=== Konversi CSV ke File Utama ===\n")
    
    # 1. Backup data existing
    print("1. Membuat backup data existing...")
    existing_count = backup_existing_data()
    
    # 2. Load data CSV
    print("\n2. Memuat data dari csvjson.json...")
    csv_data = load_csv_data()
    if not csv_data:
        print("❌ Tidak ada data CSV untuk diproses")
        return
    
    print(f"   Data CSV: {len(csv_data)} item")
    
    # 3. Konversi format
    print("\n3. Mengkonversi format data...")
    converted_data = convert_csv_to_onts_format(csv_data)
    print(f"   Data yang berhasil dikonversi: {len(converted_data)} item")
    
    # 4. Validasi data
    validate_data(converted_data)
    
    # 5. Simpan data baru
    print("\n4. Menyimpan data baru...")
    if save_new_data(converted_data):
        print("\n=== Konversi Berhasil ===")
        print(f"Data CSV ({len(csv_data)} item) berhasil dikonversi menjadi {len(converted_data)} item")
        print("File onts.json telah diperbarui dengan data dari CSV")
        
        if existing_count > 0:
            print(f"Data existing ({existing_count} item) telah di-backup")
    else:
        print("\n❌ Konversi gagal")

if __name__ == "__main__":
    main() 