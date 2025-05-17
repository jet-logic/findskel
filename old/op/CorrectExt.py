import re, imghdr;
from os.path import join, splitext, exists;
from os import rename;

class Counter:
	def __getattr__(self, name):
		return self.__dict__.setdefault(name, 0);
	def __contains__(self, name):
		return name in self.__dict__;
	def __getitem__(self, name):
		return getattr(self, name);
	def __setitem__(self, key, value):
		self.__dict__[key] = value;

TOT = Counter();
RENAME = lambda a,b : False;
CLUE = '?'
JPEG =  ('.jpeg', '.jpg');

def on_file_found(ctx, f):
	global JPEG
	if f.isdir:
		return
	t = imghdr.what(f.path)
	TOT.Files += 1;
	if t:
		t = ('.' + t).lower();
		(root, ext) = splitext(f.name)
		ext = ext.lower();
		if (t != ext) and (not ((ext in JPEG) and (t in JPEG))):
			name = root + t;
			print ('rename:', name, f.path, CLUE)
			RENAME(f, name)
			TOT.Renamed += 1;
		else:
			TOT.Same += 1;

def ren(f,name2):
	x = join(f.parent, name2);
	if exists(x):
		return False;
	if rename(f.path, x) is not False:
		f.reset(x);
	return x;

def on_file_start(ctx):
	global CLUE, RENAME
	if ctx.dryRun is False:
		CLUE = '!';
		RENAME = ren;

def on_file_end(ctx):
	if len(TOT.__dict__) :
		print 'CorrectExt:', ' '.join(('%s %d;' % (k, v) for (k, v) in TOT.__dict__.items()));

"""
fsaux -p I:\wrx\python\fsaux\op\CorrectExt.py M:\col
"""
