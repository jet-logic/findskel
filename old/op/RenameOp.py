class RenameOp:
	m_subs = [];
	m_enumMethod = 0;
	def parseSubs(self, *ss):
		from re import compile;
		for s in ss:
			subs = [];
			ret = bracket_encode(s, copy_brack_trans(), subs);
			if len(ret) != 0 or len(subs) != 2:
				raise RuntimeError("Invalid subtitue pattern `%s'" % s);
			else:
				subs[0] = compile(subs[0]);
				self.m_subs.append(subs);
	def on_file_found(self, ctx, st, path, base, name):
		from os.path import join;
		from os import rename;
		name2 = None;
		dryRun = ctx.dryRun is not False;
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
			try:
				dryRun or rename(path, join(base, name2));
				self.m_n += 1;
			finally:
				say2("REN: %r -> %r" % (name, name2), dryRun and "?" or "!");
	def on_file_start(self, ctx):
		self.m_n = 0;
	def on_file_end(self, ctx):
		say2("REN:", self.m_n, "renamed");

class RenameFormatOp:
	m_subs = [];
	def parseSubs(self, *ss):
		from re import compile;
		for s in ss:
			subs = [];
			ret = bracket_encode(s, copy_brack_trans(), subs);
			if len(ret) != 0 or len(subs) != 2:
				raise RuntimeError("Invalid subtitue pattern `%s'" % s);
			else:
				subs[0] = compile(subs[0]);
				self.m_subs.append(subs);
	def on_file_found(self, ctx, st, path, base, name):
		from os.path import join;
		from os import rename;
		name2 = None;
		dryRun = ctx.dryRun is not False;
		name2 = name;
		for x in self.m_subs:
			m = x[0].search(name2);
			m = m and m.groupdict();
			#~ say2(repr(x), repr(m));
			if m:
				for k in m:
					if k[0] == 'i':
						m[k] = int(m[k], 10);
					elif k[0] == 'f':
						m[k] = float(k[0]);
					elif k[0] == 'x':
						m[k] = int(m[k], 16);
				name2 = x[1].format(**m);
		if name2 and (name != name2):
			try:
				dryRun or rename(path, join(base, name2));
				self.m_n += 1;
			finally:
				say2("RENF: %r -> %r" % (name, name2), dryRun and "?" or "!");
	def on_file_start(self, ctx):
		self.m_n = 0;
	def on_file_end(self, ctx):
		say2("RENF:", self.m_n, "renamed");
