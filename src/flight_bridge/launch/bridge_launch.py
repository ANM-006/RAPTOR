from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable

def generate_launch_description():
    gazebo_topic = '/world/default/model/x500_depth_0/link/camera_link/sensor/IMX214/image'

    return LaunchDescription([
        # Global Environment Variables
        SetEnvironmentVariable('RMW_IMPLEMENTATION', 'rmw_fastrtps_cpp'),
        SetEnvironmentVariable('GZ_VERSION', 'harmonic'),

        # Initialise Micro-XRCE-DDS Agent
        ExecuteProcess(
            cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
            output='screen'
        ),
        
        # Bridge Command
        ExecuteProcess(
            cmd=['bash', '-c', f'source /opt/ros/jazzy/setup.bash && ros2 run ros_gz_image image_bridge {gazebo_topic}'],
            output='screen'
        ),

        # Viewer Command
        ExecuteProcess(
            cmd=['bash', '-c', f'source /opt/ros/jazzy/setup.bash && ros2 run image_tools showimage --ros-args -r image:={gazebo_topic}'],
            output='screen'
        ),

        # LidarBridge
        ExecuteProcess(
            cmd=['bash', '-c', 'source /opt/ros/jazzy/setup.bash && ros2 run ros_gz_bridge parameter_bridge /depth_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked'],
            output='screen'
        )
    ])