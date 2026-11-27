#!/bin/bash
U=https://foxysoxy-tech.github.io/bt-test/test.mp4
M=https://foxysoxy-tech.github.io/bt-test/vp9.txt
code() { curl -s -o /dev/null -w '%{http_code}' "$1"; }
if [ "$(code $U)" != "200" ] || [ "$(code $M)" != "200" ]; then
  command -v ffmpeg >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y ffmpeg >/dev/null)
  mkdir -p bt-test
  ffmpeg -y -loglevel error -f lavfi -i testsrc2=size=640x360:rate=25 -f lavfi -i sine=frequency=440 -t 180 -c:v libvpx-vp9 -deadline realtime -cpu-used 8 -b:v 300k -g 50 -pix_fmt yuv420p -c:a aac -b:a 64k -movflags +faststart bt-test/test.mp4
  ls -la bt-test/test.mp4
  SZ=$(stat -c %s bt-test/test.mp4)
  echo "vp9 $SZ" > bt-test/vp9.txt
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add bt-test/test.mp4 bt-test/vp9.txt
  git commit -m "Testvideo (VP9) fuer den Emulator-Test"
  git push
  for i in $(seq 1 100); do
    L=$(curl -sI "$U?x=$RANDOM" | tr -d '\r' | awk 'tolower($1)=="content-length:"{print $2}')
    [ "$(code $M)" = "200" ] && [ "$L" = "$SZ" ] && break
    sleep 6
  done
fi
echo "Testvideo: HTTP $(code $U)"
curl -sI -H "Range: bytes=0-99" "$U" | head -12
echo "mock.out" > mock.out
