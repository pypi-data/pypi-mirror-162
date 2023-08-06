from .number import NumberGenerator


class Adder:
    def __init__(self):
        NumberGenerator.__init__(self)

    def add(self):
        return self.a + self.b

    def go(self):
        print(f'Your summ is: {self.add()}')