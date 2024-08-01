import argparse
import os
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
import multiprocessing
import multiprocessing.popen_spawn_posix

DEFAULT_CONFIG_PATH = "config.json"

def extract_element_number(element_ref):
    """Extract element number from element reference."""
    return element_ref.split(':')[-1]

def extract_timestamp(line):
    """Extract the timestamp from a log line."""
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
    if match:
        timestamp = match.group(1)
        return timestamp.replace(" ", "_").replace(":", "h", 1).replace(":", "m").replace(",", "s")
    return None

def write_xml_fragment(output_dir, element_number, fragment, timestamp, file_counters):
    """Write XML fragment to a file with a unique name."""
    index = file_counters[element_number]
    filename = output_dir / f'course_{element_number}_{index}_{timestamp}.xml'
    with open(filename, 'w', encoding='utf-8') as xml_file:
        xml_file.write(fragment)
    file_counters[element_number] += 1

def process_xml_fragment(fragment, output_dir, filtered_element_numbers_set, config, timestamp, file_counters):
    """Process a single XML fragment."""
    try:
        root = etree.fromstring(fragment)
        element_ref = root.find(config.ELEMENT_REF_XPATH).text
        element_number = extract_element_number(element_ref)

        if not filtered_element_numbers_set or element_number in filtered_element_numbers_set:
            write_xml_fragment(output_dir, element_number, fragment, timestamp, file_counters)
    except AttributeError:
        print("Skipping fragment: Missing DatedVehicleelementRef")
    except Exception as e:
        print(f"Error processing XML fragment: {e}")

def process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, timestamp, file_counters):
    """Process XML content and extract relevant fragments."""
    xml_fragments = config.XML_PATTERN.findall(xml_content)
    for fragment in xml_fragments:
        process_xml_fragment(fragment, output_dir, filtered_element_numbers_set, config, timestamp, file_counters)

def read_file_content(file_path):
    """Read and return file content based on file type."""
    if file_path.suffix == '.gz':
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            return file.read()
    else:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

def process_tar_gz(file_path, output_dir, filtered_element_numbers_set, config):
    """Process .tar.gz file to extract and handle XML files."""
    with tarfile.open(file_path, 'r:gz') as tar:
        members = [m for m in tar.getmembers() if m.isfile() and m.name.endswith('.xml')]
        for member in tqdm(members, desc="Processing tar.gz members", unit="file"):
            f = tar.extractfile(member)
            if f:
                xml_content = f.read().decode('utf-8')
                timestamp = extract_timestamp(xml_content)
                process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, timestamp)

def process_files(trace_file_path, output_dir_path, filtered_element_numbers, config):
    """Main function to process input files."""
    trace_file_path = Path(trace_file_path)
    output_dir = Path(output_dir_path.strip() or "out")

    if output_dir.exists() and output_dir.is_dir():
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    filtered_element_numbers_set = set(filtered_element_numbers.split(';')) if filtered_element_numbers else set()
    file_counters = defaultdict(int)

    current_timestamp = None
    current_fragment = []

    with open(trace_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in tqdm(lines, desc="Processing log lines", unit="line"):
            timestamp = extract_timestamp(line)
            if timestamp:
                if current_fragment:
                    xml_content = "".join(current_fragment)
                    process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, current_timestamp, file_counters)
                    current_fragment = []
                current_timestamp = timestamp
            if current_timestamp:
                current_fragment.append(line)

    # Process the last fragment if exists
    if current_fragment:
        xml_content = "".join(current_fragment)
        process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, current_timestamp, file_counters)

    print("File processing completed.")
    print("https://github.com/krl91/log2files")  # Affichage du lien en ligne de commande

def main(args):
    config_path = args.config_path if args.config_path else DEFAULT_CONFIG_PATH
    config = Config(config_path)
    print(f"Config loaded: {config}")  # Debugging line
    print(f"Globals initialized: XML_PATTERN={config.XML_PATTERN}, ELEMENT_REF_XPATH={config.ELEMENT_REF_XPATH}")  # Debugging line

    if args.cli:
        process_files(args.trace_file_path, args.output_dir, args.filtered_element_numbers, config)
    else:
        launch_gui(config)

def launch_gui(config):
    """Launch the GUI to interact with the user."""
    
    def browse_trace_file():
        file_path = filedialog.askopenfilename(filetypes=[("Log Files", "*.log"), ("All Files", "*.*")])
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

    def open_url(event):
        webbrowser.open_new("https://github.com/krl91/log2files")
    
    # Creating the main window
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
    
    # Filtered element numbers
    tk.Label(root, text="Filtered element Numbers:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    filtered_element_numbers_entry = tk.Entry(root, width=50)
    filtered_element_numbers_entry.grid(row=2, column=1, padx=10, pady=10)
    
    # Process button
    process_button = tk.Button(root, text="Process Files", command=process_files_gui)
    process_button.grid(row=3, column=1, pady=20)

    # Display the GitHub link
    url_label = tk.Label(root, text="https://github.com/krl91/log2files", fg="blue", cursor="hand2")
    url_label.grid(row=4, column=1, pady=10)
    url_label.bind("<Button-1>", open_url)
    
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Process XML, gz, or tar.gz files.")
    parser.add_argument("--config_path", type=str, help="Path to the configuration file (default: config.json)")
    parser.add_argument("--cli", action="store_true", help="Run in command-line mode")
    parser.add_argument("--trace_file_path", type=str, help="Path to trace file")
    parser.add_argument("--output_dir", type=str, default="out", help="Output directory")
    parser.add_argument("--filtered_element_numbers", type=str, default="", help="Filtered element numbers")
    args = parser.parse_args()

    config_path = args.config_path if args.config_path else DEFAULT_CONFIG_PATH
    config = Config(config_path)
    print(f"Config loaded: {config}")
    print(f"Globals initialized: XML_PATTERN={config.XML_PATTERN}, ELEMENT_REF_XPATH={config.ELEMENT_REF_XPATH}")

    if args.cli:
        process_files(args.trace_file_path, args.output_dir, args.filtered_element_numbers, config)
    else:
        launch_gui(config)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
