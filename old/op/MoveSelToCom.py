import os, subprocess, re, tempfile
from __main__ import getCounter, say2

def on_file_found(ctx, f):
	if f.isdir:
		return
	com = subprocess.check_output(["exiftool", "-b", "-Comment", f.path], shell=True).strip()
	if com and re.search(r"\[sel\(", com):
		return
	output = subprocess.check_output(["exiftool", "-IPTC:FixtureIdentifier", f.path], shell=True).strip()
	if output:
		m = re.search(r"(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)", output)
		if m:
			x = int(m.group(1))
			y = int(m.group(2))
			w = int(m.group(3)) - x
			h = int(m.group(4)) - y
			p = ["","l","r"][int(m.group(5))] + ["","t","b"][int(m.group(6))]
			assert w>0 and h>0
			m = r"[sel(%d,%d,%d,%d,%s)]" % (x, y, w, h, p)
			if com:
				m = com + m
			m = ["exiftool", "-overwrite_original_in_place" ,  "-ignoreMinorErrors", r'-comment='+m, f.path]
			if ctx.dryRun is False:
				subprocess.check_call(m, shell=True)
			else:
				say2(m)
				
			


"""
[[123,24][142x234][]]
exiftool -IPTC:FixtureIdentifier  M:\b
fsaux -p I:\wrx\python\fsaux\op\MoveSelToCom.py
fsaux -p I:\wrx\python\fsaux\op\MoveSelToCom.py M:\col --include "i00*.*g*"
"""
