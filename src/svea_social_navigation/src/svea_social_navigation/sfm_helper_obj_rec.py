#!/usr/bin/env python
import rospy
import numpy as np
from threading import Lock

# Import AgentStates message
from rsu_msgs.msg import StampedObjectPoseArray
from visualization_msgs.msg import Marker, MarkerArray
from tf.transformations import euler_from_quaternion

def load_param(name, value=None):
    if value is None:
        assert rospy.has_param(name), f'Missing parameter "{name}"'
    return rospy.get_param(name, value)

class SFMHelper(object):
    def __init__(self, is_pedsim=True):
        """
        Init method for the SFMHelper class
        """
        # Get pedestrian topic
        self.ped_pos_topic = load_param('~pedestrian_position_topic', '/sensor/objects') 
        # Create subscriber
        self.ped_sub = rospy.Subscriber(self.ped_pos_topic, StampedObjectPoseArray, self.pedestrian_cb)
        # Pedestrian position array
        self.ped_pos = []
        # Marker array publisher for visualization purposes
        self.pub = rospy.Publisher('/sensor/markers', MarkerArray, queue_size=1, latch=True)
        self.r = 0.0
        self.g = 1.0
        self.b = 0.0
        self.ns = 'sensor'
        # Mutex for mutual exclusion over the access on pedestrian_states
        self.mutex = Lock()

    def pedestrian_cb(self, msg):
        """
        Callback method for the pedestrian state subscriber

        :param msg: message
        :type msg: AgentStates
        """
        self.ped_pos = []
        # For every agent in the environment
        for obj in msg.objects:
            if obj.object.label == 'person':
                # Create state array
                state = [obj.pose.pose.position.x, obj.pose.pose.position.y, 0, 0]
                # Updata/insert entry in pedestrian states array 
                self.ped_pos.append(state)
        #print(self.ped_pos)
        self.publish_obstacle_msg()

    def create_marker_array(self):
        """
        Function to create an array of Markers

        :return: array of markers
        :rtype: list[Marker]
        """
        return [Marker()] * np.shape(self.ped_pos)[0]
    
    def create_marker(self, x, y, id):
        """
        Function to create a single marker

        :param x: x position 
        :type x: float
        :param y: y position
        :type y: float
        :param id: id 
        :type id: integer
        :return: marker
        :rtype: Marker
        """
        m = Marker()
        m.header.frame_id = 'map'
        m.header.stamp = rospy.Time.now()
        m.ns = self.ns
        m.id = id
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        m.pose.position.x = x
        m.pose.position.y = y
        m.pose.position.z = 0
        m.pose.orientation.x = 0.0
        m.pose.orientation.y = 0.0
        m.pose.orientation.z = 0.0
        m.pose.orientation.w = 1.0
        m.scale.x = 0.1
        m.scale.y = 0.1
        m.scale.z = 0.1
        m.color.a = 1.0 
        m.color.r = self.r
        m.color.g = self.g
        m.color.b = self.b
        return m
    
    def publish_obstacle_msg(self):
        """
        Method to publish the array of markers
        """
        obstacle_msg = MarkerArray()
        obstacle_msg.markers = self.create_marker_array()
        for i in range(np.shape(self.ped_pos)[0]):
            obstacle_msg.markers[i] = self.create_marker(self.ped_pos[i][0], self.ped_pos[i][1] ,i)
        self.pub.publish(obstacle_msg)
        
    
if __name__ == '__main__':
    rospy.init_node('test')
    sfm = SFMHelper()
    rospy.spin()
