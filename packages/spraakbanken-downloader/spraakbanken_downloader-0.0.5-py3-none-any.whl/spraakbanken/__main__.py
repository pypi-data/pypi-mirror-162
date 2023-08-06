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

AVAILABLE_DATASETS = [ "NST", "Storting", "NBtale" ]

class ProgressBar:
    def __init__(self):
        self.old_percent = 0
        self.already_printed = False

    def init_print(self, total_sz):
        if not self.already_printed:
            print(f"Total file size: {round(total_sz * 1e-6, 2)} MB")
            print('_' * 50)
            self.already_printed = True

    def download_progress_hook(self, count, block_sz, total_sz):
        self.init_print(total_sz)
        percent = int(count * block_sz * 100 / total_sz)
        if percent >= 2 + self.old_percent:
            self.old_percent = percent
            print('>', end='')
            sys.stdout.flush()

def fetch_meta(obj: Dict[str, Any], folder_path: str, timestamp: str) -> None:
    # stores the metadata in a json file with checksum id
    filename = f"{obj['checksum']}_{timestamp}.json"
    path = os.path.join(folder_path, filename)
    with open(path, "w", encoding="latin-1") as meta_file:
        json.dump(obj["meta"], meta_file, indent=4)

def download_url(url: str, fpath: str) -> None:
    try:
        print('Downloading ' + url + ' to ' + fpath)
        urlretrieve(url, fpath, reporthook=ProgressBar().download_progress_hook)
    except (URLError, IOError) as err:
        print(err)
        if url[:5] == 'https':
            url = url.replace('https:', 'http:')
            print('Failed download. Trying https -> http instead.'
                    ' Downloading ' + url + ' to ' + fpath)
            urlretrieve(url, fpath, reporthook=ProgressBar().download_progress_hook)
            
def handle_dataset(dataset: str, args: Namespace) -> None:
    print(f"Fetching data for dataset: '{dataset}'")
    dataset = dataset.lower()
    obj = make_dataset_object(dataset)
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

    os.makedirs(folder_path, exist_ok=True)

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

    inp = input("Download all? [yes (Y) / no (N)] ")
    if inp.lower() not in ["y", "yes"]:
        return

    for i, _file in enumerate(obj["downloads"]):
        _name = _file.split("/")[-1]
        _path = os.path.join(folder_path, _name)
        print(f"{i+1}. {_name}")
        
        # 1 -- Download
        # download_url(url=_file, fpath=_path)

        # 2 -- Unpack and delete old archives
        archive_path = os.path.join(folder_path, _name.split(".")[0])
        # os.makedirs(archive_path, exist_ok=True)
        # shutil.unpack_archive(_path, archive_path)
        # os.remove(_path)

        # 3 -- Move files to folder based on custom rules
        if dataset.lower() == "storting":
            for _file in os.listdir(archive_path):
                if _file.endswith(".wav"):
                    _id = _file.split("-")[0]
                    os.makedirs(os.path.join(folder_path, _id), exist_ok=True)
                    
                    shutil.move(
                        src=os.path.join(archive_path, _file),
                        dst=os.path.join(folder_path, _id)
                    )
        
        if dataset.lower() == "nst":
            # define a language for later support (e.g. dk)
            language = "no"
            # create the grouped folder (1_a, 1_b, 1_c => 1)
            id_path = archive_path.rsplit("_", maxsplit=1)[0]
            if "lydfiler" not in id_path:
                continue

            src = os.path.join(archive_path, language)
            dst = os.path.join(id_path, language)

            for sub_file in os.listdir(src):
                shutil.move(os.path.join(src, sub_file), os.path.join(dst, sub_file))
            os.remove(src)

        print(f"Downloaded {_name}")

    print("Downloads complete. Storing metadata...")
    fetch_meta(obj=obj, folder_path=folder_path, timestamp=timestamp)

def main(args: Namespace) -> None:
    """ handles all steps from user input to the downloading and structuring of data
    Args:
        args (Namespace): the arguments passed from the terminal
    """
    dataset = args.dataset
    valid = [d.lower() for d in AVAILABLE_DATASETS]
    print(dataset)

    if not dataset:
        dataset = input(f"Enter dataset {AVAILABLE_DATASETS} or 'all': ")
        if dataset.lower() == "all":
            print("Downloading all datasets...")
            for _dataset in AVAILABLE_DATASETS:
                handle_dataset(_dataset, args)
        elif dataset.lower() in valid:
            handle_dataset(dataset, args)
    elif dataset.lower() in valid:
        handle_dataset(dataset, args)

if __name__ == "__main__":
    parser = ArgumentParser()
    # * [NST](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-54/)
    # * [NPSC](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-58/)
    # * [NB tale](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-31/)
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        help=f"A dataset in the list {AVAILABLE_DATASETS}",
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
