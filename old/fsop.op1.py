def print_func(tail = None, sep = '\n', format = None):
	import sys;
	global w__;
	w__ = sys.stdout.write;
	def p0(x):
		global w__;
		try:
			w__(x);
		except UnicodeEncodeError:
			sys.stdout.flush();
			if hasattr(sys.stdout, 'buffer'):
				W__ = sys.stdout.buffer.write;
			else:
				W__ = sys.stdout.write;
			if sys.stdout.isatty( ):
				w__ = lambda x: W__(x.encode('mbcs', 'replace'));
			else:
				w__ = lambda x: W__(x.encode('utf-8'));
			w__(x);
		w__(sep);
	if format is None:
		if tail: return lambda _, p: p0(p.name);
	elif format == 'cygwin':
		import re;
		__re = re.compile(r'^([A-Za-z]):');
		def pC(_, p):
			p = __re.sub(r'/cygdrive/\1', p.path);
			p = p.replace('\\', '/');
			p0(p);
		return pC;
	elif format == 'mingw':
		import re;
		__re = re.compile(r'^([A-Za-z]):');
		def pM(_, p):
			p = __re.sub(r'/\1', p.path);
			p = p.replace('\\', '/');
			p0(p);
		return pM;
	elif format == 'uri':
		if tail:
			try:
				from urllib import quote;
			except:
				from urllib.request import quote;
			def pU1(_, p):
				p0(quote(p.name));
			return pU1;
		try:
			from urllib import pathname2url;
		except:
			from urllib.request import pathname2url;
		def pU2(_, p):
			p = pathname2url(p.path);
			p0((p[0] == '/') and ('file:' + p) or p);
		return pU2;
	else:
		raise RuntimeError("Path format not recognized %r" % format);
	return lambda _, p: p0(p.path);

class ExStatOp:
	sort = '';
	def on_file_found(self, ctx, p):
		if not p.isdir:
			p = self.getext(p.name);
			self.map[p] = self.map.get(p, 0) + 1;
	def on_file_start(self, ctx):
		self.map = {};
		if not getattr(self, 'getext', None):
			from os.path import splitext;
			self.getext = (self.sort and ('s' in self.sort)) and (lambda x: splitext(x)[1]) or (lambda x: splitext(x.lower())[1]);
	def on_file_end(self, ctx):
		s = getattr(self, 'sort', '');
		x = self.map;
		x = sorted(zip(x.keys(), x.values()), key = (('x' in s) and (lambda x: x[0]) or (lambda x: x[1])), reverse = ('a' not in s));
		if 'v' in s:
			for k in x:	say2(k[0], k[1]);
		else:
			put2("Extension:");
			for k in x:	put2(' ', str(k[0]), ' ', str(k[1]), ';');
			put2("\n");
	def on_file_args(self, ctx, opt):
		if opt.is_string('sort'): self.sort = opt.string;

class DeleteOp:
	def on_file_found(self, ctx, p):
		if p.isdir:
			try:
				self.RD(p.path);
				self.nDir += 1;
			finally:
				say2("DEL: Dir %r" % p.path, self.CH);
		else:
			try:
				self.RM(p.path);
				self.nFile += 1;
			finally:
				say2("DEL: File %r" % p.path, self.CH);
	def on_file_start(self, ctx):
		self.nFile = 0;
		self.nDir = 0;
		if ctx.dryRun is not False:
			self.RM = lambda x: None;
			self.RD = self.RM;
			self.CH = '?';
		else:
			from os import rmdir, remove, chmod;
			from stat import S_IWRITE;
			def rd(p):
				chmod(p, S_IWRITE);
				rmdir(p);
			def rm(p):
				chmod(p, S_IWRITE);
				remove(p);
			self.RM = rm;
			self.RD = rd;
			self.CH = '!';
	def on_file_end(self, ctx):
		say2("DEL: %d Removed;" % (self.nFile+self.nDir), (self.nFile > 0) and (str(self.nFile) + " files;") or "", (self.nDir > 0) and (str(self.nDir) + " dirs;") or "");
