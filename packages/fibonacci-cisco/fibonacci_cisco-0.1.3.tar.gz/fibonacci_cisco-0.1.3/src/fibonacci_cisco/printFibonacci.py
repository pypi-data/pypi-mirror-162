def getFibonacciNumber(n):
    if n < 0:
        raise Exception("n must be non negative number")
    saveNumbers = {0: 0, 1: 1}
    for i in range(2, n + 1):
        saveNumbers[i] = saveNumbers[i - 1] + saveNumbers[i - 2]
    return saveNumbers[n]

def getFibonacciCisco(n):
    numberOfPrints = getFibonacciNumber(n)
    for i in range(1,numberOfPrints+1):
        print(f"Cisco {i}")
    return

