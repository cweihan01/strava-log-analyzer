# Strava Log Analyzer

*Strava Software Engineering Intern (Foundation) 2025 - Take-Home Assignment Submission*

A command-line tool that parses JSON data from a local file or a HTTP API and prints:
1. Top 5 indexes by storage size  
2. Top 5 indexes by shard count  
3. Top 5 least balanced indexes (GB/shard ratio) with new recommended shard counts  

## Table of Contents
- [Strava Log Analyzer](#strava-log-analyzer)
  - [Table of Contents](#table-of-contents)
  - [Assumptions](#assumptions)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Clone the repo](#clone-the-repo)
    - [Setting up a virtual environment](#setting-up-a-virtual-environment)
    - [Install dependencies](#install-dependencies)
    - [Usage](#usage)
      - [Debug mode](#debug-mode)
      - [Live API mode](#live-api-mode)
  - [Testing](#testing)
    - [Debug mode](#debug-mode-1)
    - [Live API mode](#live-api-mode-1)
      - [Setup](#setup)
      - [Usage](#usage-1)

## Assumptions

While I tried my best to replicate the behavior provided in the specifications and the example input and output, there were some assumptions that I had to make while working on the project due to insufficient information.

The key assumptions I made are as follows:

1. I assumed storage size is always to be displayed in GB (instead of KB, TB, etc.).

2. I assumed that `index` is a unique identifier throughout the local file or across multiple days. As such, when aggregating data over multiple days, I did not account for behavior when `index` is repeated across days.

3. Input JSON is a valid list of objects, each with the keys:
```json
{
  "index": "<name>",
  "pri.store.size": "<bytes (string)>",
  "pri": "<shard‑count (string)>"
}
```
If any input object had missing or invalid fields, the program throws an error (instead of ignoring this entry, for example).

4. In API mode, I fetched one day per request starting from the day before today and work backwards, aggregating data from the last `--days` days (only yesterday for `days = 1`, yesterday and 2 days before for `days = 2`, etc.). I also assumed that the input argument to `--days` must be at least 1, or an error is raised.

5. I assumed that today's date is determined by the local timezone from which the user is running the program (instead of GMT or UTC for example).

6. When displaying the balance ratio, I chose to round down the ratio to the closest whole number, ie. printing the `floor` of the ratio. I found that the provided example input and output had inconsistent behavior.

Consider these input fields from `example-in.json`:
```json
{
    "index": "oblivion",
    "pri.store.size": "537619000000",
    "pri": "7"
},
{
    "index": "express",
    "pri.store.size": "901261200000",
    "pri": "2"
}
```

Calculating the balance ratio by hand should give the following ratios (rounded to 4 decimal points):
```txt
Index: oblivion
Balance Ratio: 76.8027

Index: express
Balance Ratio: 450.6306
```

However, `example-out.txt` presents the following results:
```txt
Index: express
Size: 901.26 GB
Shards: 2
Balance Ratio: 450
Recommended shard count is 30
Index: oblivion
Size: 537.62 GB
Shards: 7
Balance Ratio: 77
Recommended shard count is 17
```

This table summarizes the various possibilities for these ratios.

| Index    | Computed (4 d.p.) | Round Up | Round Down | Round to closest integer | Ratio in `example-out.txt` |
| -------- | ----------------- | -------- | ---------- | ------------------------ | -------------------------- |
| express  | 450.6306          | 451      | 450        | 451                      | 450                        |
| oblivion | 76.8027           | 77       | 76         | 77                       | 77                         |

None of the possibilities of converting the decimal ratio to a whole number produce consistent behavior with `example-out.txt`. As such, I chose to round down the ratio, as I observed this matched the output produced by most other examples, and only disagrees with the output for "oblivion".

7. Similarly, when computing the new shard count recommendation, I chose to round up as mentioned in the specification:
> For example, an index with 2,000 GB and 20 shards has a “ratio” of 100. Ideally, this index should have at least 67 shards allocated.

If we compute the recommended new shard count by hand, we obtain the value $2000 / 30 = 66.6667 (4 d.p.)$. It makes intuitive sense to round up the value to $67$ as per the specification.

However, this behavior contradicts the expected output from the example files. Consider the following input from `example-in.json`:
```json
{
    "index": "secluded",
    "pri.store.size": "689537000000",
    "pri": "1"
}
```

Computing the recommended new shard count by hand should yield $689.537 / 30 = 22.9846 (4 d.p.)$. Rounding up yields $23$ recommended shards.

But `example-out.json` has the following result:
```txt
Index: secluded
Size: 689.54 GB
Shards: 1
Balance Ratio: 689
Recommended shard count is 22
```

The example output recommends $22$ shards for "secluded" instead. Despite this behavior, it made intuitive sense to me to round up this value as per the specification, so I chose to round up the recommended shard count.


## Installation

### Prerequisites
- Python 3.10+

### Clone the repo
```bash
git clone https://github.com/cweihan01/strava-log-analyzer
cd strava-log-analyzer
```

### Setting up a virtual environment
```
python3 -m venv .venv
```

*macOS/Linux*
```
source .venv/bin/activate
```

*Windows*
```
.venv\Scripts\Activate.ps1
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Usage

#### Debug mode

To specify a custom file:
```bash
python main.py --debug --file <FILENAME.txt>
```

If the `--file <FILENAME.txt>` argument is not used, the default file is `indexes.json` in the current directory.

#### Live API mode
```bash
python main.py --endpoint <www.domain.com> --days <DAYS>
```

If the `--days <DAYS>` argument is not used, the default value is 7. 

## Testing

### Debug mode

I used the provided `example-in.json` to run my script in debug mode, and redirected the output to a separate file:
```bash
python main.py --debug --file example-in.json > test-out.txt
```

I then used the `diff` command to compare my output with `example-out.txt`:
```bash
diff test-out.txt example-out.txt
```

As mentioned in the [assumptions](#assumptions) (points 6 & 7), there are some discrepancies due to the way I rounded the balance ratio and the recommended shard count. Besides these, the rest of the output is identical.

My `diff` output is as follows:
```txt
31c31
< Recommended shard count is 23
---
> Recommended shard count is 22
36c36
< Recommended shard count is 17
---
> Recommended shard count is 16
41c41
< Recommended shard count is 31
---
> Recommended shard count is 30
45,46c45,46
< Balance Ratio: 76
< Recommended shard count is 18
---
> Balance Ratio: 77
> Recommended shard count is 17
```

### Live API mode
To test the live API mode of my script, I wrote a simple API server using FastAPI, with the one required endpoint.

#### Setup

In a new terminal, run the following command:
```bash
cd mock-api
```

Setup the virtual environment using the same steps as [above](#setting-up-a-virtual-environment), but using a different virtual environment name and `requirements-api.txt` instead.

The server can be started with:
```bash
python main.py
```

The API is now exposed at `http://localhost:8000/_cat/indices/*<YEAR>*<MONTH>*<DAY>?v&h=index,pri.store.size,pri&format=json&bytes=b`.

#### Usage

Since the main log script expects a HTTPS connection, we have to either modify line 51 of `main.py` in the root directory, or setup a HTTPS proxy.

For testing, I modified line 51 directly to use HTTP instead of HTTPS.

Then, when the API server is running, the [commands to interact with the live API](#live-api-mode) should work.
