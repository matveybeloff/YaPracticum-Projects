import re
import string


SYMBOLS = string.ascii_letters + string.digits
CUSTOM_ID_LENGTH = 16
MAX_ORIGINAL_URL_LENGTH = 512
DEFAULT_SHORT_ID_LENGTH = 6
FILES_ROUTE = 'files'
RESERVED_SHORT_IDS = {
    FILES_ROUTE,
    'api',
}
SHORT_ID_REGEX = (
    rf'^[{re.escape(SYMBOLS)}]'
    rf'{{1,{CUSTOM_ID_LENGTH}}}$'
)
SHORT_ID_PATTERN = re.compile(SHORT_ID_REGEX)
