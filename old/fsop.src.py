#!/usr/bin/env python
##inconce <say1.py>
##inconce <say2.py>
##inconce <put2.py>
##inconce <iteropt.py>
##inconce <Counter.py>
##inconce <DO.py>
##inconce <glob_match.py>
##inconce <ntHardLinkInfo.py>
##inconce <fsop.aux.py>
##inconce <fsop.op1.py>
##inconce <fsop.op2.py>
import sys, os, logging, os.path as path
from os import listdir
from os.path import join, normpath

gCounterMap = {}
def getCounter(name):
	global gCounterMap
	if name not in gCounterMap:
		gCounterMap[name] = Counter()
	return gCounterMap[name]

def listdr(f0):
	try:
		return listdir(f0.path);
	except:
		logging.exception("Failed to list %r", f0.path)
	return ()

def walk_dir_pre(f0):
	d2 = f0.depth + 1;
	for name in listdr(f0):
		f1 = f0.__class__(join(f0.path, name))
		f1.depth = d2
		f1.rel = join(f0.rel, name)
		f1.walk = None
		yield f1
		if f1.walk:
			for x in walk_dir_pre(f1):
				yield x

def walk_dir_post(f0):
	d2 = f0.depth + 1;
	for name in listdr(f0):
		f1 = f0.__class__(join(f0.path, name))
		f1.rel = join(f0.rel, name)
		f1.depth = d2
		try:
			b = f1.isdir
		except:
			logging.error("Failed to process %r" % f1.path)
			continue
		if b:
			f1.walk = True
			for x in walk_dir_post(f1):
				yield x
		yield f1

def main():
	from collections import deque;
	ctx = DO()
	ctx.nVerbosity = 1
	ctx.carryOn = None
	ctx.fnSubs = []
	ctx.iglobs = []
	ctx.xglobs = []
	##########
	args = deque()
	opt = iteropt()
	icase = None
	mo = None
	mp = None
	print_opt = {}
	op = []
	def mo_init(_):
		x = getattr(_, 'on_file_init', None)
		x and x(ctx)
		return getattr(_, 'on_file_args', None)
	while opt.next():
		if opt.is_plain():
			args.append(opt.plain)
	# Module:
		elif opt.is_string('plugin', 'p'):
			if not mp:
				from os.path import isdir;
				mp = join(sys.path[0], '_rc', 'PYTHONLIB');
				isdir(mp) and (mp not in sys.path) and sys.path.append(mp);
				mp = join(sys.path[0], 'PYTHONLIB');
				isdir(mp) and (mp not in sys.path) and sys.path.append(mp);
			mo = None;
			try:
				mo = loadModule(opt, opt.string);
			finally:
				logging.info("Module:", mo and getattr(mo, '__name__', '') or '', repr(opt.string));
			if mo:
				op.append(mo);
				x = getattr(mo, 'on_file_init', None);
				x and x(ctx);
				mo = getattr(mo, 'on_file_args', None);
				# TODO: file_register_calback
		# If there is an module option callback, give him the first chance to pop the option.
		# If he pops an option, go to next. Notice that he can't use SHORT and PLAIN option
		elif mo and opt.is_long_form() and (mo(ctx, opt) or True) and (not opt.is_valid()):
			continue;
	# Main:
		elif opt.is_bool('dry-run'):#D
			ctx.dryRun = opt.bool;
		elif opt.is_true('act'):#D
			ctx.dryRun = not opt.bool;
		elif opt.is_true('quiet'):
			ctx.nVerbosity -= 1;
		elif opt.is_true('debug'):
			globals()['_DEBUG'] = True;
	# Walk:
		elif opt.is_bool('follow', 'L'):#D
			ctx.followSymLinks = opt.bool;
		elif opt.is_string('include',):#D
			ctx.iglobs.append(glob_match(opt.string, icase));
		elif opt.is_string('exclude',):#D
			ctx.xglobs.append(glob_match(opt.string, icase));
		elif opt.is_bool('depth', 'd'):#D
			ctx.postOrder = True;
		elif opt.is_bool('carryon'):#D
			ctx.carryOn = opt.bool;
		elif opt.is_bool('icase'):#D
			icase = opt.bool;
		#~ elif opt.is_integer('maxdepth'):#D
			#~ ctx.maxLevel = opt.integer;
		#~ elif opt.is_integer('mindepth'):#D
			#~ ctx.minLevel = opt.integer;
		#~ elif opt.is_string('rname', 'e'):#D
			#~ import re;
			#~ wkr.nameRE.append(re.compile(opt.string));
	# Filter:
		elif opt.is_string('type'):#D
			ctx.fileType = opt.string;
		elif opt.is_bool('empty'):#D
			ctx.emptyCheck = opt.bool;
		elif opt.is_string('size'):
			o = opt.string.split('..', 2);
			if not ctx.Sizes:
				ctx.Sizes = [];
			if o[0] and o[1]:
				ctx.Sizes.append(sorted((parseBinSize(o[0]), parseBinSize(o[1]))))
			elif o[0]:
				ctx.Sizes.append([parseBinSize(o[0]), None]);
			else:
				ctx.Sizes.append([0, parseBinSize(o[1])])
	# Print:
		elif opt.is_true('print'):#D
			print_opt['format'] = None;
		elif opt.is_true('basename'):#D
			print_opt['tail'] = True;
		elif opt.is_true('mingw'):#D
			print_opt['format'] = 'mingw';
		elif opt.is_true('cygwin'):#D
			print_opt['format'] = 'cygwin';
		elif opt.is_true('uri'):#D
			print_opt['format'] = 'uri';
	# Pre-Operator:
		elif opt.is_true('exstat'):#D
			mo = ctx.opExStat = ExStatOp();
			mo = mo_init(mo);
		elif opt.is_true('stat'):#D
			mo = ctx.opStat = StatOp();
			mo = mo_init(mo);
	# Operator:
		elif opt.is_true('del'):#D
			ctx.opDelete = opt.bool;
		elif opt.is_string('ren'):#D
			ctx.fnSubs.append(opt.string);
	# Misc:
		elif opt.is_bool('unicode'):
			ctx.bUnicode = opt.bool;
	##########
	_T = ((getattr(ctx, 'bUnicode', None) or (os.name == 'nt')) and (sys.hexversion < 0x03000000)) and unicode or (lambda x: x);
	### Pre-Operator
	(ctx.opExStat is not None) and op.append(ctx.opExStat);
	(ctx.opStat is not None) and op.append(ctx.opStat);
	#~ ### Level Filter
	#~ (ctx.minLevel or ctx.maxLevel) and insert_level_filter(ctx, w);
	cbItem = [];
	### Operator
	if len(ctx.fnSubs):
		o = RenameOp();
		o.parseSubs(*ctx.fnSubs);
		op.append(o);
	elif ctx.opDelete:
		ctx.postOrder = True;
		op.append(DeleteOp());
	if op:
		for x in op:
			hasattr(x, 'on_file_found') and cbItem.append(x.on_file_found);
		if print_opt:
			cbItem.append(print_func(**print_opt));
	else:
		cbItem.append(print_func(**print_opt));
	### Empty Filter
	if ctx.emptyCheck:
		def f_empty(_, p):
			if not p.isdir:
				return p.size > 0;
			try:
				for _ in listdir(p.path):
					return True;
			except:
				logging.exception("Failed to list %r", p.path);
		cbItem.insert(0, f_empty);
	### SymLink Filter
	if ctx.followSymLinks is not True:
		def listdr2(f0):
			try:
				if not f0.islink: return listdir(f0.path);
			except:
				logging.exception("Failed to list %r", f0.path);
			return ();
		listdr = listdr2;
	### Size Filter
	if ctx.Sizes:
		_s = ctx.Sizes;
		def f_size(_, p):
			n = p.size
			for v in _s:
				if (n < v[0]) or ((v[1] is not None) and (n > v[1])):
					return True
		cbItem.insert(0, f_size)
	### Globs
	if ctx.iglobs:
		_i = ctx.iglobs
		def f_globs(_, p):
			for v in _i:
				if v.match(p):
					return None
			return True
		cbItem.insert(0, f_globs)
	if ctx.xglobs:
		_x = ctx.xglobs;
		def f_globs(_, p):
			for v in _x:
				if v.match(p):
					#~ if v.nameOnly:
						#~ if v.dirOnly:
							#~ continue;
					return True
			return None;
		cbItem.insert(0, f_globs)
	### Type Filter
	if ctx.fileType:
		insert_type_filter(ctx, cbItem, ctx.fileType)
	### Walk
	walk_dir = ctx.postOrder and walk_dir_post or walk_dir_pre

	def walk():
		line = None
		while True:
			if args:
				x = args.popleft()
				if x == '-':
					line = True
					continue
			elif line:
				x = sys.stdin.readline().strip()
			else:
				x = None
			if not x:
				break
			f = normpath(_T(x))
			try:
				f = PathItem(f)
				x = f.isdir
			except:
				logging.error("Path failed %r" % x)
				if ctx.carryOn:
					continue
				else:
					raise
			f.depth = 0
			f.rel = ''
			f.walk = None
			if x:
				for x in walk_dir(f):
					yield x
			else:
				yield f

	for x in op:
		hasattr(x, 'on_file_start') and x.on_file_start(ctx)

	for f in walk():
		#~ if f.walk is None:
			#~ f.walk = f.isdir
		#
		for cb in cbItem:
			x = None
			try:
				x = cb(ctx, f)
			except:
				logging.error("Failed to process %r" % f.path)
				if ctx.carryOn:
					x = True
					f.walk = False
					f.isdir = False
				else:
					raise
			if x:
				break
			elif x is False:
				f.walk = False
		#
		if f is None:
			break;
		elif f.walk is None:
			try:
				f.walk = f.isdir
			except:
				logging.error("Failed to process %r" % f.path)
				continue
	for x in op:
		hasattr(x, 'on_file_end') and x.on_file_end(ctx)
	for k in gCounterMap:
		v = gCounterMap[k]
		len(v.__dict__)  and say2(k, ':', ' '.join(('%s %d;' % (k, v) for (k, v) in v.__dict__.items())))
main()

"""
pushd K:\wrx\python\fsaux
mee --cd K:\wrx\python\fsaux -- nmake q3 && fsaux B:\menu
""";
