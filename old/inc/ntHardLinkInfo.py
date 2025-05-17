def ntHardLinkInfo(*args):
	#print('ntHardLinkInfo', args)
	global ntHardLinkInfo
	from ctypes import windll, c_uint32, c_wchar_p, c_void_p, WinError, create_string_buffer, byref;
	from struct import unpack;
	(GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, INVALID_HANDLE_VALUE) = (c_uint32(0x80000000), c_uint32(0x00000001), c_uint32(3), 0x00000080, c_void_p(-1));
	FILE_FLAG_BACKUP_SEMANTICS   = 0x02000000
	CreateFileW = windll.kernel32.CreateFileW;
	GetFileInformationByHandle = windll.kernel32.GetFileInformationByHandle;
	CloseHandle = windll.kernel32.CloseHandle;
	def O(file, flag = None):
		FileName = c_wchar_p(file);
		FileHandle = CreateFileW(FileName, GENERIC_READ, FILE_SHARE_READ, None, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS+FILE_ATTRIBUTE_NORMAL, None);
		if FileHandle == -1:
			raise WinError();
		try:
			buf = create_string_buffer(52);
			if GetFileInformationByHandle(FileHandle, byref(buf)):
				(v, n, h, l) = unpack("<28xL8xLLL", buf.raw);
			else:
				raise WinError();
		finally:
			if not CloseHandle(FileHandle):
				raise WinError();
		return (v, (h << 32) | l, n)
	ntHardLinkInfo = O;
	return ntHardLinkInfo(*args);
