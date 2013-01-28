develop:
	if [ ! -x bin/buildout ]; then \
	    mkdir -p lib/buildout; \
	    wget -O lib/buildout/bootstrap.py https://raw.github.com/buildout/buildout/1.7.0/bootstrap/bootstrap.py; \
	    python lib/buildout/bootstrap.py --distribute; \
	fi
	bin/buildout -N
