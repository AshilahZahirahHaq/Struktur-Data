def mergeThreeSortedLists(listA, listB, listC):
    i = j = k = 0
    result = []

    while i < len(listA) or j < len(listB) or k < len(listC):

        a = listA[i] if i < len(listA) else float('inf')
        b = listB[j] if j < len(listB) else float('inf')
        c = listC[k] if k < len(listC) else float('inf')

        minimum = min(a, b, c)

        result.append(minimum)

        if minimum == a:
            i += 1
        elif minimum == b:
            j += 1
        else:
            k += 1

    return result

print(mergeThreeSortedLists(
    [1, 5, 9],
    [2, 6, 10],
    [3, 4, 7]
))

#menggabungkan tiga list terurut dengan:
#3 pointer