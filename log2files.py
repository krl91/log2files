import argparse
import os
import sys
import shutil
import gzip
import tarfile
import re
from collections import defaultdict
from lxml import etree
from pathlib import Path
from utils import Config
import tkinter as tk
from tkinter import filedialog, messagebox
from tqdm import tqdm
import webbrowser
import base64
import warnings

DEFAULT_CONFIG_PATH = "config.json"

def extract_element_number(element_ref):
    """Extract the element number from an element reference."""
    return element_ref.split(':')[-1]

def extract_timestamp(line):
    """Extract the timestamp from a log line and format it for use in filenames."""
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
    if match:
        timestamp = match.group(1)
        return timestamp.replace(" ", "_").replace(":", "h", 1).replace(":", "m").replace(",", "s")
    return None

def write_xml_fragment(output_dir, element_number, fragment, timestamp, file_counters):
    """Write a single XML fragment to a uniquely named file."""
    index = file_counters[element_number]
    filename = output_dir / f'msg_{element_number}_{index}_{timestamp}.xml'
    with open(filename, 'w', encoding='utf-8') as xml_file:
        xml_file.write(fragment)
    file_counters[element_number] += 1

def process_xml_fragment(fragment, output_dir, filtered_element_numbers_set, config, timestamp, file_counters):
    """Process and save an XML fragment if it matches the filter criteria."""
    try:
        root = etree.fromstring(fragment)
        element_ref = root.find(config.ELEMENT_REF_XPATH).text
        element_number = extract_element_number(element_ref)
        if not filtered_element_numbers_set or element_number in filtered_element_numbers_set:
            write_xml_fragment(output_dir, element_number, fragment, timestamp, file_counters)
    except AttributeError:
        print("Skipping fragment: Missing markup reference")
    except Exception as e:
        print(f"Error processing XML fragment: {e}")

def process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, timestamp, file_counters):
    """Process the entire XML content, extracting and handling relevant fragments."""
    xml_fragments = config.XML_PATTERN.findall(xml_content)
    for fragment in xml_fragments:
        process_xml_fragment(fragment, output_dir, filtered_element_numbers_set, config, timestamp, file_counters)

def get_pu():
    """Return the decoded URL."""
    encoded_url = b'aHR0cHM6Ly9naXRodWIuY29tL2tybDkxL2xvZzJmaWxlcw=='
    return base64.b64decode(encoded_url).decode('utf-8')

def read_file_content(file_path):
    """Read and return the content of a file, handling gzip files if necessary."""
    if file_path.suffix == '.gz':
        return read_gzip_file(file_path)
    return read_plain_file(file_path)

def read_gzip_file(file_path):
    """Read content from a gzip file."""
    with gzip.open(file_path, 'rt', encoding='utf-8') as file:
        return file.read()

def read_plain_file(file_path):
    """Read content from a plain text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def process_tar_gz(file_path, output_dir, filtered_element_numbers_set, config):
    """Process a .tar.gz archive, extracting and processing contained XML files."""
    with tarfile.open(file_path, 'r:gz') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith('.xml'):
                process_tar_member(tar, member, output_dir, filtered_element_numbers_set, config)

def process_tar_member(tar, member, output_dir, filtered_element_numbers_set, config):
    """Extract and process an XML file from a tar member."""
    f = tar.extractfile(member)
    if f:
        xml_content = f.read().decode('utf-8')
        timestamp = extract_timestamp(xml_content)
        process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, timestamp)

def initialize_output_dir(output_dir):
    """Initialize the output directory by clearing it if it exists or creating it."""
    if output_dir.exists() and output_dir.is_dir():
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

def process_files(trace_file_path, output_dir_path, filtered_element_numbers, config):
    """Main function to process log files, extract XML fragments, and save them."""
    trace_file_path = Path(trace_file_path)
    output_dir = Path(str(output_dir_path).strip() or "out")
    initialize_output_dir(output_dir)

    filtered_element_numbers_set = set(filtered_element_numbers.split(';')) if filtered_element_numbers else set()
    file_counters = defaultdict(int)

    if trace_file_path.suffix == '.gz':
        process_compressed_log_file(trace_file_path, output_dir, filtered_element_numbers_set, config, file_counters)
    elif trace_file_path.suffix == '.tar.gz':
        process_tar_gz(trace_file_path, output_dir, filtered_element_numbers_set, config)
    else:
        process_log_file(trace_file_path, output_dir, filtered_element_numbers_set, config, file_counters)

def process_compressed_log_file(trace_file_path, output_dir, filtered_element_numbers_set, config, file_counters):
    """Process a compressed log file (e.g., .gz), extracting and processing XML content."""
    print(f"Processing compressed log file: {trace_file_path}")
    
    # Ouvrir le fichier gzippé et le lire comme texte
    with gzip.open(trace_file_path, 'rt', encoding='utf-8') as file:
        xml_content = file.read()
        timestamp = extract_timestamp(xml_content)
        process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, timestamp, file_counters)


def process_log_file(trace_file_path, output_dir, filtered_element_numbers_set, config, file_counters):
    """Process the log file line by line, extracting and processing XML content."""
    current_timestamp = None
    current_fragment = []

    with open(trace_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in tqdm(lines, desc="Processing log lines", unit="line"):
            current_timestamp, current_fragment = process_log_line(
                line, current_timestamp, current_fragment, output_dir, filtered_element_numbers_set, config, file_counters
            )

    process_final_fragment(current_fragment, current_timestamp, output_dir, filtered_element_numbers_set, config, file_counters)

def process_log_line(line, current_timestamp, current_fragment, output_dir, filtered_element_numbers_set, config, file_counters):
    """Process a single log line, updating the current fragment and timestamp."""
    timestamp = extract_timestamp(line)
    if timestamp:
        if current_fragment:
            xml_content = "".join(current_fragment)
            process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, current_timestamp, file_counters)
            current_fragment = []
        current_timestamp = timestamp
    if current_timestamp:
        current_fragment.append(line)
    return current_timestamp, current_fragment

def process_final_fragment(current_fragment, current_timestamp, output_dir, filtered_element_numbers_set, config, file_counters):
    """Process the final XML fragment after all log lines have been read."""
    if current_fragment:
        xml_content = "".join(current_fragment)
        process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, current_timestamp, file_counters)

def main(args):
    """Load the configuration and either start the CLI or GUI based on the arguments."""
    config_path = args.config_path if args.config_path else DEFAULT_CONFIG_PATH
    config = Config(config_path)
    print(f"Config loaded: {config}")
    print(f"Globals initialized: XML_PATTERN={config.XML_PATTERN}, element_REF_XPATH={config.ELEMENT_REF_XPATH}")

    if args.cli:
        process_files(args.trace_file_path, args.output_dir, args.filtered_element_numbers, config)
    else:
        print("Loading GUI...")
        launch_gui(config)
    
    print(get_pu())

def launch_gui(config):
    """Launch the GUI interface for user interaction."""
    
    def browse_trace_file():
        file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.log;*.gz"), ("All Files", "*.*")])
        if file_path:
            trace_file_entry.delete(0, tk.END)
            trace_file_entry.insert(0, file_path)
    
    def browse_output_dir():
        directory = filedialog.askdirectory()
        if directory:
            output_dir_entry.delete(0, tk.END)
            output_dir_entry.insert(0, directory)
    
    def process_files_gui():
        trace_file_path = trace_file_entry.get()
        output_dir = output_dir_entry.get()
        filtered_element_numbers = filtered_element_numbers_entry.get()
        
        if not trace_file_path:
            messagebox.showerror("Error", "Please select a trace file.")
            return
        
        try:
            process_files(trace_file_path, output_dir, filtered_element_numbers, config)
            messagebox.showinfo("Success", "File processing completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def open_g_l(event):
        webbrowser.open_new(get_pu())

    # Create the main window for the GUI
    root = tk.Tk()
    root.title("Log File Extractor")
    
    # Trace file selection
    tk.Label(root, text="Trace File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    trace_file_entry = tk.Entry(root, width=50)
    trace_file_entry.grid(row=0, column=1, padx=10, pady=10)
    browse_trace_button = tk.Button(root, text="Browse...", command=browse_trace_file)
    browse_trace_button.grid(row=0, column=2, padx=10, pady=10)

    # Output directory selection
    tk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    output_dir_entry = tk.Entry(root, width=50)
    output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
    browse_output_button = tk.Button(root, text="Browse...", command=browse_output_dir)
    browse_output_button.grid(row=1, column=2, padx=10, pady=10)
    
    # Filtered element numbers input
    tk.Label(root, text="Filtered Element Numbers:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    filtered_element_numbers_entry = tk.Entry(root, width=50)
    filtered_element_numbers_entry.grid(row=2, column=1, padx=10, pady=10)
    
    # Process files button
    process_button = tk.Button(root, text="Process Files", command=process_files_gui)
    process_button.grid(row=3, column=1, pady=20)

    # Display the GitHub link and make it clickable
    github_link = tk.Label(root, text=get_pu(), fg="blue", cursor="hand2")
    github_link.grid(row=4, column=1, pady=10)
    github_link.bind("<Button-1>", open_g_l)
    
    root.mainloop()

if __name__ == "__main__":
    print("Starting...")
    parser = argparse.ArgumentParser(description="Process XML, gz, or tar.gz files.")
    parser.add_argument("--config_path", type=str, help="Path to the configuration file (default: config.json)")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")
    parser.add_argument("--trace_file_path", type=str, help="Path to trace file")
    parser.add_argument("--output_dir", type=str, default="out", help="Output directory")
    parser.add_argument("--filtered_element_numbers", type=str, default="", help="Filtered element numbers")
    args = parser.parse_args()

    main(args)
