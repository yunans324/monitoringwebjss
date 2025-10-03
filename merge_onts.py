#!/usr/bin/env python3
"""
Script untuk menggabungkan data dari csvjson.json ke onts.json
Mengubah format: no -> id, ID -> id_pelanggan
Menimpa data yang sama berdasarkan id_pelanggan
"""

import json
from datetime import datetime

def load_json_file(filename):
    """Memuat file JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON dari {filename}: {e}")
        return []

def save_json_file(filename, data):
    """Menyimpan data ke file JSON"""
    try:
        # Write atomically to avoid partial writes and make a simple backup
        import os
        temp_path = f'.tmp-{filename}'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        # create backup of existing file if present
        try:
            if os.path.exists(filename):
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                backup_filename = f'onts-backup-{timestamp}.json' if filename == 'onts.json' else f'{filename}-backup-{timestamp}.json'
                with open(filename, 'r', encoding='utf-8') as oldf, open(backup_filename, 'w', encoding='utf-8') as bf:
                    bf.write(oldf.read())
                print(f"Backup dibuat: {backup_filename}")
        except Exception as e:
            print(f"Warning: gagal membuat backup: {e}")

        os.replace(temp_path, filename)
        print(f"Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"Error menyimpan ke {filename}: {e}")

def convert_csv_data(csv_data):
    """Mengkonversi data dari format CSV ke format yang diinginkan"""
    converted_data = []
    
    for item in csv_data:
        # Skip jika data tidak lengkap
        if not item.get('ID') or not item.get('Nama'):
            continue
            
        # Konversi format
        converted_item = {
            "id": item.get('no', 0),  # no -> id
            "id_pelanggan": item.get('ID', ''),  # ID -> id_pelanggan
            "name": item.get('Nama', ''),  # Nama -> name
            "lokasi": item.get('Lokasi', ''),  # Lokasi -> lokasi
            "ip": item.get('IP', ''),  # IP -> ip
            "latitude": item.get('Latitude', 0),  # Latitude -> latitude
            "longitude": item.get('Longitude', 0),  # Longitude -> longitude
            "status": "ON",  # Default status
            "rto_count": 0  # Default rto_count
        }
        
        # Konversi latitude dan longitude ke float jika string
        if isinstance(converted_item['latitude'], str) and converted_item['latitude']:
            try:
                converted_item['latitude'] = float(converted_item['latitude'])
            except ValueError:
                converted_item['latitude'] = 0
        elif not converted_item['latitude']:
            converted_item['latitude'] = 0
            
        if isinstance(converted_item['longitude'], str) and converted_item['longitude']:
            try:
                converted_item['longitude'] = float(converted_item['longitude'])
            except ValueError:
                converted_item['longitude'] = 0
        elif not converted_item['longitude']:
            converted_item['longitude'] = 0
            
        converted_data.append(converted_item)
    
    return converted_data

def merge_data(existing_data, new_data):
    """Menggabungkan data, menimpa yang sama berdasarkan id_pelanggan"""
    # Buat dictionary untuk data yang sudah ada berdasarkan id_pelanggan
    existing_dict = {item['id_pelanggan']: item for item in existing_data}
    
    # Counter untuk ID baru
    max_id = max([item['id'] for item in existing_data]) if existing_data else 0
    
    merged_data = existing_data.copy()
    added_count = 0
    updated_count = 0
    
    for new_item in new_data:
        id_pelanggan = new_item['id_pelanggan']
        
        if id_pelanggan in existing_dict:
            # Update data yang sudah ada
            existing_item = existing_dict[id_pelanggan]
            existing_item.update({
                'name': new_item['name'],
                'lokasi': new_item['lokasi'],
                'ip': new_item['ip'],
                'latitude': new_item['latitude'],
                'longitude': new_item['longitude']
            })
            updated_count += 1
            print(f"✓ Updated: {new_item['name']} ({id_pelanggan})")
        else:
            # Tambah data baru
            max_id += 1
            new_item['id'] = max_id
            merged_data.append(new_item)
            added_count += 1
            print(f"✓ Added: {new_item['name']} ({id_pelanggan})")
    
    return merged_data, added_count, updated_count

def main():
    print("=== Merge Data ONT ===\n")
    
    # Load data yang sudah ada
    print("1. Memuat data existing dari onts.json...")
    existing_data = load_json_file('onts.json')
    print(f"   Data existing: {len(existing_data)} item")
    
    # Load data dari CSV
    print("\n2. Memuat data dari csvjson.json...")
    csv_data = load_json_file('csvjson.json')
    print(f"   Data CSV: {len(csv_data)} item")
    
    if not csv_data:
        print("Tidak ada data CSV untuk diproses")
        return
    
    # Konversi format CSV
    print("\n3. Mengkonversi format data...")
    converted_data = convert_csv_data(csv_data)
    print(f"   Data yang valid: {len(converted_data)} item")
    
    # Gabungkan data
    print("\n4. Menggabungkan data...")
    merged_data, added_count, updated_count = merge_data(existing_data, converted_data)
    
    print(f"\n5. Hasil penggabungan:")
    print(f"   - Data existing: {len(existing_data)}")
    print(f"   - Data baru ditambahkan: {added_count}")
    print(f"   - Data diperbarui: {updated_count}")
    print(f"   - Total data akhir: {len(merged_data)}")
    
    # Backup data lama
    print("\n6. Membuat backup data lama...")
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_filename = f'onts-backup-{timestamp}.json'
    save_json_file(backup_filename, existing_data)
    
    # Simpan data yang sudah digabung
    print("\n7. Menyimpan data yang sudah digabung...")
    save_json_file('onts.json', merged_data)
    
    print(f"\n=== Selesai ===")
    print(f"Backup data lama: {backup_filename}")
    print(f"Data baru tersimpan di: onts.json")

if __name__ == "__main__":
    main() 