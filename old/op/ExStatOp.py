class ExStatOp:
	def on_file_found(self, ctx, st, path, _, name):
		from stat import S_ISDIR;
		if not S_ISDIR(st.st_mode):
			from os.path import splitext;
			(_, ext) = splitext(name);
			ext = ext.lower();
			self.extMap[ext] = self.extMap.get(ext, 0) + 1;
		return True;
	def on_file_start(self, ctx):
		self.extMap = {};
	def on_file_end(self, ctx):
		x = self.extMap;
		#~ for k in x:
			#~ say2('%7d' % x[k], ":", k);
		#~ for k in sorted(x.keys()):
			#~ say2('%7d' % x[k], ":", k);
		for k in sorted(zip(x.values(), x.keys())):
			say2('%7d' % k[0], ":", k[1]);
