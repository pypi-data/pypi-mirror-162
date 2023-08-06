import json
import os
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import Any, Dict
from urllib.error import URLError
from urllib.request import urlretrieve

from sprakbanken_scraping import make_dataset_object


def fetch_meta(obj: Dict[str, Any], folder_path: str, timestamp: str) -> None:
    # stores the metadata in a json file with checksum id
    filename = f"{obj['checksum']}_{timestamp}.json"
    path = os.path.join(folder_path, filename)
    with open(path, "w", encoding="latin-1") as meta_file:
        json.dump(obj["meta"], meta_file, indent=4)

def download_url(url: str, fpath: str) -> None:
    try:
        print('Downloading ' + url + ' to ' + fpath)
        urlretrieve(url, fpath)
    except (URLError, IOError) as err:
        print(err)
        if url[:5] == 'https':
            url = url.replace('https:', 'http:')
            print('Failed download. Trying https -> http instead.'
                    ' Downloading ' + url + ' to ' + fpath)
            urlretrieve(url, fpath)

def main(args: Namespace) -> None:
    """ handles all steps from user input
    to the downloading and structuring of data

    example run:
    python scribedl.py --dataset nst
    should store the fetched data in its respective folder
    (bigger data is split into random sized batches)
    |- data
     |- NST
       |- 1
       |- 2
       |- ...
       |- N
    
    Args:
        args (Namespace): the arguments passed from the terminal
    """
    dataset = args.dataset
    if not dataset:
        dataset = input("Enter dataset [nst, storting, nbtale]: ")
    print(f"Fetching data for dataset: '{dataset}'")
    obj = make_dataset_object(dataset.lower())
    print("-" * 40)
    print(f"Last updated at {obj['updated']}")
    if args.verbose:
        print("Metadata:")
        for k, v in obj["meta"].items():
            print(f"{k}: {v}")
        print("-" * 40)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    folder_path = os.path.join(os.getcwd(), "data", dataset)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    print(f"Accessed URL '{obj['url']}' at {timestamp}")

    if args.only_meta:
        fetch_meta(obj=obj, folder_path=folder_path, timestamp=timestamp)
        print("Exiting...")
        sys.exit(0)
    
    checksums = [f.split("_")[0] for f in os.listdir(folder_path) if f.endswith(".json")]
    
    if str(obj["checksum"]) in checksums:
        print(f"Dataset '{dataset}' already downloaded")
        inp = input("Continue to download regardless? [yes (Y) / no (N)] ")
        if inp.lower() in ["y", "yes"]:
            pass
        else:
            print("Exiting...")
            sys.exit(0)

    print("Found the following files:")
    for i, tarfile in enumerate(obj["downloads"]):
        tar_name = tarfile.split("/")[-1]
        print(f"{i+1}. {tar_name}")

    inp = input("Download? [yes (Y) / no (N)] ")
    if inp.lower() in ["y", "yes"]:
        for i, tarfile in enumerate(obj["downloads"]):
            tar_name = tarfile.split("/")[-1]
            tar_path = os.path.join(folder_path, tar_name)
            print(f"{i+1}. {tar_name}")
            download_url(url=tarfile, fpath=tar_path)

        print("Downloads complete. Storing metadata...")
        fetch_meta(obj=obj, folder_path=folder_path, timestamp=timestamp)


if __name__ == "__main__":
    parser = ArgumentParser()
    # * [NST](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-54/)
    # * [NPSC](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-58/)
    # * [NB tale](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-31/)
    available_datasets = [ "NST", "NPSC", "NBtale" ]
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        help=f"A dataset in the list {available_datasets}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints additional debug information",
    )
    parser.add_argument(
        "--only-meta",
        action="store_true",
        help="Skips the download process, only fetches metadata",
    )

    main(args=parser.parse_args())
