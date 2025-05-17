class DeleteOp:
	def on_file_found(self, ctx, st, path, base, name):
		from stat import S_ISDIR;
		from os import rmdir, remove;
		dryRun = (ctx.dryRun is not False);
		if S_ISDIR(st.st_mode):
			try:
				dryRun or rmdir(path);
				self.nDir += 1;
			finally:
				say2("DEL: Dir %r" % path, dryRun and "?" or "!");
		else:
			try:
				dryRun or remove(path);
				self.nFile += 1;
			finally:
				say2("DEL: File %r" % path, dryRun and "?" or "!");
	def on_file_start(self, ctx):
		self.nFile = 0;
		self.nDir = 0;
	def on_file_end(self, ctx):
		say2("DEL: %d Removed;" % (self.nFile+self.nDir), (self.nFile > 0) and (str(self.nFile) + " files;") or "", (self.nDir > 0) and (str(self.nDir) + " dirs;") or "");
