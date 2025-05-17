
params = {'htmRE' : [], 'rmRE' : [], 'bye' : None};

def on_file_args(ctx, opt):
	if opt.is_bool('bye'):
		params['bye'] = opt.bool;

def on_file_start(ctx):
	if len(params['htmRE']) < 1:
		from re import compile;
		params['htmRE'].append(compile(r"(.+)\.x?html?$"));
	if len(params['rmRE']) < 1:
		from re import compile;
		params['rmRE'].append(compile(r".*\.(?:js(on)?|php|x?html?|as[xp].?|loaded_\d+)$"));
		params['rmRE'].append(compile(r"^[^\.]+$"));

def on_file_found(ctx, st, path, base, name):
	from stat import S_ISDIR;
	from os.path import isdir, join;
	dirFiles = None;
	if not S_ISDIR(st.st_mode):
		for r in params['htmRE']:
			m = r.match(name);
			if m:
				m = join(base, m.group(1) + '_files');
				if isdir(m):
					dirFiles = m;
					break;
	if dirFiles:
		from os import listdir, rmdir, remove;
		from shutil import rmtree;
		dryRun = ctx.dryRun is not False;
		print(repr(dirFiles));
		for name in listdir(dirFiles):
			path = join(dirFiles, name);
			bye = None;
			if isdir(path):
				bye = rmtree;
			else:
				for r in params['rmRE']:
					if r.match(name):
						bye = remove;
						break;
			if bye:
				print ('\t%s %s%s' % (bye == remove and 'F' or 'D', repr(name), dryRun and "?" or "!"));
				dryRun or bye(path);
		try:
			dryRun or rmdir(dirFiles);
		except OSError:
			pass;
# TODO: 1x1 pixel img
