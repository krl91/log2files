import unittest
import subprocess
import os

class TestFunctionalLogfileExtractor(unittest.TestCase):

    def run_command(self, command):
        """Helper function to run shell command and return exit code."""
        process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.returncode, process.stdout, process.stderr

    def test_functional_full_process(self):
        """Test processing a log file and comparing with reference output."""
        command = "rm -rf ./out && time python log2files.py --cli --trace_file_path ./test_datasets/file.log --output_dir out --config_path config.json && diff -rq ./out ./test_datasets/out.ref"
        return_code, _, _ = self.run_command(command)
        self.assertEqual(return_code, 0, "Functional test failed: full process without filters")

    def test_functional_filtered_992(self):
        """Test processing a log file with filtered element 992 and comparing with reference output."""
        command = "rm -rf ./out && time python log2files.py --cli --trace_file_path ./test_datasets/file.log --output_dir out --filtered_element_numbers 992 --config_path config.json && diff -rq ./out ./test_datasets/out.992.ref"
        return_code, _, _ = self.run_command(command)
        self.assertEqual(return_code, 0, "Functional test failed: filtered process with element 992")

    def test_functional_filtered_992_991(self):
        """Test processing a log file with filtered elements 992 and 991 and comparing with reference output."""
        command = "rm -rf ./out && time python log2files.py --cli --trace_file_path ./test_datasets/file.log --output_dir out --filtered_element_numbers '992;991' --config_path config.json && diff -rq ./out ./test_datasets/out.992.991.ref"
        return_code, _, _ = self.run_command(command)
        self.assertEqual(return_code, 0, "Functional test failed: filtered process with elements 992 and 991")

    def test_functional_gz_file(self):
        """Test processing a compressed log file and comparing with reference output."""
        command = "rm -rf ./out && time python log2files.py --cli --trace_file_path ./test_datasets/file.log.gz --output_dir out --config_path config.json && diff -rq ./out ./test_datasets/out.gz.ref"
        return_code, _, _ = self.run_command(command)
        self.assertEqual(return_code, 0, "Functional test failed: processing gzip file")

    def test_functional_gz_filtered(self):
        """Test processing a compressed log file with filtered elements and comparing with reference output."""
        command = "rm -rf ./out && time python log2files.py --cli --trace_file_path ./test_datasets/file.log.gz --output_dir out --filtered_element_numbers '433;24' --config_path config.json && diff -rq ./out ./test_datasets/out.gz.433.24.ref"
        return_code, _, _ = self.run_command(command)
        self.assertEqual(return_code, 0, "Functional test failed: processing gzip file with filtered elements 433 and 24")

if __name__ == '__main__':
    unittest.main()

