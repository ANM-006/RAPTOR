from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='flight_bridge',
            executable='hz_tracker',
            name='hz_tracker_node',
            output='screen'
        ),
        Node(
            package='flight_bridge',
            executable='failsafe',
            name='failsafe_node',
            output='screen'
        )
    ])

