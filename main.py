import argparse
import sys
import json


def get_data_from_file(filename: str) -> dict:
    """
    Open local file containing log data and parse json as Python object.

    :param str filename: path to local json file

    :returns data: Python object obtained from parsing json file
    """
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def get_data_from_server(endpoint: str, days: int) -> dict:
    pass


def _convert_byte_to_gb(size: str | int) -> float:
    """
    Helper function that converts a byte to GB.

    :param str/int size: size in bytes

    :returns size_gb: size in GB, as a float
    """
    return int(size) / (10 ** 9)


def print_largest_indexes(data: dict) -> None:
    """
    Print the top 5 indexes by size.

    :param dict data: Python object containing log data

    Format:
    ```
    Printing largest indexes by storage size
    Index: express
    Size: 901.26 GB
    Index: secluded
    Size: 689.54 GB
    ...
    ```
    """
    # Sort descending by byte size
    top5_size = sorted(data, key=lambda x: int(x["pri.store.size"]), reverse=True)[:5]

    # Print each index and size in GB (2 dp)
    print("\nPrinting largest indexes by storage size")
    for x in top5_size:
        index = x["index"]
        size_gb = _convert_byte_to_gb(x["pri.store.size"])
        print(f"Index: {index}")
        print(f"Size: {size_gb:.2f} GB")


def print_most_shards(data: dict) -> None:
    pass


def print_least_balanced(data: dict) -> None:
    pass


def main():
    parser = argparse.ArgumentParser(description="Process index data.")
    parser.add_argument("--endpoint", type=str, default="",
                        help="Logging endpoint")
    parser.add_argument("--debug", action="store_true",
                        help="Debug flag used to run locally")
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days of data to parse")
    args = parser.parse_args()

    data = None

    if args.debug:
        try:
            # data = get_data_from_file("indexes.json")
            data = get_data_from_file("example-in.json")
        except Exception as err:
            sys.exit("Error reading data from file. Error: " + str(err))
    else:
        try:
            data = get_data_from_server(args.endpoint, args.days)
        except Exception as err:
            sys.exit("Error reading data from API endpoint. Error: " + str(err))

    print_largest_indexes(data)
    print_most_shards(data)
    print_least_balanced(data)


if __name__ == '__main__':
    main()
