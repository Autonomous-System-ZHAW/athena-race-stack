#!/usr/bin/env bash
# .devcontainer/post_create.sh
# Runs once when the container is created.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WS_DIR="$(dirname "$REPO_DIR")"

echo ">>> Importing repositories"
mkdir -p "$REPO_DIR/src"
vcs import --recursive --skip-existing --input "$REPO_DIR/car.repos" "$REPO_DIR/src"
vcs import --recursive --skip-existing --input "$REPO_DIR/src/athena_autonomous_racing/athena.repos" "$REPO_DIR/src"

echo ">>> Installing ROS dependencies"
sudo apt-get update
rosdep update
rosdep install --from-paths "$REPO_DIR" --ignore-src --rosdistro "$ROS_DISTRO" -r -y

echo ">>> Configuring shell"
BASHRC="$HOME/.bashrc"
ROS_LINE="source /opt/ros/$ROS_DISTRO/setup.bash"
WS_LINE="[ -f $WS_DIR/install/setup.bash ] && source $WS_DIR/install/setup.bash"

# Add each line to .bashrc only if it is not there yet
if ! grep -qxF "$ROS_LINE" "$BASHRC"; then
    echo "$ROS_LINE" >> "$BASHRC"
fi
if ! grep -qxF "$WS_LINE" "$BASHRC"; then
    echo "$WS_LINE" >> "$BASHRC"
fi

echo ">>> Done. Build with: cd $WS_DIR && colcon build --symlink-install"