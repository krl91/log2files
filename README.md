Installation
------------

- MacOS

brew install python-tk

pip install -r requirements.txt

- Linux Debian

sudo apt-get install python3-tk

pip install -r requirements.txt

- Linux Fedora

sudo dnf install python3-tkinter

pip install -r requirements.txt

-Windows

pip install tk

pip install -r requirements.txt

Usage
-----

- With graphical interface 

python log2files.py --config_path config.json

or

python log2files.py

- Command line:

python log2files.py --cli --trace_file_path "./compressedfile.gz" --output_dir "out" --filtered_journey_numbers "107;22" --config_path config.json

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


Regression Tests on a Complete Dataset (need bash)
--------------------------------------------------

rm -rf ./out && time python log2files.py --cli --trace_file_path file.log --output_dir out --config_path config.json && diff -rq ./out ./out.ref
 
rm -rf ./out && time python log2files.py --cli --trace_file_path file.log --output_dir out --filtered_journey_numbers 992 --config_path config.json&& diff -rq ./out ./out.992.ref

rm -rf ./out && time python log2files.py --cli --trace_file_path file.log --output_dir out --filtered_journey_numbers "992;991" --config_path config.json && diff -rq ./out ./out.992.991.ref

About
-----

Url: https://github.com/krl91/log2files

Contact: krl.project _AT_ gmail (dot) com

Create an esecutable file
-------------------------

pip install pyinstaller
pyinstaller --onefile --noconsole log2files.py