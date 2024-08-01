import unittest
from unittest.mock import patch, mock_open, MagicMock
from collections import defaultdict
from pathlib import Path
import tempfile
import gzip
import tarfile
from log2files import (
    extract_element_number, extract_timestamp, write_xml_fragment,
    process_xml_fragment, process_xml_content, read_file_content,
    process_tar_gz, process_files, main, DEFAULT_CONFIG_PATH
)

class TestSimpleLogfileExtractor(unittest.TestCase):

    def test_extract_element_number(self):
        """Test that element number is correctly extracted from element reference."""
        self.assertEqual(extract_element_number("prefix:suffix:12345"), "12345")
        self.assertEqual(extract_element_number("prefix:67890"), "67890")

    def test_extract_timestamp(self):
        """Test that timestamp is correctly extracted and formatted from a log line."""
        line = "2024-07-31 12:34:56,789 INFO Some log message"
        expected_timestamp = "2024-07-31_12h34m56s789"  # Adjusted to match the output including milliseconds
        self.assertEqual(extract_timestamp(line), expected_timestamp)

        line_no_match = "INFO Some log message without timestamp"
        self.assertIsNone(extract_timestamp(line_no_match))

    @patch('builtins.open', new_callable=mock_open)
    def test_write_xml_fragment(self, mock_open_obj):
        """Test that XML fragment is correctly written to a file."""
        output_dir = Path("/fake/dir")
        element_number = "12345"
        fragment = "<xml>data</xml>"
        timestamp = "2024-07-31_12h34m56s"
        file_counters = defaultdict(int)
        file_counters[element_number] = 0

        write_xml_fragment(output_dir, element_number, fragment, timestamp, file_counters)

        expected_filename = output_dir / "course_12345_0_2024-07-31_12h34m56s.xml"
        mock_open_obj.assert_called_once_with(expected_filename, 'w', encoding='utf-8')
        mock_open_obj().write.assert_called_once_with(fragment)
        self.assertEqual(file_counters[element_number], 1)

    @patch('log2files.write_xml_fragment')
    @patch('lxml.etree.fromstring')
    def test_process_xml_fragment(self, mock_fromstring, mock_write_xml_fragment):
        """Test that XML fragment is processed and written if element number matches filter."""
        fragment = "<DatedElementRef>prefix:suffix:12345</DatedElementRef>"
        output_dir = Path("/fake/dir")
        filtered_element_numbers_set = {"12345"}
        config = MagicMock()
        config.ELEMENT_REF_XPATH = ".//DatedElementRef"
        timestamp = "2024-07-31_12h34m56s"
        file_counters = defaultdict(int)

        mock_fromstring.return_value.find.return_value.text = "prefix:suffix:12345"
        process_xml_fragment(fragment, output_dir, filtered_element_numbers_set, config, timestamp, file_counters)

        mock_write_xml_fragment.assert_called_once()

    @patch('log2files.process_xml_fragment')
    def test_process_xml_content(self, mock_process_xml_fragment):
        """Test that XML content is split into fragments and each fragment is processed."""
        xml_content = "<xml>fragment1</xml><xml>fragment2</xml>"
        output_dir = Path("/fake/dir")
        filtered_element_numbers_set = {"12345"}
        config = MagicMock()
        config.XML_PATTERN.findall.return_value = ["<xml>fragment1</xml>", "<xml>fragment2</xml>"]
        timestamp = "2024-07-31_12h34m56s"
        file_counters = defaultdict(int)

        process_xml_content(xml_content, output_dir, filtered_element_numbers_set, config, timestamp, file_counters)

        self.assertEqual(mock_process_xml_fragment.call_count, 2)

    @patch('builtins.open', new_callable=mock_open, read_data="file content")
    def test_read_file_content_plain(self, mock_open_obj):
        """Test that plain text file content is correctly read."""
        file_path = Path("/fake/dir/file.txt")
        content = read_file_content(file_path)
        mock_open_obj.assert_called_once_with(file_path, 'r', encoding='utf-8')
        self.assertEqual(content, "file content")

    @patch('gzip.open')
    def test_read_file_content_gz(self, mock_gzip_open):
        """Test that gzipped file content is correctly read."""
        mock_gzip_open.return_value.__enter__.return_value.read.return_value = "file content"
        file_path = Path("/fake/dir/file.gz")
        content = read_file_content(file_path)
        mock_gzip_open.assert_called_once_with(file_path, 'rt', encoding='utf-8')
        self.assertEqual(content, "file content")

    @patch('log2files.process_xml_content')
    @patch('tarfile.open')
    def test_process_tar_gz(self, mock_tarfile_open, mock_process_xml_content):
        """Test that tar.gz file is processed and XML files are handled correctly."""
        file_path = Path("/fake/dir/file.tar.gz")
        output_dir = Path("/fake/output")
        filtered_element_numbers_set = {"12345"}
        config = MagicMock()

        tar_mock = MagicMock()
        mock_tarfile_open.return_value.__enter__.return_value = tar_mock
        tar_mock.getmembers.return_value = [MagicMock(name="file.xml", isfile=lambda: True)]
        tar_mock.extractfile.return_value.read.return_value.decode.return_value = "xml content"

        process_tar_gz(file_path, output_dir, filtered_element_numbers_set, config)

        self.assertTrue(mock_process_xml_content.called)

    @patch('log2files.process_xml_content')
    @patch('builtins.open', new_callable=mock_open, read_data="2024-07-31 12:34:56,789 INFO Some log message")
    def test_process_files(self, mock_open_obj, mock_process_xml_content):
        """Test that the main file processing function reads and processes the content correctly."""
        with tempfile.TemporaryDirectory() as temp_output_dir:
            trace_file_path = "/fake/dir/trace.log"
            output_dir_path = temp_output_dir
            filtered_element_numbers = "12345"
            config = MagicMock()

            process_files(trace_file_path, output_dir_path, filtered_element_numbers, config)

            self.assertTrue(mock_open_obj.called)
            self.assertTrue(mock_process_xml_content.called)

    @patch('log2files.Config')
    @patch('log2files.argparse.ArgumentParser.parse_args')
    @patch('builtins.open', new_callable=mock_open, read_data="2024-07-31 12:34:56,789 INFO Some log message")
    def test_default_config_path_used_when_not_provided(self, mock_open_obj, mock_parse_args, mock_config):
        """Test that default config.json is used when --config_path is not provided."""
        # Setup mock for arguments
        mock_args = MagicMock()
        mock_args.config_path = None
        mock_args.cli = True
        mock_args.trace_file_path = '/fake/path/to/trace.log'
        mock_args.output_dir = '/fake/output'
        mock_args.filtered_element_numbers = ''
        mock_parse_args.return_value = mock_args

        with tempfile.TemporaryDirectory() as temp_output_dir:
            mock_args.output_dir = temp_output_dir

            main(mock_args)
        
        # Ensure that the Config object is instantiated with the default config path
        mock_config.assert_called_once_with(DEFAULT_CONFIG_PATH)

if __name__ == '__main__':
    unittest.main()
