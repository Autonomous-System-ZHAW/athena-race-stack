#!/bin/bash
# Source ROS and the workspace, then run the given command
set -e
source /opt/ros/$ROS_DISTRO/setup.bash
source /ros_ws/install/setup.bash
exec "$@"