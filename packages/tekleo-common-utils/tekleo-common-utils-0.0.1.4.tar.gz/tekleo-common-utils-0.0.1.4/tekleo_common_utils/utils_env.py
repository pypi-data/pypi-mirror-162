import os
import threading
from typing import List
from injectable import injectable

environment_variables_map = {}
environment_variables_map_lock = threading.Lock()


# A utils class that provides common methods to deal with global environment variables
# This class has 2 main functions - load variables into memory, retrieve variables from memory
# To set these variables use docker's "-e" flag
#
# Try to follow the convention, variable name can be like "CASEDRIVE_ENV" or "A360_ENV" or "A360_SPACY_VERSION"
# And values can be like "local", "test", "prod", "v1", "default" etc
@injectable
class UtilsEnv:
    def load_environment_variable(self, environment_variable_name: str) -> bool:
        with environment_variables_map_lock:
            if environment_variable_name in os.environ:
                environment_variables_map[environment_variable_name] = os.environ[environment_variable_name]
                return True
            else:
                print('UtilsEnv.load_environment_variable(): Warning! Environment variable "' + str(environment_variable_name) + '"  not found')
                return False

    def load_environment_variables(self, list_of_environment_variable_names: List[str]) -> List[bool]:
        results = []
        for environment_variable_name in list_of_environment_variable_names:
            result = self.load_environment_variable(environment_variable_name)
            results.append(result)
        return results

    def get_environment_variable(self, environment_variable_name: str, default_value: str = '') -> str:
        if environment_variable_name in environment_variables_map:
            return environment_variables_map[environment_variable_name]
        else:
            return default_value
