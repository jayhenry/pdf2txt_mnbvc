# borrow from https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/text-extraction/fitzcli.py
import argparse
import os
import sys
import time
import bisect
import fitz
from typing import List
from fitz.fitz import (
    TEXT_INHIBIT_SPACES,
    TEXT_PRESERVE_LIGATURES,
    TEXT_PRESERVE_WHITESPACE,
)

mycenter = lambda x: (" %s " % x).center(75, "-")


def open_file(filename, password, show=False, pdf=True):
    """Open and authenticate a document."""
    doc = fitz.open(filename)
    if not doc.is_pdf and pdf is True:
        sys.exit("this command supports PDF files only")
    rc = -1
    if not doc.needs_pass:
        return doc
    if password:
        rc = doc.authenticate(password)
        if not rc:
            sys.exit("authentication unsuccessful")
        if show is True:
            print("authenticated as %s" % "owner" if rc > 2 else "user")
    else:
        sys.exit("'%s' requires a password" % doc.name)
    return doc


def get_list(rlist, limit, what="page"):
    """Transform a page / xref specification into a list of integers.

    Args
    ----
        rlist: (str) the specification
        limit: maximum number, i.e. number of pages, number of objects
        what: a string to be used in error messages
    Returns
    -------
        A list of integers representing the specification.
    """
    N = str(limit - 1)
    rlist = rlist.replace("N", N).replace(" ", "")
    rlist_arr = rlist.split(",")
    out_list = []
    for seq, item in enumerate(rlist_arr):
        n = seq + 1
        if item.isdecimal():  # a single integer
            i = int(item)
            if 1 <= i < limit:
                out_list.append(int(item))
            else:
                sys.exit("bad %s specification at item %i" % (what, n))
            continue
        try:  # this must be a range now, and all of the following must work:
            i1, i2 = item.split("-")  # will fail if not 2 items produced
            i1 = int(i1)  # will fail on non-integers
            i2 = int(i2)
        except:
            sys.exit("bad %s range specification at item %i" % (what, n))

        if not (1 <= i1 < limit and 1 <= i2 < limit):
            sys.exit("bad %s range specification at item %i" % (what, n))

        if i1 == i2:  # just in case: a range of equal numbers
            out_list.append(i1)
            continue

        if i1 < i2:  # first less than second
            out_list += list(range(i1, i2 + 1))
        else:  # first larger than second
            out_list += list(range(i1, i2 - 1, -1))

    return out_list


def page_simple(page, textout, GRID, fontsize, noformfeed, skip_empty, flags):
    if noformfeed:
        eop = b"\n"
    else:
        eop = bytes([12])
    text = page.get_text("text", flags=flags)
    if not text:
        if not skip_empty:
            textout.write(eop)  # write formfeed
        return
    textout.write(text.encode("utf8", errors="surrogatepass"))
    textout.write(eop)
    return


def page_blocksort(page, textout, GRID, fontsize, noformfeed, skip_empty, flags):
    if noformfeed:
        eop = b"\n"
    else:
        eop = bytes([12])
    blocks = page.get_text("blocks", flags=flags)
    if blocks == []:
        if not skip_empty:
            textout.write(eop)  # write formfeed
        return
    blocks.sort(key=lambda b: (b[3], b[0]))  # y1, x0
    for b in blocks:
        textout.write(b[4].encode("utf8", errors="surrogatepass"))
    textout.write(eop)
    return


def page_layout(page, textout, GRID, fontsize, noformfeed, skip_empty, flags, clip):
    left = page.rect.width  # left most used coordinate
    right = 0  # rightmost coordinate
    rowheight = page.rect.height  # smallest row height in use
    chars = []  # all chars here
    rows = set()  # bottom coordinates of lines
    if noformfeed:
        eop = b"\n"
    else:
        eop = bytes([12])

    # --------------------------------------------------------------------
    def curate_rows(rows, GRID):
        """Make list of integer y-coordinates of lines on page.

        Coordinates will be ascending and differ by 'GRID' points or more."""
        rows = list(rows)
        rows.sort()  # sort ascending
        nrows = [rows[0]]
        for h in rows[1:]:
            if h >= nrows[-1] + GRID:  # only keep significant differences
                nrows.append(h)
        return nrows  # curated list of line bottom coordinates

    # --------------------------------------------------------------------
    def curate_rows(rows, GRID):
        """Make list of integer y-coordinates of lines on page.

        Coordinates will be ascending and differ by 'GRID' points or more."""
        rows = list(rows)
        rows.sort()  # sort ascending
        nrows = [rows[0]]
        for h in rows[1:]:
            if h >= nrows[-1] + GRID:  # only keep significant differences
                nrows.append(h)
        return nrows  # curated list of line bottom coordinates

    # --------------------------------------------------------------------
    def find_line_index(values: List[int], value: int) -> int:
        """Find the right row coordinate (using bisect std package).

        Args:
            values: (list) y-coordinates of rows.
            value: (int) lookup for this value (y-origin of char).
        Returns:
            y-ccordinate of appropriate line for value.
        """
        i = bisect.bisect_right(values, value)
        if i:
            return values[i - 1]
        raise RuntimeError("Line for %g not found in %s" % (value, values))

    # --------------------------------------------------------------------
    def make_lines(chars):
        lines = {}  # key: y1-ccordinate, value: char list
        for c in chars:
            ch, ox, oy, cwidth = c
            y = find_line_index(rows, oy)  # index of origin.y
            lchars = lines.get(y, [])  # read line chars so far
            lchars.append(c)
            lines[y] = lchars  # write back to line

        # ensure line coordinates are ascending
        keys = list(lines.keys())
        keys.sort()
        return lines, keys

    # --------------------------------------------------------------------
    def compute_slots(keys, lines, right, left):
        """Compute "char resolution" for the page.

        The char width corresponding to 1 text char position on output - call
        it 'slot'.
        For each line, compute median of its char widths. The minimum across
        all "relevant" lines is our 'slot'.
        The minimum char width of each line is used to determine if spaces must
        be inserted in between two characters.
        """
        slot = used_width = right - left
        lineslots = {}
        for k in keys:
            lchars = lines[k]  # char tuples of line
            ccount = len(lchars)  # how many
            if ccount < 2:  # if short line, just put in something
                lineslots[k] = (1, 1, 1)
                continue
            widths = [c[3] for c in lchars]  # list of all char widths
            widths.sort()
            line_width = sum(widths)  # total width used by line
            i = int(ccount / 2 + 0.5)  # index of median
            median = widths[i]  # take the median value
            if (
                line_width / used_width >= 0.3 and median < slot
            ):  # if line is significant
                slot = median  # update global slot
            lineslots[k] = (widths[0], median, widths[-1])  # line slots
        return slot, lineslots

    # --------------------------------------------------------------------
    def joinligature(lig):
        """Return ligature character for a given pair / triple of characters.

        Args:
            lig: (str) 2/3 characters, e.g. "ff"
        Returns:
            Ligature, e.g. "ff" -> chr(0xFB00)
        """
        if lig == "ff":
            return chr(0xFB00)
        elif lig == "fi":
            return chr(0xFB01)
        elif lig == "fl":
            return chr(0xFB02)
        elif lig == "ft":
            return chr(0xFB05)
        elif lig == "st":
            return chr(0xFB06)
        elif lig == "ffi":
            return chr(0xFB03)
        elif lig == "ffl":
            return chr(0xFB04)
        return lig

    # --------------------------------------------------------------------
    def process_blocks(page, flags, clip):
        left = page.rect.width  # left most used coordinate
        right = 0  # rightmost coordinate
        rowheight = page.rect.height  # smallest row height in use
        chars = []  # all chars here
        rows = set()  # bottom coordinates of lines
        blocks = page.get_text("rawdict", flags=flags, clip=clip)["blocks"]
        for block in blocks:
            for line in block["lines"]:
                if line["dir"] != (1, 0):  # ignore non-horizontal text
                    continue
                x0, y0, x1, y1 = line["bbox"]
                if y1 < 0 or y0 > page.rect.height:  # ignore if outside CropBox
                    continue
                # upd row height
                height = y1 - y0

                if rowheight > height:
                    rowheight = height
                for span in line["spans"]:
                    if span["size"] <= fontsize:
                        continue
                    for c in span["chars"]:
                        x0, _, x1, _ = c["bbox"]
                        cwidth = x1 - x0
                        ox, oy = c["origin"]
                        oy = int(round(oy))
                        rows.add(oy)
                        ch = c["c"]
                        if left > ox and ch != " ":
                            left = ox  # update left coordinate
                        if right < x1:
                            right = x1  # update right coordinate
                        # handle ligatures:
                        if cwidth == 0 and chars != []:  # potential ligature
                            old_ch, old_ox, old_oy, old_cwidth = chars[-1]
                            if old_oy == oy:  # ligature!
                                if old_ch != chr(0xFB00):  # previous "ff" char lig?
                                    lig = joinligature(old_ch + ch)  # 2-char
                                # convert to one of the 3-char ligatures:
                                elif ch == "i":
                                    lig = chr(0xFB03)  # "ffi"
                                elif ch == "l":
                                    lig = chr(0xFB04)  # "ffl"
                                else:  # something wrong, leave old char in place
                                    lig = old_ch
                                chars[-1] = (lig, old_ox, old_oy, old_cwidth)
                                continue
                        chars.append((ch, ox, oy, cwidth))  # all chars on page
        return rows, chars, rowheight, left, right

    # --------------------------------------------------------------------
    def make_textline(left, slot, lineslots, lchars):
        """Produce the text of one output line.

        Args:
            left: (float) left most coordinate used on page
            slot: (float) avg width of one character in any font in use.
            minslot: (float) min width for the characters in this line.
            chars: (list[tuple]) characters of this line.
        Returns:
            text: (str) text string for this line
        """
        minslot, median, maxslot = lineslots
        text = ""  # we output this
        old_x1 = 0  # end coordinate of last char
        old_ox = 0  # x-origin of last char
        if minslot <= fitz.EPSILON:
            raise RuntimeError("program error: minslot too small = %g" % minslot)

        for c in lchars:  # loop over characters
            char, ox, _, cwidth = c
            ox = ox - left  # its (relative) start coordinate
            x1 = ox + cwidth  # ending coordinate

            # eliminate overprint effect
            if (
                old_ox <= ox < old_x1
                and char == text[-1]
                and ox - old_ox <= cwidth * 0.2
            ):
                continue

            # omit spaces overlapping previous char
            if char == " " and (old_x1 - ox) / cwidth > 0.8:
                continue

            # close enough to previous?
            if ox < old_x1 + minslot:  # assume char adjacent to previous
                text += char  # append to output
                old_x1 = x1  # new end coord
                old_ox = ox  # new origin.x
                continue

            # else next char starts after some gap:
            # fill in right number of spaces, so char is positioned
            # in the right slot of the line
            delta = int(ox / slot) - len(text)
            if delta > 1 and ox <= old_x1 + slot * 2:
                delta = 1
            if ox > old_x1 and delta >= 1:
                text += " " * delta
            # now append char
            text += char
            old_x1 = x1  # new end coordinate
            old_ox = ox  # new origin
        return text.rstrip()

    # extract page text by single characters ("rawdict")
    rows, chars, rowheight, left, right = process_blocks(page, flags, clip)
    if rows == set():
        if not skip_empty:
            textout.write(eop)  # write formfeed
        return
    # compute list of line coordinates - ignoring small (GRID) differences
    rows = curate_rows(rows, GRID)

    # sort all chars by x-coordinates, so every line will receive
    # them sorted.
    chars.sort(key=lambda c: c[1])

    # populate the lines with their char tuples
    lines, keys = make_lines(chars)

    slot, lineslots = compute_slots(keys, lines, right, left)

    # compute line advance in text output
    rowheight = rowheight * (rows[-1] - rows[0]) / (rowheight * len(rows)) * 1.5
    rowpos = rows[0]  # first line positioned here
    textout.write(b"\n")
    for k in keys:  # walk through the lines
        while rowpos < k:  # honor distance between lines
            textout.write(b"\n")
            rowpos += rowheight
        text = make_textline(left, slot, lineslots[k], lines[k])
        textout.write((text + "\n").encode("utf8", errors="surrogatepass"))
        rowpos = k + rowheight

    textout.write(eop)  # write end-of-page


def gettext(args):
    doc = open_file(args.input, args.password, pdf=False)
    pagel = get_list(args.pages, doc.page_count + 1)
    output = args.output
    if output == None:
        filename, _ = os.path.splitext(doc.name)
        output = filename + ".txt"
    textout = open(output, "wb")
    flags = TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE
    if args.convert_white:
        flags ^= TEXT_PRESERVE_WHITESPACE
    if args.noligatures:
        flags ^= TEXT_PRESERVE_LIGATURES
    if args.extra_spaces:
        flags ^= TEXT_INHIBIT_SPACES
    func = {
        "simple": page_simple,
        "blocks": page_blocksort,
        "layout": page_layout,
    }
    for pno in pagel:
        page = doc[pno - 1]
        func[args.mode](
            page,
            textout,
            args.grid,
            args.fontsize,
            args.noformfeed,
            args.skip_empty,
            flags=flags,
        )

    textout.close()
