def insertionSort(arr):
    arr = arr.copy()
    comparisons = 0
    swaps = 0

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j+1] = arr[j]
                swaps += 1
                j -= 1
            else:
                break
        arr[j+1] = key

    return arr, comparisons, swaps


def selectionSort(arr):
    arr = arr.copy()
    comparisons = 0
    swaps = 0

    n = len(arr)

    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j

        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1

    return arr, comparisons, swaps


def hybridSort(theSeq, threshold=10):
    if len(theSeq) < threshold:
        return insertionSort(theSeq)
    else:
        return selectionSort(theSeq)
    
import random

sizes = [50, 100, 500]

print("Size | Hybrid Ops | Insertion Ops | Selection Ops")

for size in sizes:
    arr = [random.randint(1,1000) for _ in range(size)]

    _, c1, s1 = hybridSort(arr)
    _, c2, s2 = insertionSort(arr)
    _, c3, s3 = selectionSort(arr)

    hybrid_ops = c1 + s1
    insertion_ops = c2 + s2
    selection_ops = c3 + s3

    print(size, "|", hybrid_ops, "|", insertion_ops, "|", selection_ops)

#menggabungkan dua algortima
#Insertion Sort untuk data kecil (lebih cepat)
#Selection Sort untuk data besar
#tujuannya meningkatkan efisiensi shorting