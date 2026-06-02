#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped

from tf2_ros import TransformBroadcaster

from tf_transformations import quaternion_matrix
from tf_transformations import quaternion_from_matrix


class SlamBridgeNode(Node):

    def __init__(self):
        super().__init__('slam_bridge_node')

        # Subscriber to RTAB-Map odometry
        self.subscription = self.create_subscription(
            Odometry,
            '/rtabmap/odom',
            self.odom_callback,
            10
        )

        # Publisher for filtered odometry
        self.filtered_pub = self.create_publisher(
            Odometry,
            '/filtered_odom',
            10
        )

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        self.get_logger().info('SLAM Bridge Node Started')

    def enu_to_ned_position(self, x_enu, y_enu, z_enu):
        """
        ENU → NED conversion

        ENU:
            x east
            y north
            z up

        NED:
            x north
            y east
            z down
        """

        x_ned = y_enu
        y_ned = x_enu
        z_ned = -z_enu

        return x_ned, y_ned, z_ned

    def enu_to_ned_quaternion(self, qx, qy, qz, qw):
        """
        Convert quaternion orientation from ENU to NED.
        """

        # Quaternion to rotation matrix
        q = [qx, qy, qz, qw]
        R_enu = quaternion_matrix(q)

        # ENU → NED transform matrix
        T = [
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ]

        import numpy as np

        T = np.array(T)
        R_enu = np.array(R_enu)

        # Rotate frame
        R_ned = T @ R_enu @ T.T

        q_ned = quaternion_from_matrix(R_ned)

        return q_ned

    def odom_callback(self, msg):

        filtered_msg = Odometry()

        # Preserve timestamp
        filtered_msg.header.stamp = msg.header.stamp

        # Frame conventions
        filtered_msg.header.frame_id = 'odom'
        filtered_msg.child_frame_id = 'base_link'

        # =========================
        # POSITION CONVERSION
        # =========================

        x_enu = msg.pose.pose.position.x
        y_enu = msg.pose.pose.position.y
        z_enu = msg.pose.pose.position.z

        x_ned, y_ned, z_ned = self.enu_to_ned_position(
            x_enu,
            y_enu,
            z_enu
        )

        filtered_msg.pose.pose.position.x = x_ned
        filtered_msg.pose.pose.position.y = y_ned
        filtered_msg.pose.pose.position.z = z_ned

        # =========================
        # ORIENTATION CONVERSION
        # =========================

        qx = msg.pose.pose.orientation.x
        qy = msg.pose.pose.orientation.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        q_ned = self.enu_to_ned_quaternion(qx, qy, qz, qw)

        filtered_msg.pose.pose.orientation.x = q_ned[0]
        filtered_msg.pose.pose.orientation.y = q_ned[1]
        filtered_msg.pose.pose.orientation.z = q_ned[2]
        filtered_msg.pose.pose.orientation.w = q_ned[3]

        # =========================
        # VELOCITY CONVERSION
        # =========================

        vx_enu = msg.twist.twist.linear.x
        vy_enu = msg.twist.twist.linear.y
        vz_enu = msg.twist.twist.linear.z

        vx_ned, vy_ned, vz_ned = self.enu_to_ned_position(
            vx_enu,
            vy_enu,
            vz_enu
        )

        filtered_msg.twist.twist.linear.x = vx_ned
        filtered_msg.twist.twist.linear.y = vy_ned
        filtered_msg.twist.twist.linear.z = vz_ned

        # Preserve angular velocity
        filtered_msg.twist.twist.angular = msg.twist.twist.angular

        # =========================
        # COVARIANCE
        # =========================

        filtered_msg.pose.covariance = msg.pose.covariance
        filtered_msg.twist.covariance = msg.twist.covariance

        # Publish filtered odometry
        self.filtered_pub.publish(filtered_msg)

        # =========================
        # TF BROADCAST
        # =========================

        tf_msg = TransformStamped()

        tf_msg.header.stamp = msg.header.stamp
        tf_msg.header.frame_id = 'odom'
        tf_msg.child_frame_id = 'base_link'

        tf_msg.transform.translation.x = x_ned
        tf_msg.transform.translation.y = y_ned
        tf_msg.transform.translation.z = z_ned

        tf_msg.transform.rotation = filtered_msg.pose.pose.orientation

        self.tf_broadcaster.sendTransform(tf_msg)


def main(args=None):

    rclpy.init(args=args)

    node = SlamBridgeNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
