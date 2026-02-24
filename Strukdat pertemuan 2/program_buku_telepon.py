def buku_telepon():
    kontak = {}

    while True:
        print("\n=== MENU BUKU TELEPON ===")
        print("1. Tambah Kontak")
        print("2. Cari Kontak")
        print("3. Tampilkan Semua Kontak")
        print("4. Keluar")

        pilihan = input("Pilih menu (1-4): ")

        if pilihan == "1":
            nama = input("Masukkan nama: ")
            nomor = input("Masukkan nomor: ")
            kontak[nama] = nomor
            print("Kontak berhasil ditambahkan!")

        elif pilihan == "2":
            nama = input("Masukkan nama yang dicari: ")
            if nama in kontak:
                print("Nomor:", kontak[nama])
            else:
                print("Kontak tidak ditemukan.")

        elif pilihan == "3":
            if not kontak:
                print("Belum ada kontak.")
            else:
                print("\nDaftar Kontak:")
                for nama, nomor in kontak.items():
                    print(f"{nama} -> {nomor}")

        elif pilihan == "4":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid.")



buku_telepon()
