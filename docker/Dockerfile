# syntax=docker/dockerfile:1

# base: everything both dev and deploy need
FROM ros:jazzy-ros-base AS base

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        wget \
        tmux \
        openssh-client \
        python3-pip \
        python3-rosdep \
        python3-vcstool \
        libasio-dev \
    && rm -rf /var/lib/apt/lists/*

# Raspberry Pi 5 NeoPixel support (athena_led_hardware)
RUN pip install --break-system-packages \
        pi5neo \
        lgpio \
        adafruit-blinka \
        adafruit-circuitpython-neopixel \
        adafruit-circuitpython-pixelbuf \
        Adafruit-Blinka-Raspberry-Pi5-Neopixel

# Further Python dependencies shared by dev and deploy
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages --no-deps -r /tmp/requirements.txt

# Shared tmux configuration (system-wide, applies to every user)
COPY config/tmux.conf /etc/tmux.conf

# DDS / ROS configuration shared by dev and deploy
COPY config/fastdds.xml /etc/athena/fastdds.xml
ENV FASTRTPS_DEFAULT_PROFILES_FILE=/etc/athena/fastdds.xml
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp
ENV ROS_DOMAIN_ID=101

# dev: interactive development via devcontainer
FROM base AS dev

ARG USERNAME=baberry
ARG USER_UID=1000
ARG USER_GID=${USER_UID}
ARG WS_BASENAME=athena-race-stack

# Remove existing user with the same UID (e.g. "ubuntu" in Noble images)
RUN if id -u "$USER_UID" >/dev/null 2>&1; then userdel "$(id -un "$USER_UID")"; fi

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y --no-install-recommends sudo build-essential python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && usermod -a -G dialout $USERNAME \
    && mkdir -p /home/$USERNAME/ros2_ws/$WS_BASENAME \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME/ros2_ws

ENV SHELL=/bin/bash
CMD ["/bin/bash"]


# deploy: frozen, self-contained race image
# Requires deploy.repos (created with: vcs export --exact src > deploy.repos)
# Build: docker build --ssh default --target deploy -t athena-race-stack:deploy -f docker/Dockerfile .
FROM base AS deploy

WORKDIR /ros_ws

# Frozen package list
COPY deploy.repos /ros_ws/deploy.repos

# Clone with the host's SSH key; the key is NOT stored in the image
RUN --mount=type=ssh \
    mkdir -p ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts \
    && mkdir -p src \
    && vcs import --recursive --input deploy.repos src

# Car bringup lives in this repo, not in the .repos file
COPY athena_car_bringup /ros_ws/src/athena_car_bringup

RUN apt-get update \
    && rosdep update \
    && rosdep install --from-paths src --ignore-src -r -y \
    && rm -rf /var/lib/apt/lists/*

RUN source /opt/ros/$ROS_DISTRO/setup.bash \
    && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ros2", "launch", "athena_car_bringup", "car.launch.py"]