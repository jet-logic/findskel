def getFileID(*args):
	global getFileID
	import os;
	if os.name == 'nt':
		from ctypes import windll, c_uint32, c_wchar_p, c_void_p, WinError, create_string_buffer, byref;
		from struct import unpack;
		(GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, INVALID_HANDLE_VALUE) = (c_uint32(0x80000000), c_uint32(0x00000001), c_uint32(3), 0x00000080, c_void_p(-1));
		FILE_FLAG_BACKUP_SEMANTICS   = 0x02000000
		CreateFileW = windll.kernel32.CreateFileW;
		GetFileInformationByHandle = windll.kernel32.GetFileInformationByHandle;
		CloseHandle = windll.kernel32.CloseHandle;
		def devIno(file, flag = None):
			FileName = c_wchar_p(file);
			FileHandle = CreateFileW(FileName, GENERIC_READ, FILE_SHARE_READ, None, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS+FILE_ATTRIBUTE_NORMAL, None);
			if FileHandle == -1:
				raise WinError();
			try:
				buf = create_string_buffer(52);
				if GetFileInformationByHandle(FileHandle, byref(buf)):
					(v, h, l) = unpack("<28xL12xLL", buf.raw);
				else:
					raise WinError();
			finally:
				if not CloseHandle(FileHandle):
					raise WinError();
			return (v, (h << 32) | l)
	else:
		from os import stat;
		def devIno(target, flag = None):
			st = stat(target);
			return (st.st_dev, st.st_ino)
	def O(target, flag = 0):
		if flag in (0, 2):
			x = devIno(target);
			return "%x.%x" % (x[0], x[1])
		elif flag == 1:
			x = devIno(target);
			return "%x" % (x[1],)
		elif flag > 2:
			x = devIno(target);
			(head, tail) = os.path.split(os.path.realpath(target))
			if head and tail:
				y = devIno(head);
				if y and y[0] == x[0] and os.path.isdir(head):
					return "%x.%x.%x" % (x[0], y[1], x[1])
			return "%x.%x" % (x[0], x[1])
	getFileID = O;
	return getFileID(*args);

def on_file_found(ctx, f):
	if f.isdir:
		return
	id = getFileID(f.path);
	ctx.h_cFiles += 1;
	ctx.h_mapFileIdPaths.setdefault(id, []).append(f.path);

def on_file_init(ctx):
	ctx.h_mapFileIdPaths = {};
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
		ctx.h_dirLimit = int(opt.string);
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
	mapNamePaths = {}; # map< basename, list<path> >
	mapName = ctx.h_dbNames; # map< hash, basename >
	h_mapFileIdPaths = ctx.h_mapFileIdPaths;  # map< hash, list<path> >
	dryRun = ctx.dryRun is not False;
	dirMask = ctx.h_dirMask;
	dirLimit = ctx.h_dirLimit;
	what = ctx.h_extWhat;
	for hash in h_mapFileIdPaths:
		paths = h_mapFileIdPaths[hash];  # list<path>
		name = mapName.get(hash, None);
		if name:
			nNamed += 1;
		else:
			name = basename(paths[0]);
		if what: # fix: extension / type
			f = what(paths[0]).lower();
			if f:
				f = '.' + f;
				if splitext(name)[1].lower() != f:
					name = name + f;
		nkey = name.lower();
		if nkey in mapNamePaths:
			(i, f) = (0, splitext(name));
			while (nkey in mapNamePaths) and (i < 9999):
				i += 1;
				name = f[0] + ("-%d" % i) + f[1];
				nkey = name.lower();
			if nkey in mapNamePaths:
				raise RuntimeError("Can't generate unique name: %r" % name);
			nSame += 1;
		if len(paths) > 1:
			nDup += 1;
		mapNamePaths[nkey] = (name, paths);
	(o, f) = (ctx.h_dirMaskN, 0);
	nFiles = len(mapNamePaths);
	while len(mapNamePaths) > 0:
		(_, (name, paths)) = mapNamePaths.popitem();
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
	mapNamePaths = [("Found %d" % ctx.h_cFiles, True)];
	mapNamePaths.append(("Files %d" % nFiles, True));
	mapNamePaths.append(("Duplicates %d" % nDup, nDup > 0));
	mapNamePaths.append(("Renames %d" % nSame, nSame > 0));
	mapNamePaths.append(("Removed %d" % nRm, nRm > 0));
	mapNamePaths.append(("Named %d/%d" % (nNamed, len(mapName)), len(mapName) > 0));
	out(", ".join(x[0] for x in mapNamePaths if x[1]));
