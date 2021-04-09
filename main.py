#! /usr/bin/env python3
# coding: utf-8

import argparse
import os

import src.generation
import src.raw


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
    dirname = os.path.dirname(__file__)
    path_to_params = os.path.join(dirname, parameters_fname)

    # Run the generation with parameters
    src.generation.run(path_to_params)


if __name__ == "__main__":
    main()
