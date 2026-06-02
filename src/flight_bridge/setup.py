import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'flight_bridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aditya',
    maintainer_email='aditya@todo.todo',
    description='Flight Controller Bridge for PX4 to ROS 2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hz_tracker = flight_bridge.hz_tracker:main',
            'failsafe = flight_bridge.failsafe:main',
            'bridge_node_enu = flight_bridge.bridge_node_enu:main',
            'bridge_node_ned = flight_bridge.bridge_node_ned:main',
            'fix_euroc = flight_bridge.fix_euroc:main',
            'gps_spoofer = flight_bridge.gps_spoofer:main'
        ],
    },
)
