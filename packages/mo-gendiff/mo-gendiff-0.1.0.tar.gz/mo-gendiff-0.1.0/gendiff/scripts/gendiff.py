#!/usr/bin/env python3
import argparse


def gendiff():
    DESCRIPTION = 'Compares two configuration files and shows a difference.'
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    args = parser.parse_args()


def main():
    gendiff()


if '__name__' == '__main__':
    main()