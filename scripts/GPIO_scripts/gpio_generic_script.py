import os
from machine import Pin
import time
import gc

MB_PWM_state = 0
MB_RX_state = 0
MB_SCL_state = 0
MB_AN_state = 0
MB_INT_state = 0
MB_TX_state = 0
MB_SDA_state = 0
MB_CS_state = 0
MB_MISO_state = 0
MB_MOSI_state = 0

GPIO1_state = 0
GPIO2_state = 0
GPIO3_state = 0
GPIO4_state = 0
GPIO5_state = 0
GPIO6_state = 0
GPIO7_state = 0
GPIO8_state = 0

# Lyra Callback definitions
def MB_PWM_Callback(v:int):
    global MB_PWM_state
    MB_PWM_state = v
    print("MB_PWM_Callback: " + str(v))


def MB_RX_Callback(v:int):
    global MB_RX_state
    MB_RX_state = v
    print("MB_RX_Callback: " + str(v))


def MB_SCL_Callback(v:int):
    global MB_SCL_state
    MB_SCL_state = v
    print("MB_SCL_Callback: " + str(v))


def MB_AN_Callback(v:int):
    global MB_AN_state
    MB_AN_state = v
    print("MB_AN_Callback: " + str(v))


def MB_INT_Callback(v:int):
    global MB_INT_state
    MB_INT_state = v
    print("MB_INT_Callback: " + str(v))


def MB_TX_Callback(v:int):
    global MB_TX_state
    MB_TX_state = v
    print("MB_TX_Callback: " + str(v))


def MB_SDA_Callback(v:int):
    global MB_SDA_state
    MB_SDA_state = v
    print("MB_SDA_Callback: " + str(v))


def MB_CS_Callback(v:int):
    global MB_CS_state
    MB_CS_state = v
    print("MB_CS_Callback: " + str(v))


def MB_MISO_Callback(v:int):
    global MB_MISO_state
    MB_MISO_state = v
    print("MB_MISO_Callback: " + str(v))


def MB_MOSI_Callback(v:int):
    global MB_MOSI_state
    MB_MOSI_state = v
    print("MB_MOSI_Callback: " + str(v))

# Zephyr Callback definitions
def GPIO1_Callback(v:int):
    global GPIO1_state
    GPIO1_state = v
    print("GPIO1_Callback: " + str(v))


def GPIO2_Callback(v:int):
    global GPIO2_state
    GPIO2_state = v
    print("GPIO2_Callback: " + str(v))


def GPIO3_Callback(v:int):
    global GPIO3_state
    GPIO3_state = v
    print("GPIO3_Callback: " + str(v))


def GPIO4_Callback(v:int):
    global GPIO4_state
    GPIO4_state = v
    print("GPIO4_Callback: " + str(v))


def GPIO5_Callback(v:int):
    global GPIO5_state
    GPIO5_state = v
    print("GPIO5_Callback: " + str(v))


def GPIO6_Callback(v:int):
    global GPIO6_state
    GPIO6_state = v
    print("GPIO6_Callback: " + str(v))


def GPIO7_Callback(v:int):
    global GPIO7_state
    GPIO7_state = v
    print("GPIO7_Callback: " + str(v))


def GPIO8_Callback(v:int):
    global GPIO8_state
    GPIO8_state = v
    print("GPIO8_Callback: " + str(v))


def No_Callback(v:int):
    print("No_Callback")

print ("gpio ready")

