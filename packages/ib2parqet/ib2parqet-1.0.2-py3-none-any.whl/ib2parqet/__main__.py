import argparse

from ._version import __version__
from .ib2parqet import convert, load_ib_xml, store_parqet_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("input", type=str, help="path to Flex Query xml generated in IB")
    parser.add_argument("-o", "--output", default="trades.csv", type=str, help="output file path")
    args = parser.parse_args()
    data = load_ib_xml(args.input)
    data2 = convert(data)
    store_parqet_csv(args.output, data2)


main()
