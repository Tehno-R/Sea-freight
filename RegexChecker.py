import re
from log import logger


class RegexPattern:
    @staticmethod
    def check_number(number: str) -> bool:
        if not isinstance(number, str):
            return False
        regex_pattern = re.compile(r"^\+7[0-9]{10}$")
        return regex_pattern.match(number) is not None

    @staticmethod
    def check_int(raw_int: str) -> int | None:
        if not isinstance(raw_int, str):
            return None
        try:
            value = int(raw_int)
            if 0 <= value <= 4294967296:
                return value
            else:
                return None
        except ValueError:
            logger.warning("RegexChecker: Error checking id")
            return None