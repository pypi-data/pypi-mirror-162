def merge(arr, l, m, r):
    n1 = m - l + 1
    n2 = r - m

    L = [0] * n1
    R = [0] * n2

    for i in range(0, n1):
        L[i] = arr[l + i]

    for j in range(0, n2):
        R[j] = arr[m + 1 + j]

    i = 0
    j = 0
    k = l

    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1

    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1

    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1

    output.append(arr.copy())


def mergeSort(arr, l, r):
    if l < r:

        m = int((l + (r - 1)) / 2)
        print("before sort", l, m, r)
        mergeSort(arr, l, m)
        mergeSort(arr, m + 1, r)

        print("before merge", l, m, r)
        merge(arr, l, m, r)
        # output.append(arr.copy())


N = 10
raw = [3, 1, 2, 8, 7, 5, 9, 4, 0, 6]
intermediate = [1, 3, 2, 8, 5, 7, 4, 9, 0, 6]
output = []

mergeSort(raw, 0, N - 1)
print(output)
pos = output.index(intermediate)
if pos != -1:
    print("merge sort")
    print(output[pos + 1])
