#!/usr/bin/env python3
import argparse
from gendiff.run_gendiff import generate_diff


def main():
    DESCRIPTION = 'Compares two configuration files and shows a difference.'
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    parser.add_argument('-f', '--format', help='set format of output')
    args = parser.parse_args()
    print(generate_diff(args.first_file, args.second_file))


if '__name__' == '__main__':
    main()
