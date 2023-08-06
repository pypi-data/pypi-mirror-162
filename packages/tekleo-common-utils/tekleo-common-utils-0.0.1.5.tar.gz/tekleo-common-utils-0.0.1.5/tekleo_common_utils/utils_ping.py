from injectable import injectable, autowired, Autowired
from tekleo_common_message_protocol import PingOutput
from tekleo_common_utils.utils_id import UtilsId
from tekleo_common_utils.utils_time import UtilsTime


@injectable
class UtilsPing:
    @autowired
    def __init__(self, utils_id: Autowired(UtilsId), utils_time: Autowired(UtilsTime)):
        self.utils_id = utils_id
        self.utils_time = utils_time

    def build(self) -> PingOutput:
        id = self.utils_id.generate_uuid()
        success = True
        timestamp = self.utils_time.get_timestamp_ms_now()
        return PingOutput(id, success, timestamp)
