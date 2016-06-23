#!/bin/sh

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
	convert -background white \
	        "$img" -extent "${img_w}x$((sig_y + sig_h))" \
	        "$sig" -geometry "+$sig_x+$sig_y" -composite \
	        "$tmp"
)

[ -z "$zopflipng" ] || (
	set -x
	"$zopflipng" -y "$tmp" "$out"
)
