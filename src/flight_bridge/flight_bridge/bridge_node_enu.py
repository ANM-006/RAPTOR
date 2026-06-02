#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped

from tf2_ros import TransformBroadcaster


class SlamBridgeENUNode(Node):

    def __init__(self):
        super().__init__('slam_bridge_enu_node')

        self.subscription = self.create_subscription(
            Odometry,
            '/rtabmap/odom',
            self.odom_callback,
            10
        )

        self.filtered_pub = self.create_publisher(
            Odometry,
            '/filtered_odom_enu',
            10
        )

        self.tf_broadcaster = TransformBroadcaster(self)

        self.get_logger().info('SLAM Bridge ENU Node Started')

    def odom_callback(self, msg):

        filtered_msg = Odometry()

        # Preserve timestamp
        filtered_msg.header.stamp = msg.header.stamp

        # ENU frame convention
        filtered_msg.header.frame_id = 'odom'
        filtered_msg.child_frame_id = 'base_link'

        # Preserve pose directly
        filtered_msg.pose.pose = msg.pose.pose

        # Preserve twist directly
        filtered_msg.twist.twist = msg.twist.twist

        # Preserve covariance
        filtered_msg.pose.covariance = msg.pose.covariance
        filtered_msg.twist.covariance = msg.twist.covariance

        # Publish filtered ENU odometry
        self.filtered_pub.publish(filtered_msg)

        # TF Broadcast
        tf_msg = TransformStamped()

        tf_msg.header.stamp = msg.header.stamp
        tf_msg.header.frame_id = 'odom'
        tf_msg.child_frame_id = 'base_link'

        tf_msg.transform.translation.x = msg.pose.pose.position.x
        tf_msg.transform.translation.y = msg.pose.pose.position.y
        tf_msg.transform.translation.z = msg.pose.pose.position.z

        tf_msg.transform.rotation = msg.pose.pose.orientation

        self.tf_broadcaster.sendTransform(tf_msg)


def main(args=None):

    rclpy.init(args=args)

    node = SlamBridgeENUNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()

