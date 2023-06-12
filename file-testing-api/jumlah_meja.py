dataJumlahMeja = 10
jumlahMeja = {}

for meja in range(dataJumlahMeja):
    meja += 1
    jumlahMeja[f"{meja}"] = f"Oke, kamu di meja nomor {meja} ya, tekan tombol di bawah ini untuk menampilkan menunya dan lanjut ke langkah selanjutnya"

print(jumlahMeja)