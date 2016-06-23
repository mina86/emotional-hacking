#!/bin/sh

## Determines smallest image sizes no smaller than all images.
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

out=$1
shift

identify -format '%w %h\n' -- "$@" | (
	width=0
	height=0
	while read w h; do
		if [ -n "$w" ] && [ "$w" -gt "$width" ]; then
			width=$w
		fi
		if [ -n "$w" ] && [ "$h" -gt "$height" ]; then
			height=$h
		fi
	done

	test "$width" -gt 0
	test "$height" -gt 0
	geometry=$(printf '%dx%d\n' "$width" "$height")
	echo "$geometry" >"$out"
	echo "$geometry"
)
