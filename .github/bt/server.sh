#!/bin/bash
command -v ffmpeg >/dev/null || (sudo apt-get update -qq && sudo apt-get install -y ffmpeg >/dev/null)
nohup python3 .github/bt/mock.py > mock.out 2>&1 &
for i in $(seq 1 90); do curl -s -o /dev/null http://127.0.0.1:8099/x && break; sleep 2; done
head -3 mock.out
