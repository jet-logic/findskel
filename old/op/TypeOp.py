class TypeOp:
	typeFunc = [];
	def on_file_found(self, ctx, st, *_):
		for k in self.typeFunc:
			if k(st.st_mode):
				return True;
		return False;

