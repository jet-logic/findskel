##inconce <say2.py>
##inconce <binSizeRep2.py>
class StatOp:
	def on_file_found(self, ctx, st, path, _, name):
		from stat import S_ISDIR;
		if S_ISDIR(st.st_mode):
			self.cDirectories += 1;
		else:
			self.nSize += st.st_size;
			self.cFiles += 1;
			if 0 == st.st_size:
				self.cEmptyFiles += 1;
			elif st.st_size > 0:
				if st.st_size > self.sizeLargest:
					self.sizeLargest = st.st_size;
					self.sizeLargestN = 1;
				elif st.st_size == self.sizeLargest:
					self.sizeLargestN += 1;
				if (self.sizeSmallest is None) or (st.st_size < self.sizeSmallest):
					self.sizeSmallest = st.st_size;
					self.sizeSmallestN = 1;
				elif (st.st_size == self.sizeSmallest):
					self.sizeSmallestN += 1;
			if self.mTimeNewest == None:
				self.mTimeNewest = st.st_mtime;
			elif st.st_mtime > self.mTimeNewest:
				self.mTimeNewest = st.st_mtime;
			elif self.mTimeOldest == None:
				self.mTimeOldest = st.st_mtime;
			elif st.st_mtime < self.mTimeOldest:
				self.mTimeOldest = st.st_mtime;
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


		
		
