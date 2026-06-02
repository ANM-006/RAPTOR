import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from px4_msgs.msg import SensorCombined

class HzTracker(Node):
    def __init__(self):
        super().__init__('hz_tracker')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.subscription = self.create_subscription(
            SensorCombined,
            '/fmu/out/sensor_combined',
            self.listener_callback,
            qos_profile
        )

        self.last_msg_timestamp = 0
        self.last_receive_time = self.get_clock().now()
        
        self.watchdog_timer = self.create_timer(0.5, self.watchdog_callback)

    def listener_callback(self, msg):
        self.last_receive_time = self.get_clock().now()
        
        if self.last_msg_timestamp > 0:
            dt_micro = msg.timestamp - self.last_msg_timestamp
            if dt_micro > 0:
                hz = 1_000_000.0 / dt_micro
                self.get_logger().info(f"Current Frequency: {hz:.2f} Hz")
                
        self.last_msg_timestamp = msg.timestamp

    def watchdog_callback(self):
        time_since_last = (self.get_clock().now() - self.last_receive_time).nanoseconds / 1e9
        if time_since_last > 0.5:
            self.get_logger().warn("Waiting for telemetry... (0.00 Hz)")
            self.last_msg_timestamp = 0

def main(args=None):
    rclpy.init(args=args)
    node = HzTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
