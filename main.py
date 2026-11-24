#!/usr/bin/env python3
"""Entrypoint for the news-image-20261124 v3 entry (copy only, stdlib).

Copies the committed poster.png to $MAKEFUN_OUTPUT_DIR/entry.png after
verifying it is a real 1024x1024 PNG under 1 MiB whose sha256 matches the
hash embedded below. No rendering happens at grading time.
"""
import hashlib
import os
import struct
import sys

EXPECTED_SHA256 = "ada9daf9b528017a18ede096f00e96bd9af8caa3273bfe20ca8d09c4c2a10083"  # poster.png
MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is not set")
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "poster.png")
    try:
        with open(src, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        return fail("cannot read poster.png: %s" % exc)
    if len(data) > MAX_BYTES:
        return fail("poster.png is %d bytes, over the 1 MiB limit" % len(data))
    if not data.startswith(PNG_MAGIC):
        return fail("poster.png does not start with the PNG magic bytes")
    if len(data) < 33:
        return fail("poster.png is too short to hold an IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        return fail("poster.png is %dx%d, expected 1024x1024"
                    % (width, height))
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        return fail("poster.png sha256 mismatch: got %s" % digest)
    dest = os.path.join(out_dir, "entry.png")
    try:
        with open(dest, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        return fail("cannot write entry.png: %s" % exc)
    print("wrote %s (%d bytes)" % (dest, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
