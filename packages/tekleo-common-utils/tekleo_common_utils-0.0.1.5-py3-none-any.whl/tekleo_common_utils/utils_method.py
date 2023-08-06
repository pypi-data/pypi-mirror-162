import time
import traceback
from typing import List, Dict
from injectable import injectable


@injectable
class UtilsMethod:
    # In this case positional_arguments needs to be a list or tuple or similar, and keyword_arguments is a dict or similar.
    def execute_with_retries(self, call_to_execute, positional_arguments: List, keyword_arguments: Dict, max_number_of_tries: int = 3, delay_between_tries_in_seconds: float = 0.5):
        result = None
        needs_to_keep_trying = True
        tries_count = 0
        last_exception = None
        while needs_to_keep_trying:
            tries_count = tries_count + 1

            # Try the method call
            try:
                result = call_to_execute(*positional_arguments, **keyword_arguments)
            except Exception as exception:
                #traceback.print_exc()
                last_exception = exception
                result = None

            # Exit the loop if result was obtained
            if result is not None:
                needs_to_keep_trying = False
            # If an error occurred and we need to retry - sleep for a few moments
            else:
                time.sleep(delay_between_tries_in_seconds)

            # Exit the loop if number of tries gets exceeded
            if tries_count >= max_number_of_tries:
                needs_to_keep_trying = False

        if result is None:
            raise RuntimeError("Despite all tries to execute the request, result was not obtained") from last_exception

        return result
