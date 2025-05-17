class HardLinkClone:
	def link(self, src, dst):
		import subprocess;
		say2("Info: LN `%s' -> `%s'" % (src, dst));
		subprocess.call(['ln', src, dst]);
	def clonetree(self, src, dst):
		if not os.path.isdir(dst):
			os.makedirs(dst);
		for name in os.listdir(src):
			srcname = os.path.join(src, name)
			dstname = os.path.join(dst, name)
			if os.path.isdir(srcname):
				self.clonetree(srcname, dstname);
			else:
				self.link(srcname, dstname);
	def on_file_found(self, ctx, st, path, base, name):
		def abs2rel(path, base):
			path = os.path.abspath(path);
			base = os.path.abspath(base);
			pathchunks = split_component(path);
			basechunks = split_component(base);
			level = 0;
			while ((len(pathchunks) > 0) and (len(basechunks) > 0)  and
				os.path.normcase(pathchunks[0]) == os.path.normcase(basechunks[0])):
				pathchunks.pop(0);
				basechunks.pop(0);
				level += 1;
			if level > 0:
				if len(pathchunks) > 0 or len(basechunks) > 0:
					path = '';
					for x in basechunks: path = os.path.join(path, os.path.pardir);
					for x in pathchunks: path = os.path.join(path, x);
				else:
					path = '.';
			return path;
		rel = abs2rel(path, base);
		src = path;
		dst = os.path.join(self.ctx.hlclone, rel);
		if stat.S_ISDIR(st.st_mode):
			self.clonetree(src, dst);
		else:
			self.link(src, dst);
		#say2 "HLCLone: `%s'" % os.path.relpath(path, base);
	def on_file_end(self, ctx):
		# say2 "Info: HLCLone `%s'" % self.ctx.hlclone;
		pass;
