from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable

def generate_launch_description():

    gazebo_topic = '/world/default/model/x500_depth_0/link/camera_link/sensor/IMX214/image'

    return LaunchDescription([

        SetEnvironmentVariable(
            name='GZ_VERSION', 
            value='harmonic'
        ),

        ExecuteProcess(
            cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
            output='screen'
        ),

        ExecuteProcess(
            cmd=['ros2', 'run', 'ros_gz_image', 'image_bridge', gazebo_topic],
            output='screen'
        )
    ])
