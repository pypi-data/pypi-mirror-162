#!/usr/bin/env python

"""Take output from count matrices and average."""

import argparse

from origamipy import conditions
from origamipy import files
from origamipy import outputs
from origamipy import biases


def main():
    args = parse_args()
    system_file = files.JSONStructInpFile(args.system_filename)
    conditions_map = construct_conditions_map(args)
    fileformatter = construct_fileformatter()
    all_conditions = conditions.AllSimConditions(
        conditions_map, fileformatter, system_file
    )
    inp_filebase = create_input_filepathbase(args)
    enums = outputs.EnumCollection(inp_filebase, all_conditions)
    out_filebase = create_output_filepathbase(args)
    enums.calc_all_1d_means(out_filebase)
    enums.calc_all_1d_lfes(out_filebase)


def construct_conditions_map(args):
    conditions_map = {"temp": args.temps, "staple_m": [0], "bias": [biases.NoBias()]}

    return conditions_map


def construct_fileformatter():
    specs = [conditions.ConditionsFileformatSpec("temp", "{:d}")]
    return conditions.ConditionsFileformatter(specs)


def create_input_filepathbase(args):
    return "{}/{}".format(args.input_dir, args.filebase)


def create_output_filepathbase(args):
    return "{}/{}".format(args.output_dir, args.filebase)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("system_filename", type=str, help="System file")
    parser.add_argument("filebase", type=str, help="Filebase")
    parser.add_argument("input_dir", type=str, help="Directory of inputs")
    parser.add_argument("output_dir", type=str, help="Directory to output to")
    parser.add_argument("--temps", nargs="+", type=int, help="Temperatures")

    return parser.parse_args()


if __name__ == "__main__":
    main()
