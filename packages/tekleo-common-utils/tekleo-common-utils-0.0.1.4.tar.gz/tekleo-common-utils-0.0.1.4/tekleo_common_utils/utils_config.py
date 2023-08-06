import os
from configparser import ConfigParser, SectionProxy
import threading
from injectable import injectable

config_files_map = {}
config_files_map_lock = threading.Lock()


# A utils class that provides common methods to work with configuration files
@injectable
class UtilsConfig:
    def load_config(self, config_file_path: str) -> bool:
        if os.path.exists(config_file_path):
            with config_files_map_lock:
                config = ConfigParser()
                config.read(config_file_path)
                config_files_map[config_file_path] = config
                return True
        else:
            raise RuntimeError('File at path "' + str(config_file_path) + '" does not exist')

    def get_config(self, config_file_path: str) -> ConfigParser:
        if config_file_path in config_files_map:
            return config_files_map[config_file_path]
        else:
            raise RuntimeError('Config at path "' + str(config_file_path) + '" was not loaded')

    def get_config_section(self, config_file_path: str, section: str) -> SectionProxy:
        config = self.get_config(config_file_path)
        if section in config:
            return config[section]
        else:
            raise RuntimeError('Config at path "' + str(config_file_path) + '" does not have section "' + str(section) + '"')

    def get_config_section_value(self, config_file_path: str, section: str, key: str) -> str:
        section = self.get_config_section(config_file_path, section)
        if key in section:
            return section[key]
        else:
            raise RuntimeError('Config at path "' + str(config_file_path) + '" in section "' + str(section) + '" does not have key "' + str(key) + '"')
