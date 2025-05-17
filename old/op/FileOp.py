class FileOp:
	ctx = None;
	def __init__(self, ctx_):
		self.ctx = ctx_;
	def on_file_found(self, ctx, st, path, base, name):
		pass;
	def on_file_start(self, ctx):
		pass;
	def on_file_end(self, ctx):
		pass;
