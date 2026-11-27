#!/bin/bash
U=https://foxysoxy-tech.github.io/bt-test/test.mp4
M=https://foxysoxy-tech.github.io/bt-test/vp9.txt
AD=https://foxysoxy-tech.github.io/bt-test/ad.json
code() { curl -s -o /dev/null -w '%{http_code}' "$1"; }
NEED=0
if [ "$(code $U)" != "200" ] || [ "$(code $M)" != "200" ] || [ "$(code $AD)" != "200" ]; then NEED=1; fi
if [ "$NEED" = "1" ]; then
  command -v ffmpeg >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y ffmpeg >/dev/null)
  mkdir -p bt-test
  if [ "$(code $U)" != "200" ] || [ "$(code $M)" != "200" ]; then
    ffmpeg -y -loglevel error -f lavfi -i testsrc2=size=640x360:rate=25 -f lavfi -i sine=frequency=440 -t 180 -c:v libvpx-vp9 -deadline realtime -cpu-used 8 -b:v 300k -g 50 -pix_fmt yuv420p -c:a aac -b:a 64k -movflags +faststart bt-test/test.mp4
    echo "vp9 $(stat -c %s bt-test/test.mp4)" > bt-test/vp9.txt
  fi
  ffmpeg -y -loglevel error -f lavfi -i testsrc2=size=640x360:rate=25 -t 180 -c:v libvpx-vp9 -deadline realtime -cpu-used 8 -b:v 300k -g 50 -pix_fmt yuv420p -an -movflags +empty_moov+default_base_moof+global_sidx -frag_duration 2000000 bt-test/v.mp4
  ffmpeg -y -loglevel error -f lavfi -i sine=frequency=440 -t 180 -c:a aac -b:a 64k -vn -movflags +empty_moov+default_base_moof+global_sidx -frag_duration 2000000 bt-test/a.mp4
  python3 - <<'PY'
import json,struct
def boxes(p):
    d=open(p,'rb').read(); o=0; out=[]
    while o+8<=len(d):
        sz,t=struct.unpack('>I4s',d[o:o+8]); t=t.decode('latin1')
        if sz==1: sz=struct.unpack('>Q',d[o+8:o+16])[0]
        if sz==0: sz=len(d)-o
        out.append((t,o,o+sz)); o+=sz
    return len(d),out
def track(p,url,mime):
    n,b=boxes(p)
    moov=[x for x in b if x[0]=='moov'][0]; sidx=[x for x in b if x[0]=='sidx'][0]
    assert sidx[1]>=moov[2]
    return {"url":url,"mime":mime,"len":n,"init":[0,moov[2]-1],"idx":[sidx[1],sidx[2]-1],"dur":180000}
v=track('bt-test/v.mp4','https://test.googlevideo.com/bt-v?itag=137','video/mp4; codecs="vp09.00.10.08"')
a=track('bt-test/a.mp4','https://test.googlevideo.com/bt-a?itag=140','audio/mp4; codecs="mp4a.40.2"')
ad={"v":v,"a":a,"h":360,"opts":[]}
open('bt-test/ad.json','w').write(json.dumps(ad))
print(json.dumps(ad))
PY
  ls -la bt-test
  SZ=$(stat -c %s bt-test/a.mp4)
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add bt-test
  git commit -m "Testdateien (VP9, getrennte Spuren) fuer den Emulator-Test"
  git push
  for i in $(seq 1 100); do
    L=$(curl -sI "https://foxysoxy-tech.github.io/bt-test/a.mp4?x=$RANDOM" | tr -d '\r' | awk 'tolower($1)=="content-length:"{print $2}')
    [ "$(code $AD)" = "200" ] && [ "$L" = "$SZ" ] && break
    sleep 6
  done
fi
echo "Testvideo: HTTP $(code $U) Spuren: HTTP $(code $AD)"
curl -sI -H "Range: bytes=0-99" "$U" | head -12
