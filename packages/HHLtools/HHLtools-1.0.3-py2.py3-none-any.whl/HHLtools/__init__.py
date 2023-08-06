def output(content):
    print('success!your content:\n{}'.format(content))


def fibonacci(n):
    if n < 1 or int(n) != n:
        return "error, n should be a positive number which is greater than 1"
    if n < 3:
        return 1
    a, b = 1, 1

    for i in range(2, n):
        a = a + b if i % 2 == 0 else a
        b = a + b if i % 2 == 1 else b
    return a if a > b else b


def fibonacci_list(n):
    if n < 1 or int(n) != n:
        return "error, n should be a positive number which is greater than 1"
    if n == 1:
        return [1]
    if n == 2:
        return [1, 1]
    list = [1, 1]
    for i in range(2, n):
        list.append(list[i-2]+list[i-1])
    return list



