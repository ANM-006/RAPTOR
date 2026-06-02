from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # IMU Telemetry Tracker
        Node(package='flight_bridge', executable='hz_tracker', output='screen'),
        
        # VIO Watchdog
        Node(package='flight_bridge', executable='failsafe', output='screen'),
        
        # SLAM Translators
        Node(package='flight_bridge', executable='bridge_node_enu', output='screen'),
        Node(package='flight_bridge', executable='bridge_node_ned', output='screen'),
        
        # EuRoC Camera Spoofer
        Node(package='flight_bridge', executable='fix_euroc', output='screen')
    ])
