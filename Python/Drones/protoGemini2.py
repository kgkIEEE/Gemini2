import setup_path 
import airsim

import numpy as np
import os
import tempfile
import pprint
import cv2

import string
import random
def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
   return ''.join(random.choice(chars) for x in range(size))

def initDrone():
    # connect to the AirSim simulator
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    return client

def getDroneStats(client):
    state = client.getMultirotorState()
    s = pprint.pformat(state)
    print("state: %s" % s)

    imu_data = client.getImuData()
    s = pprint.pformat(imu_data)
    print("imu_data: %s" % s)

    barometer_data = client.getBarometerData()
    s = pprint.pformat(barometer_data)
    print("barometer_data: %s" % s)

    magnetometer_data = client.getMagnetometerData()
    s = pprint.pformat(magnetometer_data)
    print("magnetometer_data: %s" % s)

    gps_data = client.getGpsData()
    s = pprint.pformat(gps_data)
    print("gps_data: %s" % s)

    state = client.getMultirotorState()
    print("state: %s" % pprint.pformat(state))

def getDroneImages(client):
    # get camera images from the car
    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.DepthVis),  #depth visualization image
        airsim.ImageRequest("1", airsim.ImageType.DepthPerspective, True), #depth in perspective projection
        airsim.ImageRequest("1", airsim.ImageType.Scene), #scene vision image in png format
        airsim.ImageRequest("1", airsim.ImageType.Scene, False, False)])  #scene vision image in uncompressed RGBA array
    print('Retrieved images: %d' % len(responses))

    tmp_dir = os.path.join(tempfile.gettempdir(), "airsim_drone")
    print ("Saving images to %s" % tmp_dir)
    try:
        os.makedirs(tmp_dir)
    except OSError:
        if not os.path.isdir(tmp_dir):
            raise

    for idx, response in enumerate(responses):

        filename = os.path.join(tmp_dir, str(str(idx)+random_generator(4)))

        if response.pixels_as_float:
            print("Type %d, size %d" % (response.image_type, len(response.image_data_float)))
            airsim.write_pfm(os.path.normpath(filename + '.pfm'), airsim.get_pfm_array(response))
        elif response.compress: #png format
            print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            airsim.write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)
        else: #uncompressed array
            print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) # get numpy array
            img_rgb = img1d.reshape(response.height, response.width, 3) # reshape array to 4 channel image array H X W X 3
            cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb) # write to png

            
def releaseDrone(client):
    client.armDisarm(False)
    client.reset()
    # release Drone
    client.enableApiControl(False)


client = initDrone()
getDroneStats(client)
getDroneImages(client)

airsim.wait_key('Press any key to takeoff')
client.takeoffAsync().join()
getDroneStats(client)
getDroneImages(client)

airsim.wait_key('Press any key to move vehicle to (-10, 10, -10) at 5 m/s')
client.moveToPositionAsync(-10, 10, -10, 5).join()
getDroneStats(client)
getDroneImages(client)

client.hoverAsync().join()

getDroneStats(client)
getDroneImages(client)

airsim.wait_key('Press any key to reset to original state')
getDroneStats(client)
getDroneImages(client)

releaseDrone(client)