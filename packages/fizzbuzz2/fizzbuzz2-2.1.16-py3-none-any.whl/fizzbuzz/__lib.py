#!/usr/bin/env python3


class FizzBuzz:
    fizz = 'Fizz'
    buzz = 'Buzz'
    fizzbuzz = 'Fizz Buzz'
    delimiter = ', '

    @classmethod
    def judge(cls, i):
            if i % 15 == 0:
                return cls.fizzbuzz
            elif i % 3 == 0:
                return cls.fizz
            elif i % 5 == 0:
                return cls.buzz
            else:
                return str(i)

    @classmethod
    def generate(cls, start=1, end=100):
        for i in range(start, end+1):
            yield cls.judge(i)

    def play(self, start=1, end=100):
        self.ret = self.generate(start, end)

    def __init__(self, start=1, end=100):
        self.play(start, end)

    def __str__(self):
        return self.delimiter.join(self.ret)

if __name__ == '__main__':
    print(FizzBuzz())

