import json
import os
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from drain3.masking import MaskingInstruction

class LogParser:
    def __init__(self, log_type, config_dir=None):
        """
        Initialize the LogParser with a specific log type configuration.
        
        Args:
            log_type (str): The name of the log type (e.g., 'HDFS', 'Apache'). 
                            This corresponds to the JSON config filename.
            config_dir (str, optional): Directory containing the JSON config files. 
                                        Defaults to the directory of this script.
        """
        self.log_type = log_type
        if config_dir is None:
            self.config_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.config_dir = config_dir
            
        self.config = self._load_config()
        self.template_miner = TemplateMiner(config=self.config)

    def _load_config(self):
        config_path = os.path.join(self.config_dir, f"{self.log_type}.json")
        drain_config = TemplateMinerConfig()
        
        if os.path.exists(config_path):
            print(f"Loading configuration from {config_path}")
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            
                drain_config.drain_sim_th = config_dict.get("drain_sim_th", drain_config.drain_sim_th)
                drain_config.drain_depth = config_dict.get("drain_depth", drain_config.drain_depth)
            
                masking_instructions = []
                temp = config_dict["masking_instructions"]
                for mi in config_dict["masking_instructions"]:
                    masking_instructions.append(
                        MaskingInstruction(mi['regex_pattern'], mi['mask_with'])
                    )
                drain_config.masking_instructions = masking_instructions
                
        else:
            print(f"Warning: Config file {config_path} not found. Using default configuration.")
            
        return drain_config

    def parse(self, log_line):
        """
        Parse a single log line.
        
        Args:
            log_line (str): The raw log line string.
            
        Returns:
            dict: The result dictionary containing 'cluster_id', 'template_mined', etc.
        """
        # Strip whitespace
        log_line = log_line.strip()
        return self.template_miner.add_log_message(log_line)

    def get_templates(self):
        """
        Get all mined templates.
        
        Returns:
            list: List of clusters/templates.
        """
        return self.template_miner.drain.clusters
