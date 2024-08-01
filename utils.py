import json
import re

class Config:
    def __init__(self, config_path):
        self.load_config(config_path)

    def load_config(self, config_path):
        """Load configuration from a JSON file."""
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        
        self.XML_PATTERN = re.compile(rf'<{config["markup_element_conf"]}>.*?</{config["markup_element_conf"]}>', re.DOTALL)
        self.ELEMENT_REF_XPATH = f'.//{config["markup_date_conf"]}'
