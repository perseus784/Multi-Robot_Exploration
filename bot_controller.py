from controller import Robot, DistanceSensor, Motor, Node
import cv2
import numpy as np
import random
import matplotlib.pyplot as plt
import requests 
# time in [ms] of a simulation step
TIME_STEP = 64

MAX_SPEED = 6.28

# create the Robot instance.
robot = Robot()
# initialize devices
ps = []
psNames = [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
]

for i in range(8):
    ps.append(robot.getDistanceSensor(psNames[i]))
    ps[i].enable(TIME_STEP)

camera = robot.getCamera('camera')
accelerometer = robot.getAccelerometer('accelerometer')
camera.enable(4*TIME_STEP)
accelerometer.enable(4*TIME_STEP)
# print(dir(accelerometer))
leftMotor = robot.getMotor('left wheel motor')
rightMotor = robot.getMotor('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)
name = str(random.random())
  
URL = "http://127.0.0.1:5000/"

def update_info(name, radius,speed):
    PARAMS = {'name':name,'radius':radius,'speed':speed}
    r = requests.get(url = URL+'update', params = PARAMS) 
    print(r.json())
    
def retrieve_info():
    r = requests.get(url = URL+'retrieve')
    print(r.json())

def find_object(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (36, 25, 25), (70, 255,255))
    ret,thresh = cv2.threshold(mask,127,255,1)
    contours,h = cv2.findContours(thresh,1,2)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
        if len(approx) > 15:
            (x,y),radius = cv2.minEnclosingCircle(cnt)
            center = (int(x),int(y))
            radius = int(radius)
            cv2.circle(image,center,radius,(255,0,0),4)
            return (True, radius)
    
    return (False,0)


# feedback loop: step simulation until receiving an exit event
while robot.step(TIME_STEP) != -1:
    image = camera.getImageArray()
    if image:
        my_img = np.array(image,dtype=np.uint8)
        cv2.imshow(name,my_img)
        message,radius = find_object(my_img)
        if message:
            update_info(name,radius,accelerometer.getValues())
        cv2.waitKey(1)
    # read sensors outputs
    psValues = []
    for i in range(8):
        psValues.append(ps[i].getValue())

    # detect obstacles
    right_obstacle = psValues[0] > 80.0 or psValues[1] > 80.0 or psValues[2] > 80.0
    left_obstacle = psValues[5] > 80.0 or psValues[6] > 80.0 or psValues[7] > 80.0

    # initialize motor speeds at 50% of MAX_SPEED.
    leftSpeed  = 0.5 * MAX_SPEED
    rightSpeed = 0.5 * MAX_SPEED
    # modify speeds according to obstacles
    if left_obstacle:
        # turn right
        leftSpeed  = 0.5 * MAX_SPEED
        rightSpeed = -0.5 * MAX_SPEED
    elif right_obstacle:
        # turn left
        leftSpeed  = -0.5 * MAX_SPEED
        rightSpeed = 0.5 * MAX_SPEED
    # write actuators inputs
    leftMotor.setVelocity(leftSpeed)
    rightMotor.setVelocity(rightSpeed)
    

