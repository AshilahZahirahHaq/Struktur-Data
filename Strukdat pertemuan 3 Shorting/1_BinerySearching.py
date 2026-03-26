#Implementasi fungsi count0ccurences(sortedlist, target)
#Menggunakan dua kali binary serach- untuk menenetukan batas kiri kemunculan pertama
#untuk menentukan batas kanan kemunculan terakhir

def findFirst(arr, target):
    left, right = 0, len(arr) - 1
    first = -1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            first = mid
            right = mid - 1  # cari lebih ke kiri
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return first


def findLast(arr, target):
    left, right = 0, len(arr) - 1
    last = -1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            last = mid
            left = mid + 1  # cari lebih ke kanan
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return last


def countOccurrences(sortedList, target):
    first = findFirst(sortedList, target)

    if first == -1:
        return 0

    last = findLast(sortedList, target)

    return last - first + 1


# Contoh penggunaan
print(countOccurrences([1, 2, 2, 3, 3, 4, 7, 9, 12], 3))
print(countOccurrences([1, 2, 2, 3, 3, 4, 7, 9, 12], 1))