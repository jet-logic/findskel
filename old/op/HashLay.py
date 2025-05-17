def sha1OfFile(fname, chunksize = 131072):
	try:
		from hashlib import sha1;
		m = sha1();
	except ImportError:
		import sha;
		m = sha.new();
	f = open(fname, "rb");
	while 1:
		blck = f.read(chunksize);
		if not blck:
			break;
		m.update(blck);
	f.close();
	return m;

def on_file_found(ctx, st, path, _, name):
	from stat import S_ISDIR;
	if S_ISDIR(st.st_mode):
		ctx.hl_dir.append(path);
	return True;

def on_file_init(ctx):
	ctx.hl_dir = [];

def on_file_args(ctx, opt):
	if opt.is_string('dir'):
		from os.path import abspath;
		ctx.h_dirRoot = abspath(opt.string);
	elif opt.is_string('mask'):
		ctx.h_dirMask = opt.string;
	elif opt.is_string('start'):
		ctx.h_dirMaskN = int(opt.string);

def split_component(file):
	from os.path import split;
	leaf = [];
	while 1:
		x = split(file);
		if x[1]:
			leaf.append(x[1]);
			file = x[0];
		else:
			x[0] and leaf.append(x[0]);
			break;
	leaf.reverse();
	return leaf;

def abs2rel(path, base):
	from os.path import normcase, abspath, join, pardir;
	path = abspath(path);
	base = abspath(base);
	pathchunks = split_component(path);
	basechunks = split_component(base);
	level = 0;
	while ((len(pathchunks) > 0) and (len(basechunks) > 0)  and
		normcase(pathchunks[0]) == normcase(basechunks[0])):
		pathchunks.pop(0);
		basechunks.pop(0);
		level += 1;
	if level > 0:
		if len(pathchunks) > 0 or len(basechunks) > 0:
			path = '';
			for x in basechunks: path = join(path, pardir);
			for x in pathchunks: path = join(path, x);
		else:
			path = '.';
	return path;

def on_file_end(ctx):
	from os.path import basename, join, splitext, isdir, dirname, exists, normcase;
	from os import renames, remove, makedirs, removedirs, access, R_OK, W_OK;
	from shutil import move;
	import os
	d = ctx.hl_dir[0];
	for root, dirs, files in os.walk(d):
		for name in files:
			f = join(root, name);
			r = abs2rel(f, d)
			k = normcase(r);
			print(k, r, f);
			# db[k] = (r, h);




