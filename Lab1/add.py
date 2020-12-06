def add(x):
    def addX(y):
        return y + x

    return addX


foo = add(1)
print(foo(2))
