

def add_one(number):
    return number+1

def multiply(number1, number2):
    return number1 * number2

def getFile():
    with open("./Data100M.txt") as f:
        s = f.readlines()
    print(s)
    return s


