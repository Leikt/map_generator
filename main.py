#! /usr/bin/env python3
# coding: utf-8

import argparse

import src.generation


def parse_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-p", "--parameters",
                           help="Custom parameters filename in the root directory",
                           default="generation_parameters.json")

    return argparser.parse_args()


def main():
    # Parse arguments
    args = parse_args()
    parameters_fname = args.parameters
    # Run the generation with parameters
    src.generation.run(parameters_fname)


if __name__ == "__main__":
    main()
