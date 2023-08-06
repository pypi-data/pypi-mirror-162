import argparse
import sys

from dagster_fmt import run


def cli(args=None):
    parser = argparse.ArgumentParser(description="dagster_fmt code gen")

    parser.add_argument(
        "path", type=str, help="Path to the file or directory to format", metavar="p"
    )

    args = parser.parse_args(args)
    run("../" + args.path)


if __name__ == "__main__":
    cli(sys.argv[1:])
