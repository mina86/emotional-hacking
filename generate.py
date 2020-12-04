## generate.py  -- Generates Emotional Hacking comic with various layouts.
## Copyright (C) 2016-2020  Michal Nazarewicz <mina86@mina86.com>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Generates Emotional Hacking comic with various layouts.

usage: generate.py <original-image.png> <output-directory>

Reads the original Emotional Hacking comic to extract individual panels and
generates <w>x<h>.png file in the output directory with alternative layouts for
the comic.
"""
import os
import os.path
import sys
import tempfile
import typing

import PIL.Image  # type: ignore
import PIL.ImageOps  # type: ignore


def log(msg, *args):
        if args:
                msg = msg.format(*args)
        sys.stderr.write(msg + '\n')


_Pair = typing.Tuple[int, int]
_Pairs = typing.Sequence[_Pair]
_Image = typing.Any  # Should be PIL.Image.Image but PIL has no type stubs
_Panels = typing.Sequence[_Image]


def identify_panels(img: _Image) -> _Pairs:
        """Identify panels in the image and return their bounding rows.

        Identifies where each panel starts and ends in the image.  This is done
        by looking into white-space separating each panel in the original image.

        Args:
            img: PIL Image with the original comic image.

        Returns:
            A tuple of (upper, lower) pairs indicating bounding rows of each
            panel in the image.  Note that last panel includes signature and is
            higher than any other panel.
        """
        _, lines = img.getprojection()
        panels = []
        start = None
        for y, line in enumerate(lines):
                if start is None:
                        if line:
                                start = y
                elif not line:
                        panels.append((start, y))
                        start = None
        if start is not None:
                panels.append((start, img.height))
                start = None
        return tuple(panels)


def extract_panels(path: str) -> _Panels:
        """Loads Emotional Hacking comic and splits it into individual panels.

        Args:
            path: Path to the Emotional Hacking comic strip image.

        Returns:
            A tuple of PIL Image objects holding individual panels.  Note that
            the last image includes the signature and is higher than any other
            panel.
        """
        img = PIL.Image.open(path)
        inv = PIL.ImageOps.invert(img)
        left, _, right, _ = inv.getbbox()
        panel_ys = identify_panels(inv)
        return tuple(img.crop((left, upper, right, lower))
                     for upper, lower in panel_ys)


def construct(cols: int, rows: int, panels: _Panels,
              padding: int = 5) -> PIL.Image:
        """Construct Emotional Hacking comic with given layout.

        Args:
            cols: Number of columns in the generated image.
            rows: Number of rows in the generated image.
            panels: PIL Image images for each panel.
            padding: Padding used between each panel and panel and edge of the
                image.

        Returns:
            A PIL Image with Emotional Hacking comic using specified layout.
        """
        panel_width = panels[0].width
        panel_height = max(p.height for p in panels[0:-1])
        sig_height = panels[-1].height - panel_height

        width = cols * (panel_width + padding) + padding
        height = (rows * (panel_height + padding) + padding +
                  sig_height + padding)

        img = PIL.Image.new('RGB', (width, height), color=(255, 255, 255))
        for c in range(cols):
                for r in range(rows):
                        panel = panels[r * cols + c]
                        x = padding + c * (panel_width + padding)
                        y = padding + r * (panel_height + padding)
                        if  panel.height < panel_height:
                                y += (panel_height - panel.height) // 2
                        img.paste(panel, (x, y))
        return img


def save_image(img: _Image, out_dir: str, filename: str) -> None:
        """Saves given image as a PNG image in specified location.

        If destination file already exists it is overwritten.

        Args:
            img: PIL Image to save.
            out_dir: Directory to save the image in.
            filename: File name of the destination.
        """
        out_path = os.path.join(out_dir, filename)
        fd, tmp = tempfile.mkstemp(dir=out_dir)
        try:
                with os.fdopen(fd, 'wb') as wr:
                        img.save(wr, format='PNG', optimize=True)
                        umask = os.umask(0o777)
                        os.umask(umask)
                        os.fchmod(wr.fileno(), 0o644 % ~umask)
                os.rename(tmp, out_path)
                log('Saved {}', out_path)
        except:
                os.unlink(tmp)
                raise


def main(argv: typing.Sequence[str]) -> typing.Union[str, int]:
        """Main function.

        Args:
            argv: Command line arguments.

        Returns:
            Exit code or error message.
        """
        if len(argv) != 3:
                return 'usage: {} <input.png> <output-dir>'.format(argv[0])

        in_file = argv[1]
        out_dir = argv[2]

        if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
        log('Extracting panels...')
        panels = extract_panels(in_file)
        panel_width = panels[0].width
        panel_height = max(p.height for p in panels[:-1])
        log('{} panels found [{}x{}]', len(panels), panel_width, panel_height)

        constructed = False
        for cols in range(2, len(panels)):
                if len(panels) % cols:
                        continue
                rows = len(panels) // cols
                log('Constructing {}x{} image...', cols, rows)
                save_image(construct(cols, rows, panels),
                           out_dir, '{}x{}.png'.format(cols, rows))
                constructed = True

        if not constructed:
                return 'No images generated'

        return 0


if __name__ == '__main__':
        sys.exit(main(sys.argv))
