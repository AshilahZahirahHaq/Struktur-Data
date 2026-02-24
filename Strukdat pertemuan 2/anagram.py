#Anagram Check: Tentukan apakah dua string adalah anagram (gunakan hitungan karakter dengan dict).

def is_anagram(str1, str2):
    if len(str1) != len(str2):
        return False

    count = {}

    for char in str1:
        count[char] = count.get(char, 0) + 1

    for char in str2:
        if char not in count:
            return False
        count[char] -= 1
        if count[char] < 0:
            return False

    return True

kata1 = input("Masukkan kata pertama: ")
kata2 = input("Masukkan kata kedua: ")

print("Apakah anagram?", is_anagram(kata1, kata2))
