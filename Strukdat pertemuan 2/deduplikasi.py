#Deduplikasi: Tulis fungsi yang menerima list dan mengembalikan list baru tanpa duplikat dengan urutan kemunculan pertama. 

def deduplikasi(lst):
    seen = set()
    hasil = []

    for item in lst:
        if item not in seen:
            seen.add(item)
            hasil.append(item)

    return hasil

data = [1, 2, 2, 3, 4, 3, 5, 1]
print("List awal:", data)
print("Tanpa duplikat:", deduplikasi(data))

