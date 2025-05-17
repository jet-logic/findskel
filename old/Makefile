NAME=fileop

clean:
	del /Q ".build\*.*~*"

build: .build/to7z.py

q1: .build/fileop.py
#~ fileop -h .
q3: .build/fsaux.src

.build:
#~ mkdir .build

.build/fileop.py: .build fileop.src.py op/*.py SearchFile.py .build/usage.txt bracket_enc.py
	scrpp -Iop -I. -I.../_inc/python fileop.src.py | perl -ne "BEGIN{binmode(STDOUT)};print;"  > $@
	rm -f ".build/*.*~*"

.build/fsaux.src: .build fsop.*.py 
	scrpp -Iinc -I. -I.../_inc/python fsop.src.py | python  -c "import os,sys; a=os.fdopen(0,'Ub').read(); len(a) > 0 and open(sys.argv[1],'wb',16777216).write(a);" $@

q2: .build/manual.w.xml

.build/manual.w.xml: .build/manual.html doc/manual.w.xsl
#	tidy --doctype omit --output-xml 1 --numeric-entities 1 --add-xml-space 1 --output-encoding ascii --tidy-mark 0 --quote-nbsp 1 --newline LF \
#	--show-warnings 0 --wrap 0 --indent 1 .build/manual.html | xsltproc doc/manual.w.xsl - > $@
#	tidy --doctype omit --output-xml 1 --numeric-entities 1 --add-xml-space 1 --output-encoding ascii --tidy-mark 0 --quote-nbsp 1 --newline LF \
	xsltproc doc/manual.w.xsl .build/manual.html > $@

### CMDREF
doc/cmdref.xml: doc/cmdref.src.xml
	dbproc --type=cmdref --src $? --out $@
.build/manual.html: doc/manual.xml
	dbproc --type=html --src doc/manual.xml --out - | alter --out $@ -mmm -x --indent -pPullTag --tag div/span -
#~ dbproc --type=html --src doc/manual.xml --out $@
#~ alter -mmm -x --indent -pPullTag --tag div/span $@
#	--xsl doc/manual.xsl
.build/usage.txt: .build/manual.html
	lynx -nolist -dump -width=80 $? | perl -ne "if(/Filter files base on type/){exit(0)}elsif(/\S+/){print}"  > $@
man: .build/manual.html
### CMDREF
# lrun --cd I:\wrx\python\fsaux -- nmake q3
