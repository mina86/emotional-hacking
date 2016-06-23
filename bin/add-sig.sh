#!/bin/sh

## Adds SMBC signature to mosaic image.
## Copyright 2016 by Michal Nazarewicz <mina86@mina86.com>
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

set -eu

img=$1
sig=$2
out=$3

set -- $(identify -format %w\ %h -- "$img") $(identify -format %w\ %h -- "$sig")
img_w=$1; img_h=$2; sig_w=$3; sig_h=$4

sig_x=$((img_w - sig_w - 25))
[ "$sig_x" -ge 0 ] || sig_x=0
sig_y=$((img_h - 10))

zopflipng=$(which zopflipng 2>/dev/null)

if [ -n "$zopflipng" ]; then
	tmp=$(mktemp "${TMPDIR:-/tmp}/tmp.XXXXXX.png")
	trap 'rm -- "$tmp"' 0
else
	tmp=$out
fi

(
	set -x
	convert -depth 8 -background white \
	        "$img" -extent "${img_w}x$((sig_y + sig_h))" \
	        "$sig" -geometry "+$sig_x+$sig_y" -composite \
	        "$tmp"
)

[ -z "$zopflipng" ] || (
	set -x
	"$zopflipng" -y "$tmp" "$out"
)
