from os.path import join, splitext, exists, basename, normcase;
import os
from __main__ import getCounter, say2
TOT = getCounter('Unique')
TO2 = getCounter('UniqueName')
TO3 = getCounter('UniqueTime')
umap = {}
imap = {}
smap = {}
def on_file_found(ctx, f):
	i = f.st_ino
	if f.isdir:
		return
	TOT.All += 1
	if i in imap:
		return
	else:
		imap[i] = True
	smap.setdefault(f.size, []).append(f.path)
	#~ k = "%d:%d:%s" % (f.size, f.st_ctime, f.name)
	#~ x = umap.setdefault(k, [])
	#~ x.append(f.path)

def on_file_end(ctx):
	#~ for k in umap:
		#~ v = umap[k];
		#~ if len(v) >1 :
			#~ say2('Multi', repr(v))
			#~ TOT.Multi += 1
		#~ else:
			#~ TOT.Unique += 1
	while len(smap) > 0:
		(size, files) = smap.popitem();
		if len(files) < 2:
			TOT.DistinctSize += 1
			continue
		TOT.SameSize += 1
		# filter: name, st_ctime
		nmap = {}
		for f in files:
			nmap.setdefault(normcase(basename(f)), []).append(f)
		while len(nmap) > 0:
			(name, files2) = nmap.popitem();
			if len(files2) < 2:
				TO2.Distinct += 1
				continue
			TO2.Same += 1
			cmap = {}
			for f in files2:
				cmap.setdefault(long(os.stat(f).st_ctime), []).append(f)
			while len(cmap) > 0:
				(ctime, files3) = cmap.popitem();
				if len(files3) < 2:
					TO3.Distinct += 1
					continue
				TO3.Same += 1

"""
size+name+ctime

fsaux -p I:\wrx\python\fsaux\op\Unique.py F:\arc\sub
"""
