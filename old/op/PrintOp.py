class PrintOp:
	bLeafOnly = None;
	bCygWin = None;
	bMingW = None;
	bURI = None;
	relTo = None;
	@staticmethod
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
	@staticmethod
	def abs2rel(path, base):
		from os.path import normcase, abspath, join, pardir;
		path = abspath(path);
		base = abspath(base);
		pathchunks = PrintOp.split_component(path);
		basechunks = PrintOp.split_component(base);
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
	def on_file_found(self, ctx, st, path, base, name):
		if self.relTo:
			path = PrintOp.abs2rel(path, self.relTo);
		if self.bLeafOnly:
			path = name;
		elif self.bCygWin:
			path = self.bCygWin.sub(r'/cygdrive/\1', path);
			path = path.replace('\\', '/');
		elif self.bMingW:
			path = self.bMingW.sub(r'/\1', path);
			path = path.replace('\\', '/');
		if self.bURI:
			path = self.bURI(path);
			if path[0] == '/':
				path = 'file:' + path
		try:
			#~ print (path);
			say1(path);
		except UnicodeEncodeError:
			#~ print (path.encode('utf-8'))
			say1(path.encode('utf-8'));
	def on_file_start(self, ctx):
		if self.bCygWin is True:
			import re;
			self.bCygWin = re.compile(r'^([A-Za-z]):');
		elif self.bMingW is True:
			import re;
			self.bMingW = re.compile(r'^([A-Za-z]):');
		elif self.bURI:
			try:
				urllib = __import__('urllib');
				self.bURI = getattr(urllib, 'pathname2url');
			except:
				from urllib.request import pathname2url;
				self.bURI = pathname2url;
# TODO: fullpath
# TODO: quote path
# TODO: separator
