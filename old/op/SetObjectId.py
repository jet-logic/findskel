class Counter:
	def __getattr__(self, name):
		return self.__dict__.setdefault(name, 0);
	def __contains__(self, name):
		return name in self.__dict__;
	def __iter__(self):
		return iter(self.__dict__);
	def __getitem__(self, name):
		return getattr(self, name);
	def __setitem__(self, key, value):
		self.__dict__[key] = value;

def fsctlSetObjectId(*args):
	global fsctlSetObjectId
	from ctypes.wintypes import windll, c_wchar_p, create_string_buffer, c_void_p, byref, WinError;
	CreateFileW = windll.kernel32.CreateFileW;
	CloseHandle = windll.kernel32.CloseHandle;
	DeviceIoControl = windll.kernel32.DeviceIoControl;
	FSCTL_CREATE_OR_GET_OBJECT_ID=590016
	FSCTL_GET_OBJECT_ID=589980
	FSCTL_SET_OBJECT_ID_EXTENDED=590012
	GENERIC_WRITE = 0x40000000;
	GENERIC_READ = 0x80000000;
	FILE_SHARE_READ = 0x00000001;
	FILE_SHARE_WRITE = 0x00000002;
	FILE_SHARE_DELETE = 0x00000004;
	OPEN_EXISTING = 3;
	FILE_ATTRIBUTE_NORMAL = 0x00000080;
	def call(f):
		f = c_wchar_p(f);
		h = CreateFileW(f, GENERIC_READ|GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None);
		if h == -1:
			raise WinError();
		try:
			buf = create_string_buffer(64);
			xLen = c_void_p(48);
			if 0 == DeviceIoControl(h, FSCTL_CREATE_OR_GET_OBJECT_ID, None, 0, buf, 64, byref(xLen), None):
				raise WinError();
		finally:
			if not CloseHandle(h):
				raise WinError();
		return
	fsctlSetObjectId = call
	return fsctlSetObjectId(*args)
	
def fsctlHasObjectId(*args):
	global fsctlHasObjectId
	from ctypes.wintypes import windll, c_wchar_p, create_string_buffer, c_void_p, byref, WinError;
	CreateFileW = windll.kernel32.CreateFileW;
	CloseHandle = windll.kernel32.CloseHandle;
	DeviceIoControl = windll.kernel32.DeviceIoControl;
	FSCTL_CREATE_OR_GET_OBJECT_ID=590016
	FSCTL_GET_OBJECT_ID=589980
	FSCTL_SET_OBJECT_ID_EXTENDED=590012
	GENERIC_WRITE = 0x40000000;
	GENERIC_READ = 0x80000000;
	FILE_SHARE_READ = 0x00000001;
	FILE_SHARE_WRITE = 0x00000002;
	FILE_SHARE_DELETE = 0x00000004;
	OPEN_EXISTING = 3;
	FILE_ATTRIBUTE_NORMAL = 0x00000080;
	def call(f):
		f = c_wchar_p(f);
		h = CreateFileW(f, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None);
		if h == -1:
			raise WinError();
		try:
			buf = create_string_buffer(64);
			xLen = c_void_p(48);
			return 0 != DeviceIoControl(h, FSCTL_GET_OBJECT_ID, None, 0, buf, 64, byref(xLen), None)
		finally:
			if not CloseHandle(h):
				raise WinError();
		return None
	fsctlHasObjectId = call
	return fsctlHasObjectId(*args)
	
TOT = Counter()
def on_file_found(ctx, f):
	if f.isdir:
		return
	if fsctlHasObjectId(f.path):
		TOT.Already += 1
	else:
		TOT.Set += 1;
		fsctlSetObjectId(f.path)

def on_file_end(ctx):
	if len(TOT.__dict__): print('SetObjectId:', ' '.join(('%s %d;' % (k, v) for (k, v) in TOT.__dict__.items())));

"""
fsaux -p I:\wrx\python\fileop.py\op\SetObjectId.py B:\temp
fsutil file queryfileid B:\menu\Compression\WinRAR.lnk
"""