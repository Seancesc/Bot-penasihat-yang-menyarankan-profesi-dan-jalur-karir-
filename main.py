import json

with open("database.json", "r", encoding="utf-8") as file:
    data = json.load(file)

minat_input = input("Apa minatmu? (pisahkan dengan koma): ")

# Ubah input menjadi huruf kecil
minat_user = [m.strip().lower() for m in minat_input.split(",")]

hasil = []

for profesi in data:
    minat_profesi = [m.lower() for m in profesi["minat"]]

    # Hitung berapa minat yang cocok
    skor = sum(
        1 for minat in minat_user
        if minat in minat_profesi
    )

    if skor > 0:
        hasil.append((skor, profesi["nama"]))

# Urutkan dari skor tertinggi ke terendah
hasil.sort(reverse=True)

if hasil:
    print("\n Rekomendasi Karir:\n")

    for skor, nama in hasil:
        print(f" {nama} ({skor} minat cocok)")
else:
    print(" Maaf, belum ada profesi yang cocok dengan minat tersebut.")