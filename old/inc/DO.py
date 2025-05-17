class DO:
	def __getattr__(self, name):
		return self.__dict__.get(name);
	def __contains__(self, name):
		return name in self.__dict__;
	def __iter__(self):
		return iter(self.__dict__);
	def __getitem__(self, name):
		return getattr(self, name);
	def __setitem__(self, key, value):
		self.__dict__[key] = value;
	def setdefault(self, key, value = None):
		return self.__dict__.setdefault(key, value);
