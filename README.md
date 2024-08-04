Installation
------------

Download the zip file according to your OS.
Unzip it.

Download the config.json file and modify it according to the log file to be parsed.

Config file should be at the same folder as the executable file.

By default the gui is launched.


Installation from sources
-------------------------

- MacOS

brew install python-tk

pip install -r requirements.txt

- Linux Debian

sudo apt-get install python3-tk

pip install -r requirements.txt

- Linux Fedora

sudo dnf install python3-tkinter

pip install -r requirements.txt

- Windows

pip install tk

pip install -r requirements.txt

Usage
-----

log2files.py [-h] [--config_path CONFIG_PATH] [--cli] [--trace_file_path TRACE_FILE_PATH] [--output_dir OUTPUT_DIR] [--filtered_element_numbers FILTERED_ELEMENT_NUMBERS] [--version] [--debug]

Process XML, gz, or tar.gz files.

options:
  -h, --help            show this help message and exit
  --config_path CONFIG_PATH
                        Path to the configuration file (default: config.json)
  --cli                 Run in command-line mode
  --trace_file_path TRACE_FILE_PATH
                        Path to trace file
  --output_dir OUTPUT_DIR
                        Output directory
  --filtered_element_numbers FILTERED_ELEMENT_NUMBERS
                        Filtered element numbers
  --version             current version number
  --debug               Enable debug logging

- With graphical interface 

python log2files.py --config_path config.json

or

python log2files.py

- Command line:

python log2files.py --cli --trace_file_path "./compressedfile.gz" --output_dir "out" --filtered_element_numbers "107;22" --config_path config.json

Config file example
-------------------
{
    "markup_element_conf": "Element",
    "markup_date_conf": "Date"
}


Unit Tests
----------

python -m unittest test_log2files.py

python -m unittest test_utils.py


Functionnal Tests on a Complete Dataset 
---------------------------------------

python test_functional.p

About
-----

Url: https://github.com/krl91/log2files

Create an esecutable file
-------------------------

pip install pyinstaller

pyinstaller --onefile log2files.py
