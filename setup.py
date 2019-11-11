
index = 3
arr = [1, 4, 23, 6, 2, 6, 3, 7]

tickets = arr[3]  # 6
time = 1
total = 0


for i in range(0, 6):
    total += time * (index + 1)
    j = 0
    while j <= index:
        if arr[j] == 1:
            arr.pop(j)
        else:
            arr[j] = arr[j] - 1
        j += 1
    index = len(arr) - 1

print(total)
