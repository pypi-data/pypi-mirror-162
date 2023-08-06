from logging import debug, error
import io
from PIL import Image
import sys


def image_resizing(origin: Image, target_size: int) -> Image:
    (width, height) = (origin.size[0], origin.size[1])
    debug(f"origin_width={width}, origin_height={height}")
    aspect_ratio = width / height
    l, r = 1, height
    for _ in range(10000):
        mid = (l + r) // 2
        resized = origin.resize([int(aspect_ratio * mid), mid])
        out = io.BytesIO()
        resized.save(out, format=origin.format, quality=75, subsampling=0)
        size = out.tell()
        debug(f"mid={mid}, size={size}")
        if size <= target_size:
            if (target_size - size) / target_size < 0.02:
                return resized
            l = mid + 1
        else:
            r = mid
        out.flush()
    else:
        error("Timeout")
        sys.exit(1)
