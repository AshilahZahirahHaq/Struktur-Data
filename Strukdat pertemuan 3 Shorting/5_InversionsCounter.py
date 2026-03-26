#Fungsi Naive
def countInversionsNaive(arr):
    count = 0
    n = len(arr)

    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] > arr[j]:
                count += 1

    return count

#Fungsi Smart
def mergeAndCount(arr, left, mid, right):
    left_part = arr[left:mid+1]
    right_part = arr[mid+1:right+1]

    i = j = 0
    k = left
    inv_count = 0

    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            inv_count += len(left_part) - i
            j += 1
        k += 1

    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1

    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1

    return inv_count


def mergeSortAndCount(arr, left, right):
    inv_count = 0

    if left < right:
        mid = (left + right) // 2

        inv_count += mergeSortAndCount(arr, left, mid)
        inv_count += mergeSortAndCount(arr, mid + 1, right)
        inv_count += mergeAndCount(arr, left, mid, right)

    return inv_count


def countInversionsSmart(arr):
    arr_copy = arr.copy()
    return mergeSortAndCount(arr_copy, 0, len(arr_copy) - 1)

#Uji Program
import random
import time
sizes = [1000, 5000, 10000]
for size in sizes:
    arr = [random.randint(1, 10000) for _ in range(size)]

    start = time.time()
    naive = countInversionsNaive(arr)
    naive_time = time.time() - start

    start = time.time()
    smart = countInversionsSmart(arr)
    smart_time = time.time() - start

    print(f"\nUkuran array: {size}")
    print(f"Inversions Naive: {naive} | waktu: {naive_time:.4f} detik")
    print(f"Inversions Smart: {smart} | waktu: {smart_time:.4f} detik")

#Merge short lebih cepat
#karena tidak membandingkan semua pasangan
#menghitung banyak inversions sekaligus saat proses merge