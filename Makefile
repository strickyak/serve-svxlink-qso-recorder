all:
	test -f ../rye/bin/rye || ( cd ../rye ; make all )
	../rye/bin/rye build qso_server.py 

clean:
	rm -rf qso_server rye_
