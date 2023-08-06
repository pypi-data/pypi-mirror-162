import re
import os
from typing import Optional


def parse_file_size(size: str) -> Optional[int]:
    matched = re.findall(r"(.+?)[k|K|m|M]", size)
    if len(matched) > 0:
        number = int(matched[0])
        match size[-1]:
            case "k" | "K":
                return number * 1000
            case "m" | "M":
                return number * 1000**2


def filepath2basename_without_extension(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]
