# serve-svxlink-qso-recorder
Serve `qso*.ogg` files from `/qso_recorder/` directory of svxlink, with a directory webpage.

This program is written in Rye.
Use https://github.com/strickyak/rye to compile it.

```
$ cd $HOME/go/src
$ go get github.com/strickyak/serve-svxlink-qso-recorder
# ignore errors
$ go get github.com/strickyak/rye
# ignore errors
$ cd github.com/strickyak/rye ; make
$ cd ../serve-svxlink-qso-recorder
$ go run ../rye/rye.go build qso_server.py
$ ./qso_server \
  --spooldir=/usr/local/var/spool/svxlink/qso_recorder \
  --bind=:8080 \
  --title="Identify your repeater and echolink channel here."
```
