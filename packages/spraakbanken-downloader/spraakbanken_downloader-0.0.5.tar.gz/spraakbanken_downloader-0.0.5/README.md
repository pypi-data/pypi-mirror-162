# SCRIBE/Spraakbanken data downloader
<!-- include data/img.png -->
![](data/img.png)

This is a project in progress, with the core functionality being interactive, version-checked downloads with user prompting for the following datasets:

* [NST](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-54/)
* [NPSC](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-58/)
* [NB tale](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-31/)
* more to come...

### System components
- Metadata handling
    - Web scraper (online information)
    - PDF
    - XML
- Downloader
    - Downloading the files
- Data extraction (TODO)
    - Reformat the downloaded data into a unified format, as described [in the `combined_dataset` repo](https://github.com/scribe-project/combined_dataset)
- Parsing (TODO)

## Installation
`pip install spraakbanken-downloader`

## Usage (from pip installation)
- For the interactive downloader:
    - `python -m spraakbanken`
- With specific arguments:
    - `python -m spraakbanken --dataset nst`
    - See below for supported arguments
___
## Arguments
-------------     
| Option String | Required | Default | Option Summary |  
|---------------|----------|---------|----------------|  
| ['-d', '--dataset'] | `False` | `None` | Optional specific dataset| 
| ['-v', '--verbose'] | `False` | `False` | Verbose to print meta in console| 
| ['-o', '--outdir'] | `False` | `current_dir/data` | Specify output dir |
| ['-m', '--meta'] | `False` | `False` | Mock run to test download of metadata. Will download to `outdir` | 

## Local usage
1. install dependencies first `make install`  
2. subsequent runs: `make` which in turns runs linting and the main file, prompting you for which dataset to download. 
## Usage (Local: Accessing python files directly)
run the main file with a `--dataset (-d)` argument:

`python src/spraakbanken/__main__.py --dataset *somedataset*` (where dataset is in {nst, storting, nbtale})

e.g.

`python src/spraakbanken/__main__.py --dataset nst`


this guides you through the download process, based on information from the Sprakbanken websites, as such:

### New datasets:
```
Fetching data for dataset: 'nst'
----------------------------------------
Last updated at 2020-07-31
Accessed URL 'https://www.nb.no/SPRAKBANKEN/ressurskatalog//oai-nb-no-sbr-54/' at 03-08-2022_16-10-09
Found the following files:
1. ADB_NOR_0463.tar.gz
2. ADB_NOR_0464.tar.gz
3. ADB_OD_Nor.NOR.tar.gz
4. lydfiler_16_1_a.tar.gz
5. lydfiler_16_1_b.tar.gz
6. lydfiler_16_1_c.tar.gz
7. lydfiler_16_1_d.tar.gz
8. lydfiler_16_2_a.tar.gz
9. lydfiler_16_2_b.tar.gz
10. lydfiler_16_2_c.tar.gz
11. lydfiler_16_2_d.tar.gz
12. lydfiler_16_begge_a.tar.gz
13. lydfiler_16_begge_b.tar.gz
14. lydfiler_16_begge_c.tar.gz
15. lydfiler_16_begge_d.tar.gz
Download? [yes (Y) / no (N)]
```

### Existing local datasets
The metadata fetching process stores the data locally, along with a checksum to match the data points. An example file name is `nbtale/3676375100_02-08-2022_20-14-59.json`
the first part being the checksum, the rest being the date and time accessed.

Within this file is the corresponding metadata to each dataset. Varying data points are fetched, as this is not standardized by Sprakbanken.

Given that a checksum-file is matching the newly fetched metadata, the user is prompted as such:

```
Last updated at 2015-12-22
Accessed URL 'https://www.nb.no/SPRAKBANKEN/ressurskatalog//oai-nb-no-sbr-31/' at 03-08-2022_16-14-45
Dataset 'nbtale' already downloaded
Continue to download regardless? [yes (Y) / no (N)] 
```

if "y", the user continues to the same pipeline as above:
```
Continue to download regardless? [yes (Y) / no (N)] y
Found the following files:
1. sennheiser_1.tar.gz
2. sennheiser_2.tar.gz
3. sennheiser_3.tar.gz
4. shure_1.tar.gz
5. shure_2.tar.gz
6. shure_3.tar.gz
Download? [yes (Y) / no (N)]  
```

### Meta file example (Storting corpus):
There is still a bit of work left to store proper data fields. The sprakbanken websites are not web scraper friendly.
```
{
    "corpus audio info": {
        "size": "140",
        "size unit": "files",
        "duration unit": "hours",
        "mime type": "audio/wav",
        "signal encoding": "linearpcm",
        "sampling rate": "48000",
        "quantization": "16",
        "byte order": "littleendian",
        "sign convention": "signedinteger",
        "number of tracks": "2",
        "recording quality": "medium"
    },
    "audio size info": {
        "size": "140",
        "size unit": "files",
        "duration unit": "hours"
    },
    "size info": {
        "size": "1198590",
        "size unit": "words"
    },
    "duration of effective speech info": {
        "size": "126",
        "duration unit": "hours"
    },
    "duration of audio info": {
        "size": "140",
        "duration unit": "hours"
    },
    "audio format info": {
        "mime type": "audio/wav",
        "signal encoding": "linearpcm",
        "sampling rate": "48000",
        "quantization": "16",
        "byte order": "littleendian",
        "sign convention": "signedinteger",
        "number of tracks": "2",
        "recording quality": "medium"
    },
    "corpus text info": {
        "size": "1198590",
        "size unit": "words",
        "character encoding": "utf-8"
    },
    "text format info": {
        "size": "1198590",
        "size unit": "words"
    },
    "size per text format": {
        "size": "1198590",
        "size unit": "words"
    },
    "character encoding info": {
        "character encoding": "utf-8"
    }
}
```
