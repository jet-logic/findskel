class MultiRenameOp:
	fMask = "FILE%04d";
	nIndex = None;
	def on_file_found(self, ctx, st, path, base, name):
		from os.path import join;
		from os import rename;
		name2 = self.fMask % self.nIndex;
		if name2 and (name != name2):
			dryRun = (ctx.dryRun is not False);
			say2("MREN: %r %s %r'" % (name, dryRun and "~~" or "->", name2));
			dryRun or rename(path, join(base, name2));
			self.nIndex += 1;
			self.cRenamed += 1;
	def on_file_start(self, ctx):
		self.cRenamed = 0;
		if self.nIndex is None: self.nIndex = 0;
	def on_file_end(self, ctx):
		say2("MREN:", self.cRenamed, "renamed");
	def on_file_args(self, ctx, opt):
		if opt.is_string('mask'):
			self.fMask = opt.string;
		elif opt.is_integer('idx'):
			self.nIndex = opt.integer;
