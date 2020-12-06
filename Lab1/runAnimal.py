import animals


def testDuck(duck):
    duck.quark()


duck = animals.Duck('Tommy')
testDuck(duck)
dog = animals.Dog('Fox')
testDuck(dog)
