#!/bin/bash
A="timeout 60 adb"
$A install -r BraveTube.apk
$A logcat -c
$A shell am start -n com.foxysoxy.bravetube/.MainActivity --es selftest p3ug4IRm_ic --es testurl 'https://foxysoxy-tech.github.io/bt-test/test.mp4?itag=18'
for i in 1 2 3 4 5 6 7 8; do
  sleep 15
  timeout 25 adb logcat -b all -d -v brief > tmp1.txt 2>/dev/null
  [ -s tmp1.txt ] && cp tmp1.txt alllog1.txt
  echo "Lauf $i: $(wc -l < tmp1.txt) Zeilen, Geraet: $(timeout 10 adb get-state 2>&1 | head -1)"
done
grep BTTEST alllog1.txt > bttest.log
echo "Phase 1 fertig: $(wc -l < alllog1.txt) Zeilen"
timeout 30 adb shell am force-stop com.foxysoxy.bravetube
sleep 3
timeout 30 adb logcat -c
timeout 30 adb shell am start -n com.foxysoxy.bravetube/.MainActivity --es selftest p3ug4IRm_ic --es testurl 'https://test.googlevideo.com/videoplayback?itag=99'
sleep 85
timeout 90 adb logcat -d -v brief > alllog2.txt
grep BTTEST alllog2.txt > bttest2.log
cat alllog1.txt alllog2.txt > alllog.txt
echo "Phase 2 fertig: $(wc -l < alllog2.txt) Zeilen"
exit 0
