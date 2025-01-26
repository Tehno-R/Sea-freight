import re
from log import logger


class RegexPattern:
    @staticmethod
    def check_number(number: str) -> str | None:
        if not isinstance(number, str):
            return None
        regex_pattern = re.compile(r"^\+7[0-9]{10}$")
        return number if regex_pattern.match(number) is not None else None

    @staticmethod
    def date_check(date: str) -> str | None:
        if not isinstance(date, str):
            return None
        regex_pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
        return date if regex_pattern.match(date) is not None else None

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