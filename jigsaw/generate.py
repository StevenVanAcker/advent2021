#!/usr/bin/env python3

import sys
import os
import subprocess
import random
import hashlib
import base64
import json


def getObjects(fn):
    lines = subprocess.check_output([
        "inkscape",
        "--query-all",
        fn
    ]).decode().split("\n")

    lines = [x for x in lines if x != ""]

    out = []
    for line in lines:
        parts = line.split(",")
        # the object named "svg8" contains the entire image
        if "svg" in parts[0]:
            continue

        rec = {
            "name": parts[0],
            "x": float(parts[1]),
            "y": float(parts[2]),
            "w": float(parts[3]),
            "h": float(parts[4]),
        }

        out += [rec]

    return out


def calculateDistribution(numpieces, data):
    """
    How to split the data over <numpieces> puzzle pieces using 2 and 3 byte chunks
    """

    assert len(data) >= numpieces * 2
    assert len(data) <= numpieces * 3

    remaining = len(data) - (numpieces * 2)

    numbers = [3] * remaining
    numbers += [2] * (numpieces - len(numbers))

    assert sum(numbers) == len(data)
    assert len(numbers) == numpieces
    random.shuffle(numbers)

    offset = 0
    out = []
    for size in numbers:
        out += [data[offset:offset + size]]
        offset += size

    return out


def sortedPieces(pieces):
    # first, find the lowest y offset, which is the top of the image
    lowesty = min([r["y"] for r in pieces])

    # now find all pieces with that y offset, that will be the top row
    toprow = [r for r in pieces if r["y"] == lowesty]

    # now we know the dimensions of the puzzle
    width = len(toprow)
    height = int(len(pieces) / width)

    print(f"Puzzle pieces: {width} x {height}")

    # now sort all pieces by Y value, and split them chunks of length <width>
    ysortedlist = sorted(pieces, key=lambda r: r["y"])
    out = []
    for rowid in range(height):
        row = ysortedlist[rowid * width: (rowid+1) * width]
        # sort this row by X value
        row = sorted(row, key=lambda r: r["x"])

        for col, piece in enumerate(row):
            piece["row"] = rowid
            piece["column"] = col
            out += [piece]

    return out


def extractPiece(fn, rec, data):
    os.makedirs("data", exist_ok=True)

    recname = rec["name"]
    outfn = os.path.join("data", f"{recname}.png")

    # first cut out the piece
    subprocess.check_output([
        "inkscape",
        '--export-type=png',
        f'--export-id={rec["name"]}',
        "--export-id-only",
        "--export-background-opacity=0",
        "--export-dpi=600",
        f'--export-filename={outfn}',
        fn
    ])

    # next, rotate the piece
    angle = random.choice([0, 90, 180, 270])
    rec["rotate"] = angle
    tmpfile = os.path.join("data", "tempfile.png")
    subprocess.check_output(["convert", "-rotate", f"{angle}", outfn, tmpfile])
    subprocess.check_output(["mv", tmpfile, outfn])

    # then, store exif data
    rec["data"] = data
    subprocess.check_output(
        ["exiftool", "-overwrite_original", "-all=", f"-Comment=Secret data: '{data}'", outfn])

    # finally, calculate sha256sum
    h = hashlib.sha256(open(outfn, "rb").read()).hexdigest()

    # and rename the file
    newfn = f"{h}.png"
    newpath = os.path.join("data", newfn)

    subprocess.check_output(["mv", outfn, newpath])

    rec["filename"] = newfn
    return rec


if __name__ == "__main__":
    svgfile = sys.argv[1]
    secretdatafile = sys.argv[2]
    resultfile = sys.argv[3]

    secretdata = open(secretdatafile, "rb").read()
    secretdata = base64.b64encode(secretdata).decode()

    puzzlepieces = sortedPieces(getObjects(svgfile))
    pcount = len(puzzlepieces)
    datapieces = calculateDistribution(pcount, secretdata)

    result = []
    for data, rec in zip(datapieces, puzzlepieces):
        result += [extractPiece(svgfile, rec, data)]

    json.dump(result, open(resultfile, "w"))
