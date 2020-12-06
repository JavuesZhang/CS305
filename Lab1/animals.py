class Animal:
    def __init__(self, name):
        self.name = name


class Duck(Animal):
    def __init__(self, name):
        super(Duck, self).__init__(name)

    @staticmethod
    def quark():
        print('Quark')


class Dog(Animal):
    def __init__(self, name):
        super(Dog, self).__init__(name)

    @staticmethod
    def quark():
        print('Woof')
