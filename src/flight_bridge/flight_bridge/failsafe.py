import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from px4_msgs.msg import VehicleCommand

class FailsafeWatchdog(Node):
    def __init__(self):
        super().__init__('failsafe_watchdog')

        # subscribing to the VIO Odometry topic
        self.vio_sub = self.create_subscription(
            Odometry,
            '/rtabmap/odom',
            self.vio_callback,
            10
        )

        # publisher to command PX4 via uXRCE-DDS bridge
        self.px4_cmd_pub = self.create_publisher(
            VehicleCommand,
            '/fmu/in/vehicle_command',
            10
        )

        # Track the last time the data was received
        self.last_vio_time = self.get_clock().now()
        self.failsafe_triggered = False
        # Create a high-frequency watchdog timer (50Hz)
        self.watchdog_timer = self.create_timer(0.02, self.check_vio_timeout)

        self.get_logger().info('Failure Watchdog Node initialized and monitoring...')

    def vio_callback(self, msg):
        # Resets the timeout clock every time a fresh VIO packet arrives.
        if not self.failsafe_triggered:
            self.last_vio_time = self.get_clock().now()

    def check_vio_timeout(self):
        # Evaluates if the delta exceeds the critical 0.5-second threshold.
        if self.failsafe_triggered:
            # keep publishing the land command to ensure PX4 receives it
            self.send_auto_land_command()
            return
        
        current_time = self.get_clock().now()
        #calculate the time elapsed in nanoseconds, convert to seconds
        elapsed_time = (current_time - self.last_vio_time).nanoseconds / 1e9

        if elapsed_time > 0.5:
            self.get_logger().error(f'CRITICAL: VIO stream lost for {elapsed_time:.2f}s! Initiating Failsafe.')
            self.failsafe_triggered = True
            self.send_auto_land_command()

    def send_auto_land_command(self):
        # Formats and sends the specific vehicle command to force PX4 to land.
        msg = VehicleCommand()
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000) # PX4 uses microseconds
        msg.command = VehicleCommand.VEHICLE_CMD_NAV_LAND # PX4 internal command ID for Auto-Land
        msg.param1 = 0.0 #Precision land parameters if applicable
        msg.target_system = 1 #Standard MAVLink System ID for the drone
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True

        self.px4_cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FailsafeWatchdog()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
