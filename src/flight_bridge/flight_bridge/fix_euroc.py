import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo

class EurocSyncFix(Node):
    def __init__(self):
        super().__init__('euroc_sync_fix')
        self.sub = self.create_subscription(Image, '/cam0/image_raw', self.image_callback, 10)
        self.left_pub = self.create_publisher(CameraInfo, '/cam0/camera_info', 10)
        self.right_pub = self.create_publisher(CameraInfo, '/cam1/camera_info', 10)

    def image_callback(self, msg):
        info = CameraInfo()
        info.header = msg.header
        info.width = 752
        info.height = 480
        info.k = [458.654, 0.0, 367.215, 0.0, 457.296, 248.375, 0.0, 0.0, 1.0]
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        
        # Publish Left Camera (Baseline = 0)
        info.p = [458.654, 0.0, 367.215, 0.0, 0.0, 457.296, 248.375, 0.0, 0.0, 0.0, 1.0, 0.0]
        self.left_pub.publish(info)
        
        # Publish Right Camera (Baseline Tx = -fx * 0.11m = -50.45)
        info.header.frame_id = 'cam1' 
        info.p = [458.654, 0.0, 367.215, -50.45, 0.0, 457.296, 248.375, 0.0, 0.0, 0.0, 1.0, 0.0]
        self.right_pub.publish(info)

def main(args=None):
    rclpy.init(args=args)
    node = EurocSyncFix()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
