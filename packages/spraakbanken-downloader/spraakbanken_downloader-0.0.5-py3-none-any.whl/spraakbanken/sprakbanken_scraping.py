import re
import zlib
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup as BS  # type: ignore
from bs4 import ResultSet, Tag

SPRAKBANKEN_KEYS = {
    "updated": "Oppdatert",
    "docs": "Dokumentasjon"
}

SPRAKBANKEN = "https://www.nb.no/SPRAKBANKEN/ressurskatalog/"

dataset_ids = {
    "nst":"oai-nb-no-sbr-54",
    "storting": "oai-nb-no-sbr-58",
    "nbtale": "oai-nb-no-sbr-31",
}

def make_url(dataset: str) -> str:
    return f"{SPRAKBANKEN}/{dataset_ids[dataset]}/"

def get_content(url: str) -> BS:
    page = requests.get(url)
    if page.status_code == 200:
        return BS(page.text, features="html.parser")

def make_metadata(from_soup: BS) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}

    meta_box: ResultSet = from_soup.find_all("aside")[0]
    for m in meta_box:
        meta_type = m.text.split(":")[0]

        if meta_type == SPRAKBANKEN_KEYS["updated"]:
            datestr = m.text.split(":")[-1]
            dateobj = datetime.strptime(datestr, "%d.%m.%Y").date()
            metadata["updated"] = dateobj

        if meta_type == SPRAKBANKEN_KEYS["docs"]:
            doc_links: List[Tag] = m.find_all("a", href=True)
            metadata["docs"] = [a["href"] for a in doc_links]
            
    return metadata

def make_additional_meta(from_soup: BS) -> Dict[str, Any]:
    corpus_info = from_soup.find(id="resource-corpus-info-content")
    root_ul = corpus_info.find_all("ul")[1]  # the second index: "corpus info"
    
    corpus_dict = {}

    info_li = [x for x in root_ul.find_all("li") if x.find("span").text == "corpus Part Info"][0]
    for _li in info_li.find_all("li"):
        subhead = _li.find("span")
        if not subhead:
            continue

        subhead_dict = {}
        for _ul in _li.find_all("ul"):

            if len(_ul.find_all("ul")) != 0:
                continue
            
            # text = _ul.find("span").text
            values = [__li.text.split(":") for __li in _ul.find_all("li")]
            for key, val in values:
                val = re.sub(r"\s+", " ", val.lower().strip())
                key = key.lower().strip()
                subhead_dict[key] = val
        
        if len(subhead_dict.values()) > 0:
            corpus_dict[subhead.text.lower()] = subhead_dict
    return corpus_dict

def is_valid_file(link: ResultSet) -> bool:
    link = link["href"]
    return ".tar.gz" in link or ".zip" in link

def make_download_links(from_soup: BS) -> List[str]:
    download_class = "teft-link-list-item__link"
    downloads: ResultSet = from_soup.find_all(class_=download_class)
    tarfiles = [a["href"] for a in downloads if is_valid_file(a)]
    return tarfiles

def make_checksum(metadata: Dict[str, Any]) -> int:
    """ create a checksum based on hashes of all items within the metadata

    Args:
        metadata (dict): dictionary of metadata

    Returns:
        int: a unique checksum for the metadata
    """
    checksum = 0
    for i in metadata.items():
        csum = 1
        for _i in i:
            csum = zlib.adler32(bytes(repr(_i), "utf-8"), csum)
        checksum = checksum ^ csum
    return checksum

def make_dataset_object(dataset: str) -> Dict[str, Any]:
    url = make_url(dataset.lower())
    soup = get_content(url)
    meta = make_additional_meta(soup)

    return dict(
        url=url,
        meta=meta,
        checksum=make_checksum(meta),
        downloads=make_download_links(soup),
        updated=make_metadata(soup)["updated"].isoformat()
    )
