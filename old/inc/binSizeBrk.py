def binSizeBrk(n):
	(f, u) = (0, 0);
	while (n > 10000):
		f = ((n%(1 << 10)) * 100) >> 10; # (n%1024)*(100/1024)
		n = n >> 10; # n/(1**1024)
		u += 1;
	u = ((u==1) and 'k') or ((u==2) and 'M') or ((u==3) and 'G') or ((u==4) and 'T') or ((u==5) and 'P') or ((u==6) and 'E') or ((u==7) and 'Z') or ((u==8) and 'Y') or (not (u==0) and None) or '';
	return n, f, u;
