#!/usr/bin/env python3

from fizzbuzz import FizzBuzz
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def main():
    parser = ArgumentParser(description='A Fizz Buzz Generator', formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', metavar='start', help='start with this number', type=int, default=1)
    parser.add_argument('-e', metavar='end', help='end with this number', type=int ,default=100)
    parser.add_argument('-f', metavar='fizz', help='"Fizz" string', type=str, default='Fizz')
    parser.add_argument('-b', metavar='buzz', help='"Buzz" string', type=str, default='Buzz')
    parser.add_argument('-z', metavar='fizzbuzz', help='"Fizz Buzz" string', type=str, default='Fizz Buzz')
    parser.add_argument('-d', metavar='delimiter', help='word delimiter', type=str, default=', ')
    args = parser.parse_args()

    FizzBuzz.fizz = args.f
    FizzBuzz.buzz = args.b
    FizzBuzz.fizzbuzz = args.z
    FizzBuzz.delimiter = args.d.encode().decode('unicode-escape')
    print(FizzBuzz(args.s, args.e))


if __name__ == '__main__':
    main()

