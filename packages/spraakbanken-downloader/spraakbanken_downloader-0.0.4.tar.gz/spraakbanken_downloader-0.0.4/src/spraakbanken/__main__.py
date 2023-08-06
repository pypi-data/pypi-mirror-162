import json
import os
import shutil
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import Any, Dict
from urllib.error import URLError
from urllib.request import urlretrieve

from spraakbanken.sprakbanken_scraping import make_dataset_object


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
    """ handles all steps from user input to the downloading and structuring of data
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
        for meta_key, meta_val in obj["meta"].items():
            print(f"{meta_key}: {meta_val}")
        print("-" * 40)

    if args.outdir:
        folder_path = args.outdir
    else:
        folder_path = os.path.join(os.getcwd(), "data")

    folder_path = os.path.join(folder_path, dataset)

    if not os.path.exists(folder_path):
        print(f"Creating folder '{folder_path}'")
        os.makedirs(folder_path)

    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    print(f"Accessed URL '{obj['url']}' at {timestamp}")

    if args.meta:
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
    for i, _file in enumerate(obj["downloads"]):
        print(f"{i+1}. {_file.split('/')[-1]}")

    inp = input("Download? [yes (Y) / no (N)] ")
    if inp.lower() in ["y", "yes"]:
        for i, _file in enumerate(obj["downloads"]):
            _name = _file.split("/")[-1]
            _path = os.path.join(folder_path, _name)
            print(f"{i+1}. {_name}")
            download_url(url=_file, fpath=_path)
            # create a separate folder for each archive:
            archive_path = os.path.join(folder_path, _name.split(".")[0])
            os.makedirs(archive_path)
            shutil.unpack_archive(_path, archive_path)
            os.remove(_path)
            print(f"Downloaded {_name}")

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
        "-o",
        "--outdir",
        type=str,
        help="The output directory for the downloaded files",
    )
    parser.add_argument(
        "-u",
        "--unpack",
        action="store_true",
        help="Unpacks downloaded .zip/.tar.gz and deletes the archives",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints additional debug information",
    )
    parser.add_argument(
        "-m",
        "--meta",
        action="store_true",
        help="Skips the download process, only fetches metadata",
    )

    main(args=parser.parse_args())
