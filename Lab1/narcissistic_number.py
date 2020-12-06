def find_narcissistic_number(start, end):
    list = []
    if start < 0:
        start = 0
    if end > start:
        length = end - start
        for i in range(length):
            sum = 0
            this_num = start + i
            temp = this_num
            n = 0
            while temp > 0:
                temp //= 10
                n += 1
            temp = this_num
            while temp > 0:
                digit = temp % 10
                temp //= 10
                sum += digit**n
            if sum == this_num:
                list.append(this_num)
    else:
        print(
            "Narcissistic numbers are nonnegative numbers. Please input valid start number and end number. "
        )
    return list
