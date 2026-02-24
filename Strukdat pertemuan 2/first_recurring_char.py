#First Recurring Character: Dari sebuah string, temukan karakter pertama yang muncul lebih dari sekali. (Gunakan set)

def kata_berulang(s):
    seen = set()

    for char in s:
        if char in seen:
            return char
        seen.add(char)

    return None

teks = input("Masukkan beberapa huruf(hilangkan koma dan spasi): ")
print("Karakter berulang pertama:", kata_berulang(teks))
