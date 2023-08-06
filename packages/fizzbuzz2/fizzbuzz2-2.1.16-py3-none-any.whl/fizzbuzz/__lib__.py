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
            elif i % 5 == 0:
                return cls.buzz
            elif i % 3 == 0:
                return cls.fizz
            else:
                return str(i)

    @classmethod
    def generate(cls, start=1, end=100):
        for i in range(start, end+1):
            yield cls.judge(i)

    def __init__(self, start=1, end=100):
        self.gen = self.generate(start, end)

    def __str__(self):
        return self.delimiter.join(self.gen)

if __name__ == '__main__':
    print(FizzBuzz())

