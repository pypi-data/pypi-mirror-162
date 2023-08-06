#!/usr/bin/env python3

from fizzbuzz import FizzBuzz
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def main():
    parser = ArgumentParser(description='a powerful fizz buzz engine.', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', metavar='start', help='start with this number.', type=int, default=1)
    parser.add_argument('-e', metavar='end', help='end with this number.', type=int ,default=100)
    parser.add_argument('-f', metavar='fizz', help='replace "Fizz" string.', type=str, default='Fizz')
    parser.add_argument('-b', metavar='buzz', help='replace "Buzz" string.', type=str, default='Buzz')
    parser.add_argument('-z', metavar='fizzbuzz', help='replace "Fizz Buzz" string.', type=str, default='Fizz Buzz')
    parser.add_argument('-d', metavar='delimiter', help='replace the word delimiter.', type=str, default=', ')
    args = parser.parse_args()

    FizzBuzz.fizz = args.f
    FizzBuzz.buzz = args.b
    FizzBuzz.fizzbuzz = args.z
    FizzBuzz.delimiter = args.d.encode().decode('unicode-escape')

    fb = FizzBuzz(args.s, args.e)
    print(fb.gen.__next__(), end='')
    for s in fb.gen:
        print(fb.delimiter + s, end='')
    print()

    return 0


if __name__ == '__main__':
    exit(main())

