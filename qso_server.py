# Serve qso*.ogg files from /qso_recorder/ directory of svxlink.

from go import flag, os, net.http, regexp, time
from go import path.filepath as FP

BIND = flag.String('bind', ':8080', 'Port to server HTTP on')
SPOOLDIR = flag.String('spooldir', '/usr/local/var/spool/svxlink/qso_recorder', 'where to find dated .ogg files')
TITLE = flag.String('title', 'Identify your repeater and echolink channel here.', 'Root page title')

YMD = '2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
HMS = '[0-2][0-9][0-9][0-9][0-9][0-9]'
FILENAME_PATTERN = regexp.MustCompile('_(' + YMD + '_' + HMS + ')_(' + YMD + '_' + HMS + ').ogg$')
TIMESTAMP = '2006-01-02_150405 -0700'
CALIF = time.LoadLocation('America/Los_Angeles')

class Ogg:
  def __init__(filename):
    .filename = filename
    m = FILENAME_PATTERN.FindStringSubmatch(filename)
    assert m, filename
    _, m1, m2 = m
    .t1 = time.Parse(TIMESTAMP, m1 + ' +0000')
    .t2 = time.Parse(TIMESTAMP, m2 + ' +0000')
    .dur = go_cast(time.Duration, .t2.Sub(.t1))
    .z_day = .t1.Format('2006-01-02')
    .z_hr = .t1.Format('15')
    .c_day = .t1.In(CALIF).Format('2006-01-02')
    .c_hr = .t1.In(CALIF).Format('15')
    .size = os.Stat(filename).Size()

class Glob:
  def __init__(dirname):
    .oggs = {}
    .day_hr = {}
    for filename in FP.Glob(dirname + '/qso*.ogg'):
      o = Ogg(filename)
      .oggs[filename] = o

      d = .day_hr.get(o.z_day)
      if not d:
        d = {}
        .day_hr[o.z_day] = d

      h = d.get(o.z_hr)
      if not h:
        h = {}
        d[o.z_hr] = h

      h[o.t1.Unix()] = o

  def Emit(w):
    print >>w, """
<html>
<head>
  <title>{title}</title>
</head>
<body>
<h2>{title}</h2>
<table border=1 cellpadding=2>
  <tr>
    <th>UTC
    <th>California
    <th>Sound Files
""".format(title=go_elem(TITLE))

    for day, d in sorted(.day_hr.items(), reverse=True):
      for hr, h in sorted(d.items(), reverse=True):
        first = h.values()[0]
        print >>w, """
  <tr>
    <td><tt>{o.z_day} {o.z_hr}:**</tt>
    <td><tt>{o.c_day} {o.c_hr}:**</tt>
    <td>
""".format(o=first)
        for secs, o in sorted(h.items()):
          kilos=int((o.size + 999) / 1000 )
          A, B = '', ''
          if kilos <= 25: A, B = '<small>', '</small>'
          if kilos >= 1000: A, B = '<b>', '</b>'
          print >>w, """
      <a href="qso_recorder/{filebase}">{A}{start}({duration},{kilos}k){B}</a>
      &nbsp;
""".format(  filebase=FP.Base(o.filename),
             start=o.t1.Format(':04:05'),
             duration=o.dur,
             kilos=kilos, secs=secs, A=A, B=B,
             )
        print >>w, """
    <td>  <a href="playlist.m3u?starting={secs}">playlist</a>
""".format(secs=sorted(h.keys())[0])

    print >>w, """
</table>
</body>
</html>
"""

  def EmitPlaylist(w, r, starting):
    w.Header().Set('Content-Type', 'audio/mpegurl')
    w.WriteHeader(http.StatusOK)
    for day, d in sorted(.day_hr.items()):
      for hr, h in sorted(d.items()):
        for secs, o in sorted(h.items()):
          if int(secs) >= starting:
            print >>w, 'http://{host}/qso_recorder/{filebase}'.format(
                host=r.Host,
                filebase=FP.Base(o.filename),
                )

def RootHandler(spool):
  def handler(w, r):
    try:
      values = dict(r.URL.Query())
      if 'starting' in values:
        Glob(spool).EmitPlaylist(w, r, int(values['starting'][0]))
      else:
        Glob(spool).Emit(w)
    except as ex:
      print >>w, ex
  return handler

def main(args):
  flag.Parse()
  spool = str(go_elem(SPOOLDIR))

  http.HandleFunc("/qso_recorder/", http.StripPrefix("/qso_recorder/", http.FileServer(go_cast(http.Dir, spool))))
  http.HandleFunc("/", RootHandler(spool))

  print >>os.Stderr, '# Starting Server at %s' % time.Now().Format(time.Stamp)
  http.ListenAndServe(go_elem(BIND), None)
