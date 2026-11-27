#!/bin/bash
adb install -r BraveTube.apk
adb logcat -c
adb shell am start -n com.foxysoxy.bravetube/.MainActivity --es selftest p3ug4IRm_ic --es testurl 'http://10.0.2.2:8099/videoplayback?itag=18'
sleep 85
adb logcat -d -s BTTEST:I -v brief > bttest.log
adb shell am force-stop com.foxysoxy.bravetube
adb logcat -c
adb shell am start -n com.foxysoxy.bravetube/.MainActivity --es selftest p3ug4IRm_ic --es testurl 'http://10.0.2.2:8099/videoplayback?itag=99'
sleep 85
adb logcat -d -s BTTEST:I -v brief > bttest2.log
adb logcat -d -v brief > alllog.txt
