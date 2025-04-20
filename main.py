import argparse
import sys
import json
import math


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


def _get_balance_ratio(entry: dict) -> float:
    """
    Helper function that calculates GB-to-shard ratio for a given log entry.

    :param dict entry: a single log entry

    :returns ratio: GB-to-shard ratio, as a float
    """
    size_gb = _convert_byte_to_gb(entry["pri.store.size"])
    shards = int(entry["pri"])
    return size_gb / shards if shards > 0 else float("inf")


def print_largest_indexes(data: dict) -> None:
    """
    Print the top 5 indexes by size.

    :param dict data: Python object containing log data

    Print format:
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
    """
    Print the top 5 indexes by shard count.

    :param dict data: Python object containing log data

    Print format:
    ```
    Printing largest indexes by shard count
    Index: spry
    Shards: 20
    Index: bulldog
    Shards: 13
    ...
    ```
    """
    # Sort descending by shard count
    top5_shards = sorted(data, key=lambda x: int(x["pri"]), reverse=True)[:5]

    # Print each index and shard count
    print("\nPrinting largest indexes by shard count")
    for x in top5_shards:
        index, shards = x["index"], int(x["pri"])
        print(f"Index: {index}")
        print(f"Shards: {shards}")


def print_least_balanced(data: dict) -> None:
    """
    Print the top 5 biggest offenders with the highest GB-to-shard ratio and offer
    a new shard count recommendation.

    An index should have 1 shard for every 30 GB of data it stores.

    For example, an index with 2,000 GB and 20 shards has a “ratio” of 100. Ideally,
    this index should have at least 67 shards allocated.

    :param dict data: Python object containing log data

    Print format:
    ```
    Printing least balanced indexes
    Index: secluded
    Size: 689.54 GB
    Shards: 1
    Balance Ratio: 689
    Recommended shard count is 22
    Index: puzzle
    Size: 506.28 GB
    Shards: 1
    Balance Ratio: 506
    Recommended shard count is 16
    ...
    ```
    """
    # Sort descending by GB-to-shard (balance) ratio
    top5_offenders = sorted(data, key=lambda x: _get_balance_ratio(x), reverse=True)[:5]

    print("\nPrinting least balanced indexes")
    for x in top5_offenders:
        index = x["index"]
        size_gb = _convert_byte_to_gb(x["pri.store.size"])
        shards = x["pri"]
        ratio = _get_balance_ratio(x)
        # ASSUME round up recommended shards, and minimum 1 shard allocated unless size=0
        recommended = max(1, math.ceil(size_gb / 30)) if size_gb > 0 else 0

        print(f"Index: {index}")
        print(f"Size: {size_gb:.2f} GB")
        print(f"Shards: {shards}")
        print(f"Balance Ratio: {math.floor(ratio)}")  # ASSUME round down balance ratio
        print(f"Recommended shard count is {recommended}")


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
