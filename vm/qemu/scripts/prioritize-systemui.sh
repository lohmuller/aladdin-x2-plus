#!/system/bin/sh
# VM only. Run before starting the framebuffer stream after Android boots.
systemui_pid=$(pidof com.android.systemui)
if [ -z "$systemui_pid" ]; then
    am startservice -n com.android.systemui/.SystemUIService || exit 1
fi
for attempt in 1 2 3 4 5 6 7 8 9 10; do
    systemui_pid=$(pidof com.android.systemui)
    if [ -n "$systemui_pid" ]; then
        # BusyBox without -n sets an absolute priority (does not increment it).
        /data/local/tmp/busybox renice -10 -p "$systemui_pid" || exit 1
        echo "SystemUI $systemui_pid prioritized"
        exit 0
    fi
    /data/local/tmp/busybox sleep 1
done
echo 'SystemUI did not start' >&2
exit 1
