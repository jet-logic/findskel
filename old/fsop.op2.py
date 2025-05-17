class RenameOp:
	m_subs = [];
	m_enumMethod = 0;
	def parseSubs(self, *ss):
		import re;
		for s in ss:
			a = s[1:].split(s[0], 3);
			if len(a) < 2:
				raise RuntimeError("Invalid subtitue pattern `%s'" % s);
			s = 0;
			if len(a) > 2:
				for x in a[2]:
					s |= getattr(re, x.upper());
			self.m_subs.append((re.compile(a[0], s), a[1]));
	def on_file_found(self, ctx, f):
		name2 = None;
		name = f.name;
		if self.m_enumMethod:
			for x in self.m_subs:
				name2 = x[0].sub(x[1], name);
				if name != name2:
					break;
		else:
			name2 = name;
			for x in self.m_subs:
				x = x[0].sub(x[1], name2);
				name2 = x;
		if name2 and (name != name2):
			x = None;
			try:
				x = self.ren(f, name2);
			finally:
				if x is False:
					self.m_x += 1;
					say2("REN: %r exist!" % (name2, ));
				else:
					self.m_n += 1;
					say2("REN: %r -> %r" % (name, name2), self.clue);
	def on_file_start(self, ctx):
		self.m_n = 0;
		self.m_x = 0;
		from os.path import join, exists;
		from os import rename;
		if ctx.dryRun is not False:
			rename = lambda a,b : False;
			self.clue = '?';
		else:
			self.clue = '!';
		def ren(f,name2):
			x = join(f.parent, name2);
			if exists(x):
				return False;
			if rename(f.path, x) is not False:
				f.reset(x);
			return x;
		self.ren = ren;

	def on_file_end(self, ctx):
		say2("REN:", "%d renamed;" % self.m_n, self.m_x and ("%d exists;" % self.m_x) or "");

##inconce <binSizeRep2.py>
class StatOp:
	def on_file_found(self, ctx, p):
		if p.isdir:
			if p.rel:
				self.cDirectories += 1;
		else:
			self.nSize += p.st_size;
			self.cFiles += 1;
			if 0 == p.st_size:
				self.cEmptyFiles += 1;
			elif p.st_size > 0:
				if p.st_size > self.sizeLargest:
					self.sizeLargest = p.st_size;
					self.sizeLargestN = 1;
				elif p.st_size == self.sizeLargest:
					self.sizeLargestN += 1;
				if (self.sizeSmallest is None) or (p.st_size < self.sizeSmallest):
					self.sizeSmallest = p.st_size;
					self.sizeSmallestN = 1;
				elif (p.st_size == self.sizeSmallest):
					self.sizeSmallestN += 1;
			if self.mTimeNewest == None:
				self.mTimeNewest = p.st_mtime;
			elif p.st_mtime > self.mTimeNewest:
				self.mTimeNewest = p.st_mtime;
			elif self.mTimeOldest == None:
				self.mTimeOldest = p.st_mtime;
			elif p.st_mtime < self.mTimeOldest:
				self.mTimeOldest = p.st_mtime;
		return True;
	def on_file_start(self, ctx):
		self.sizeLargest = 0;
		self.sizeLargestN = None;
		self.sizeSmallest = None;
		self.sizeSmallestN = None;
		self.cFiles = 0;
		self.cDirectories = 0;
		self.cEmptyFiles = 0;
		self.nSize = 0;
		self.mTimeNewest = None;
		self.mTimeOldest = None;
	def on_file_end(self, ctx):
		say2("Contains:", self.cFiles, 'files', self.cDirectories, 'directories');
		say2("Size:", binSizeRep2(self.nSize));
		x = {};
		if self.cEmptyFiles: x[0] = self.cEmptyFiles;
		if self.sizeSmallest: x[self.sizeSmallest] = self.sizeSmallestN;
		if self.sizeLargest: x[self.sizeLargest] = self.sizeLargestN;
		for _ in x:
			say2("Size Range:", ' .. '.join(('%s [%d]' % (binSizeRep2(k), x[k]) for k in sorted(x.keys()))));
			break;
		self.cFiles and say2("Size Average:", binSizeRep2(self.nSize/self.cFiles));
		x = [];
		(self.mTimeNewest is None) or x.append(self.mTimeNewest);
		(self.mTimeOldest is None) or x.append(self.mTimeOldest);
		if len(x) > 0:
			from datetime import datetime;
			(len(x) > 1) and (x[-1] == x[0]) and x.pop();
			x = sorted(x);
			for i, v in enumerate(x):
				x[i] = datetime.fromtimestamp(v).isoformat();
			say2("Time Range:", ' .. '.join(x));
