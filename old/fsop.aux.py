class PathItem:
	def __init__(self, p):
		self.path = p
	def __getattr__(self, name):
		if name == 'stat':
			from os import stat
			try:
				self.__dict__[name] = stat(self.path)
			except:
				from sys import stderr
				stderr.write("Stat failed %r" % self.path)
				raise
		elif name in ('parent', 'name'):
			from os.path import split
			(self.__dict__['parent'], self.__dict__['name']) = split(self.path)
		elif 'mtime' == name:
			self.__dict__[name] = int(self.stat.st_mtime)
		elif 'size' == name:
			self.__dict__[name] = self.stat.st_size
		elif 'isdir' == name:
			from stat import S_ISDIR
			self.__dict__[name] = bool(S_ISDIR(self.stat.st_mode))
		elif 'islink' == name:
			from stat import S_ISLNK
			self.__dict__[name] = bool(S_ISLNK(self.stat.st_mode))
		elif hasattr(self.stat, name):
			if name in ('st_ino', 'st_dev', 'st_nlink'):
				if self.stat.st_ino == 0 and os.name == 'nt':
					(self.st_dev, self.st_ino, self.st_nlink) = ntHardLinkInfo(self.path)
					return self.__dict__[name]
			self.__dict__[name] = getattr(self.stat, name)
		elif 'walk' == name:
			self.__dict__[name] = None
		elif 'depth' == name:
			self.__dict__[name] = 0
		elif 'rel' == name:
			self.__dict__[name] = ''
		try:
			return self.__dict__[name]
		except KeyError:
			raise AttributeError(name)
	def __contains__(self, name):
		return (name in self.__dict__) or (name in ('stat', 'md5', 'parent', 'name', 'mtime', 'size', 'isdir', 'islink'))
	def reset(self, p = None):
		self.__dict__.clear()
		if p:
			self.path = p

def loadModule(ctx, value):
	from imp import find_module, load_module
	from os.path import splitext, basename, isfile, dirname
	(mo, parent, title) = (None, dirname(value), basename(value))
	if isfile(value):
		(title, _) = splitext(title)
	if parent:
		mo = find_module(title, [parent])
	else:
		mo = find_module(title)
	if mo:
		mo = load_module(title, *mo)
	return mo

def insert_level_filter(ctx, w):
	ctx._l = 0
	if ctx.maxLevel:
		def l_inc(c, _):
			if c._l >= c.maxLevel:
				return True
			c._l += 1
		w.cbEnter.append(l_inc)
	else:
		def l_inc(c, _): c._l += 1
		w.cbEnter.append(l_inc)
	if ctx.minLevel:
		def l_min(c, _):
			if c._l < c.minLevel:
				return True
		w.cbItem.insert(0, l_min)
	def l_dec(c, _): c._l -= 1
	w.cbLeave.append(l_dec)
	#~ w.cbItem.append((lambda _, p: sys.stdout.write(str(ctx._l))))

def insert_type_filter(ctx, w, x):
	import stat
	_t = []
	for _ in (('d', stat.S_ISDIR), ('c', stat.S_ISCHR), ('b', stat.S_ISBLK), ('f', stat.S_ISREG), ('p', stat.S_ISFIFO), ('l', stat.S_ISLNK), ('s', stat.S_ISSOCK)):
		(_[0] in x) and _t.append(_[1])
	def f_type(_, p):
		p = p.st_mode
		for _ in _t:
			if _(p): return
		return True
	w.insert(0, f_type)

def parseBinSize(x):
	from re import match
	m = match(r'^(\d+(?:\.\d+)?)\s*([kKmMgG](?:ib|b)?|b?)$', x)
	if m:
		x = m.group(2).lower()
		b = ('i' in x)
		return int(float(m.group(1)) * (
			(('k' in x) and (b and 0x400 or 1000)) or
			(('m' in x) and (b and 0x100000 or 1000000)) or
			(('g' in x) and (b and 0x40000000 or 1000000000)) or
			1))
	raise ValueError(x)
