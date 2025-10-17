FROM osrf/ros:jazzy-desktop-full

SHELL [ "/bin/bash" , "-c" ]

# Upgrade all packages
RUN sudo apt update && sudo apt upgrade -y

# Install essential packages
RUN sudo apt install -y wget python3-pip

# This is a workaround, but makes sense because we work in a Docker container and a venv is not really reasonable
COPY requirements.txt /requirements.txt
RUN pip install --break-system-packages --no-deps -r /requirements.txt

# Create overlay workspace
WORKDIR /ros_ws/src
COPY packages.repos .

RUN vcs import < packages.repos; \
    cd ..; \
    apt update; \
    rosdep update; \
    rosdep install --from-paths src --ignore-src -r -y; \
    source /opt/ros/${ROS_DISTRO}/setup.bash; \
    colcon build;

# Add sourcing overlay to .bashrc
RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
RUN echo "source /ros_ws/install/setup.bash" >> ~/.bashrc