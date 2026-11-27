#!/bin/bash
A="timeout 60 adb"
$A install -r BraveTube.apk
$A logcat -c
$A shell am start -n com.foxysoxy.bravetube/.MainActivity --es selftest p3ug4IRm_ic --es testurl 'http://10.0.2.2:8099/videoplayback?itag=18'
sleep 85
timeout 90 adb logcat -d -v brief > alllog1.txt
grep BTTEST alllog1.txt > bttest.log
echo "Phase 1 fertig: $(wc -l < alllog1.txt) Zeilen"
timeout 30 adb shell am force-stop com.foxysoxy.bravetube
sleep 3
timeout 30 adb logcat -c
timeout 30 adb shell am start -n com.foxysoxy.bravetube/.MainActivity --es selftest p3ug4IRm_ic --es testurl 'http://10.0.2.2:8099/videoplayback?itag=99'
sleep 85
timeout 90 adb logcat -d -v brief > alllog2.txt
grep BTTEST alllog2.txt > bttest2.log
cat alllog1.txt alllog2.txt > alllog.txt
echo "Phase 2 fertig: $(wc -l < alllog2.txt) Zeilen"
exit 0
