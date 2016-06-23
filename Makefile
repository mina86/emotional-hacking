TILES	= 2x6 3x4 4x3
FRAMES	= $(wildcard src/??.png)

all: $(patsubst %,out/%.png,$(TILES))

tmp/.geometry: bin/choose-size.sh $(FRAMES)
	@mkdir -p -- $(dir $@)
	/bin/sh $< $@ $(FRAMES)

tmp/%.png: tmp/.geometry $(FRAMES)
	@mkdir -p -- $(dir $@)
	montage -depth 8 -geometry "$$(cat $<)+5+5" \
		-tile $(basename $(notdir $@)) $(FRAMES) $@

out/%.png: bin/add-sig.sh tmp/%.png src/sig.png
	@mkdir -p -- $(dir $@)
	/bin/sh $^ $@

distclean:
	rm -rf -- out tmp

clean:
	rm -rf -- out

.PHONY: distclean clean all
.SECONDARY:
