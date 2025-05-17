import sys, os;

from ctypes import windll, c_uint32, c_wchar_p, c_void_p, WinError, create_string_buffer, byref;
from struct import unpack;

(GENERIC_READ, FILE_SHARE_READ, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, INVALID_HANDLE_VALUE) = (c_uint32(0x80000000), c_uint32(0x00000001), c_uint32(3), c_uint32(0x00000080), c_void_p(-1));
CreateFileW = windll.kernel32.CreateFileW;
GetFileInformationByHandle = windll.kernel32.GetFileInformationByHandle;
CloseHandle = windll.kernel32.CloseHandle;

def nt_inode(file):
	#say2("nt_inode", file);
	nFileIndex = None;
	h = None;
	l = None;
	FileName = c_wchar_p(file);
	FileHandle = CreateFileW(FileName, GENERIC_READ, FILE_SHARE_READ, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None);
	if FileHandle == -1:
		raise WinError();
	try:
		buf = create_string_buffer(52);
		if GetFileInformationByHandle(FileHandle, byref(buf)):
			(h, l) = unpack("<44xLL", buf.raw);
		else:
			raise WinError();
	finally:
		if not CloseHandle(FileHandle):
			raise WinError();
	return (h << 32) | l;

file_id_map = None;
file_id_out = None;

def on_file_found(ctx, f):
	if f.isdir:
		return
	id = nt_inode(f.path);
	id = "%x" % (id, );
	#~ id = base64.b16encode(id);
	if file_id_map is None:
		print (id, f.path);
	else:
		file_id_map[id] = os.path.realpath(f.path)
	
def on_file_args(ctx, opt):
	global file_id_map, file_id_out;
	if opt.is_string('json'):
		file_id_map = {};
		file_id_out = opt.string;
		print ('file_id_map', file_id_out)
		
def on_file_end(ctx):
	global file_id_map, file_id_out;
	if file_id_map is None:
		return 
	import json;
	if (file_id_out is None) or (file_id_out == '-'):
		print json.dumps(file_id_map, indent=1)
	else:
		o = open(file_id_out, 'wb')
		try:
			json.dump(file_id_map, o, indent=1)
		finally:
			o.close();

"""
fsaux -p I:\wrx\python\fileop.py\op\lsFileId.py --json B:\temp\file_id_map.json B:\temp\unattended.msfn.org
fsutil file queryfileid B:\menu\Compression\WinRAR.lnk
"""