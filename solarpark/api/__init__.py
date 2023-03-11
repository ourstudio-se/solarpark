import re


def parse_integrity_error_msg(regex: str, msg: str) -> str:
    match = re.search(regex, msg)
    if match:
        return match.group()
    return "unique violation on field value"
