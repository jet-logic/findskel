class EmptyOp:
	def __init__(self, bCheck = True):
		self.bEmpty = bCheck;
	def on_file_found(self, ctx, st, path, *_):
		from stat import S_ISDIR;
		from os import listdir;
		nada = True;
		if S_ISDIR(st.st_mode):
			nada = len(listdir(path)) == 0;
		else:
			nada = st.st_size == 0;
		return (self.bEmpty == nada) and True or False;
