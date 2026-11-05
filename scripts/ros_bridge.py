#!/usr/bin/env python3
"""
ROS bridge for the VESC monitor.

Runs inside the ROS 2 Docker container next to vesc_driver. It subscribes to
the vesc_driver state topic and forwards each sample (max. RATE_HZ) as JSON to
the monitor on the Raspberry Pi host (vesc_monitor.py started with SOURCE=push).

Needs only rclpy and vesc_msgs, which the container already has; everything
else is from the Python standard library.

Run inside the container (after sourcing ROS and the workspace):
    python3 ros_bridge.py

Environment variables:
    MONITOR_URL  where the monitor runs (default http://127.0.0.1:8080/api/push,
                 works with --network host; otherwise use the host's IP,
                 e.g. http://172.17.0.1:8080/api/push)
    ROS_TOPIC    vesc_driver state topic (default /sensors/core)
    RATE_HZ      max. samples per second sent to the monitor (default 10)
"""

import json
import os
import threading
import time
import urllib.request

import rclpy
from vesc_msgs.msg import VescStateStamped

MONITOR_URL = os.environ.get("MONITOR_URL", "http://127.0.0.1:8080/api/push")
ROS_TOPIC = os.environ.get("ROS_TOPIC", "/sensors/core")
RATE_HZ = float(os.environ.get("RATE_HZ", "10"))

latest = None  # newest sample, sent by the sender thread
cond = threading.Condition()


def on_state(msg):
    global latest
    s = msg.state
    with cond:
        latest = {n: getattr(s, n) for n in s.get_fields_and_field_types()}
        cond.notify()


def sender():
    """Send samples in a separate thread so a slow monitor never blocks ROS."""
    global latest
    ok = None
    while True:
        with cond:
            while latest is None:
                cond.wait()
            sample, latest = latest, None
        try:
            req = urllib.request.Request(
                MONITOR_URL,
                data=json.dumps(sample).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=1).read()
            if ok is not True:
                print(f"[ros_bridge] sending to {MONITOR_URL}", flush=True)
            ok = True
        except Exception as e:
            if ok is not False:  # print each error state only once
                print(
                    f"[ros_bridge] cannot reach monitor at {MONITOR_URL}: {e}",
                    flush=True,
                )
            ok = False
            time.sleep(1)
        time.sleep(1 / RATE_HZ)


def main():
    rclpy.init()
    node = rclpy.create_node("vesc_monitor_bridge")
    node.create_subscription(VescStateStamped, ROS_TOPIC, on_state, 10)
    threading.Thread(target=sender, daemon=True).start()
    print(f"[ros_bridge] listening on {ROS_TOPIC}", flush=True)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
