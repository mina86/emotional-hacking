#!/bin/sh

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
