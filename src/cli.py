"""The command line interface entry-point for the project."""

from argparse import ArgumentParser


# default value for optional arguments
_DEFAULT_ARG = object()


# create the main argument parser
parser = ArgumentParser(
    argument_default=_DEFAULT_ARG,
)

parser.add_argument(
    "-m",
    "--models",
    type=str,
    required=True,
    help="List of models to use.",
)

parser.add_argument(
    "-df",
    "--dataset-file",
    type=str,
    required=True,
    help="Path to the dataset file.",
)

parser.add_argument(
    "-o",
    "--output-dir",
    type=str,
    help="Path to directory to save the results.",
)


def main():
    args = parser.parse_args()
    kwargs = vars(args)

    # remove arguments where the method default value should be used
    kwargs = {k: v for k, v in kwargs.items() if v is not _DEFAULT_ARG}

    # run the code with the kwargs
    print(kwargs)


if __name__ == "__main__":
    main()
