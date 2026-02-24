# Intersection Dua Array: Berikan dua list, kembalikan list yang berisi elemen yang muncul di keduanya

def intersection(list1, list2):
    set1 = set(list1)
    set2 = set(list2)

    return list(set1.intersection(set2))

a = [1, 2, 3, 4]
b = [3, 4, 5, 6]

print("Intersection:", intersection(a, b))