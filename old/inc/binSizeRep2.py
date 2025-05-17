##inconce <binSizeBrk.py>
def binSizeRep2(N):
	(n, f, u) = binSizeBrk(N);
	return str(n) + "." + (f > 9 and str(f) or ('0' + str(f))) + ' ' + (u and (str(u) + 'i') or '') + "B" + (u and (' (' + str(N) + ' bytes)') or "");
