# athena_car_bringup/launch/car.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def include(package, launch_file, arguments=None):
    """Helper: include a launch file (.py or .xml) from another package."""
    return IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare(package), "launch", launch_file])
        ),
        launch_arguments=(arguments or {}).items(),
    )


def generate_launch_description():
    # drivers
    # Real hardware, publishes sensor data according to the interface contract.
    lidar = include("ldlidar_stl_ros2", "ld19.launch.py") 
    leds = include("athena_led_hardware", "led_hardware.launch.py")

    # VESC motor controller
    vesc_driver = include("vesc_driver", "vesc_driver_node.launch.py")
    # Converts Ackermann drive commands from control into VESC commands
    ackermann_to_vesc = include("vesc_ackermann", "ackermann_to_vesc_node.launch.xml")
    # Computes odometry from VESC motor/servo data
    vesc_to_odom = include("vesc_ackermann", "vesc_to_odom_node.launch.xml")

    # autonomy stack
    # Platform-agnostic autonomy, running on wall-clock time
    # with car-specific parameter overrides.
    overrides = PathJoinSubstitution(
        [FindPackageShare("athena_car_bringup"), "config", "overrides.yaml"]
    )
    autonomy = include(
        "athena_autonomous_racing",
        "autonomy.launch.py",
        {
            "use_sim_time": "false",
            "override_params": overrides,
        },
    )

    return LaunchDescription(
        [
            lidar,
            leds,
            vesc_driver,
            ackermann_to_vesc,
            vesc_to_odom,
            autonomy,
        ]
    )