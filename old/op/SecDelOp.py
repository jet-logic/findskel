class SecDelOp:
	def on_file_found(self, ctx, st, path, base, name):
		from stat import S_ISDIR;
		say2("Info: File remove `%s'" % path);
		if S_ISDIR(st.st_mode):
			from os import rmdir;
			ctx.dryRun or rmdir(path);
			self.m_n += 1;
			say2("Info: Directory removed `%s'" % path);
		else:
			import random, tempfile;
			from os import urandom, fsync, rename, utime;
			from os.path import dirname, exists;
			top = dirname(path);
			try:
	#overwrite first 4kb
				n = 4096;
				if st.st_size < n:
					n = st.st_size;
				#say2 "overwrite first 4kb `%s'" % (path);
				if n > 0:
					s = urandom(n);
					f = open(path, 'w+b');
					f.write(s);
					f.flush();
					f.close();
	#truncate to zero
				#say2 "truncate to zero `%s'" % (path);
				f = open(path, 'w+b');
				f.flush();
				fsync(f.fileno());
				f.close();
				f = None;
	#rename
				#say2 "rename `%s'" % (path);
				newPath = tempfile.mktemp(dir = top) ;
				assert(not exists(newPath));
				rename(path, newPath);
	#change time stamps
				#say2 "change time stamps `%s'" % (newPath);
				utime(newPath, (random.randint(0, 2**31), random.randint(0, 2**31)))
	#delete
				#say2 "delete `%s'" % (newPath);
				remove(newPath);
				self.m_n += 1;
				#say2 "ok `%s'" % (newPath);
			#except WindowsError:
			#	say2 "WindowsError: Failed to remove `%s'" % path;
			#	raise;
			except:
				say2("Error: Failed to remove `%s'" % path);
				raise;
		return True;
	def on_file_start(self, ctx):
		self.m_n = 0;
	def on_file_end(self, ctx):
		say2("Info: %d Removed" % self.m_n);
