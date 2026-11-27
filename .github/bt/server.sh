#!/bin/bash
U=https://foxysoxy-tech.github.io/bt-test/test.mp4
code() { curl -s -o /dev/null -w '%{http_code}' "$U"; }
if [ "$(code)" != "200" ]; then
  command -v ffmpeg >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y ffmpeg >/dev/null)
  mkdir -p bt-test
  ffmpeg -y -loglevel error -f lavfi -i testsrc2=size=640x360:rate=25 -f lavfi -i sine=frequency=440 -t 180 -c:v libx264 -preset veryfast -crf 32 -pix_fmt yuv420p -c:a aac -b:a 64k -movflags +faststart bt-test/test.mp4
  ls -la bt-test/test.mp4
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add bt-test/test.mp4
  git commit -m "Testvideo für den Emulator-Test"
  git push
  for i in $(seq 1 60); do [ "$(code)" = "200" ] && break; sleep 5; done
fi
echo "Testvideo: HTTP $(code)"
curl -sI -H "Range: bytes=0-99" "$U" | head -12
echo "mock.out" > mock.out
