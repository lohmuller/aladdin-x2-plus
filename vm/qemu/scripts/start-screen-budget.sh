#!/system/bin/sh
export CLASSPATH=/data/local/tmp/vm-screen-stream-budget.dex
/data/local/tmp/busybox nohup /data/local/tmp/busybox nice -n 10 /system/bin/app_process32 /system/bin vm.ScreenStream 640 360 3 >/data/local/tmp/screen-stream-budget.log 2>&1 &
echo $! >/data/local/tmp/screen-stream.pid
