##inconce <say2.py>
##inconce <binSizeRep2.py>
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
		pass;
	else:
		s1 = sha1OfFile(path).hexdigest();
		ctx.h_cFiles += 1;
		ctx.h_dbHash.setdefault(s1, []).append(path);
	return True;

def on_file_init(ctx):
	ctx.h_dbHash = {};
	ctx.h_cFiles = 0;
	ctx.h_dirMask = "res%02d";
	ctx.h_dirMaskN = 0;
	ctx.h_dirLimit = 100;
	ctx.h_dbNames = {};
	ctx.h_extWhat = None;

def on_file_args(ctx, opt):
	if opt.is_string('dir'):
		from os.path import abspath;
		ctx.h_dirRoot = abspath(opt.string);
	elif opt.is_string('mask'):
		ctx.h_dirMask = opt.string;
	elif opt.is_string('start'):
		ctx.h_dirMaskN = int(opt.string);
	elif opt.is_string('limit'):
		#~ print "dirLimit: %s -> %s" % (ctx.h_dirLimit, opt.string);
		ctx.h_dirLimit = int(opt.string);
	elif opt.is_string('hns'):
		inp = opt.string;
		if inp == '-':
			from sys import stdin;
			inp = stdin;
		else:
			inp = open(inp);
		l = inp.readline();
		while l:
			l = l.strip().split();
			if l and len(l) > 1:
				#~ print "HN: %s %r" % (l[0], l[1]);
				ctx.h_dbNames[l[0]] = l[1];
			l = inp.readline();
		inp.close();
	elif opt.is_bool('extype'):
		import imghdr;
		ctx.h_extWhat = opt.bool and imghdr.what or None;
		
def out(*s):
	o = None;
	for x in s:
		if o is None:
			from sys import stdout;
			o = stdout.write;
		else:
			o(' ');
		o(str(x));
	if o:
		o('\n');
	else:
		from sys import stdout;
		stdout.write('\n');

def on_file_end(ctx):
	from os.path import basename, join, splitext, isdir, dirname, exists;
	from os import renames, remove, makedirs, removedirs, access, R_OK, W_OK;
	from shutil import move;
	(nFiles, nSame, nDup, nRm, nNamed) = (0, 0, 0, 0, 0);
	def rm_parent_dirs(x):
		try:
			removedirs(dirname(x));
		except:
			pass;
	dbName = {}; # map< basename, list<path> >
	mapName = ctx.h_dbNames; # map< hash, basename >
	h_dbHash = ctx.h_dbHash;  # map< hash, list<path> >
	dryRun = ctx.dryRun is not False;
	dirMask = ctx.h_dirMask;
	dirLimit = ctx.h_dirLimit;
	what = ctx.h_extWhat;
	for hash in h_dbHash:
		paths = h_dbHash[hash];  # list<path>
		name = mapName.get(hash, None);
		if name:
			nNamed += 1;
		else:
			name = basename(paths[0]);
		if what:
			f = what(paths[0]).lower();
			if f:
				f = '.' + f;
				if splitext(name)[1].lower() != f:
					name = name + f;
		nkey = name.lower();
		if nkey in dbName:
			(i, f) = (0, splitext(name));
			while (nkey in dbName) and (i < 9999):
				i += 1;
				name = f[0] + ("-%d" % i) + f[1];
				nkey = name.lower();
			if nkey in dbName:
				raise RuntimeError("Can't generate unique name: %r" % name);
			nSame += 1;
		if len(paths) > 1:
			nDup += 1;
		dbName[nkey] = (name, paths);
	(o, f) = (ctx.h_dirMaskN, 0);
	nFiles = len(dbName);
	while len(dbName) > 0:
		(_, (name, paths)) = dbName.popitem();
		x = join(ctx.h_dirRoot, dirMask % ((f//dirLimit) + o));
		isdir(x) or dryRun or makedirs(x);
		target = join(x, name);
		for i, path  in enumerate(paths):
			if i > 0: # NOTE: removed duplicates
				out("RM: %r" % (path));
				if dryRun:
					if not access(path, W_OK):
						out("No Write access: %r" % path);
				else:
					try:
						remove(path);
					except:
						out("Error: Failed to remove %r" % (path));
				nRm += 1;
			else:
				out("MV: %r <- %r" % (target, path));
				if exists(target):
					raise RuntimeError("Exists : %r" % target);
				elif dryRun:
					if not access(path, W_OK):
						raise RuntimeError("No Write access: %r" % path);
				else:
					move(path, target);
			dryRun or rm_parent_dirs(path);
		f += 1;
	dbName = [("Found %d" % ctx.h_cFiles, True)];
	dbName.append(("Files %d" % nFiles, True));
	dbName.append(("Duplicates %d" % nDup, nDup > 0));
	dbName.append(("Renames %d" % nSame, nSame > 0));
	dbName.append(("Removed %d" % nRm, nRm > 0));
	dbName.append(("Named %d/%d" % (nNamed, len(mapName)), len(mapName) > 0));
	out(", ".join(x[0] for x in dbName if x[1]));
