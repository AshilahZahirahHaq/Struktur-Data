def bubbleSort(arr):
    arr = arr.copy()
    n = len(arr)

    total_comparisons = 0
    total_swaps = 0
    passes_used = 0

    for i in range(n - 1):
        swapped = False
        passes_used += 1

        for j in range(n - i - 1):
            total_comparisons += 1

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                total_swaps += 1
                swapped = True

        print(f"Pass {passes_used}: {arr}")

        if not swapped:  # early termination
            break

    return arr, total_comparisons, total_swaps, passes_used


# Uji program
data1 = [5, 1, 4, 2, 8]
data2 = [1, 2, 3, 4, 5]

print("Input:", data1)
result1 = bubbleSort(data1)
print("Output:", result1)  #Data belum terurut sehingga banyak swap terjadi

print("\nInput:", data2)
result2 = bubbleSort(data2)
print("Output:", result2) #Data sudah terurut karena tidak ada swap pada pass pertama