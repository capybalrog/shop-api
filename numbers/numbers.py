def with_for_cycle(n):
    result = ''

    for i in range(1, n):
        block = str(i) * i
        result += block
        if len(result) >= n:
            break

    return result[:n]


def with_while_cycle(n):
    result = ''
    i = 1

    while len(result) < n:
        block = str(i) * i
        result += block
        i += 1

    return result[:n]

if __name__ == '__main__':
    n = int(input('Введите число: '))

    print(with_for_cycle(n))
    print(with_while_cycle(n))
