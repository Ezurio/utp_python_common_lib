import os
from machine import Pin
import time
import gc

MB_PWM_state = 0
MB_RST_state = 0
MB_SCL_state = 0
MB_AN_state = 0
MB_INT_state = 0
MB_SCK_state = 0
MB_SDA_state = 0
MB_CS_state = 0
MB_MISO_state = 0
MB_MOSI_state = 0


def MB_PWM_Callback(v: int):
    global MB_PWM_state
    MB_PWM_state = v
    print("MB_PWM_Callback: " + str(v))


def MB_RST_Callback(v: int):
    global MB_RST_state
    MB_RST_state = v
    print("MB_RST_Callback: " + str(v))


def MB_SCL_Callback(v: int):
    global MB_SCL_state
    MB_SCL_state = v
    print("MB_SCL_Callback: " + str(v))


def MB_AN_Callback(v: int):
    global MB_AN_state
    MB_AN_state = v
    print("MB_AN_Callback: " + str(v))


def MB_INT_Callback(v: int):
    global MB_INT_state
    MB_INT_state = v
    print("MB_INT_Callback: " + str(v))


def MB_SCK_Callback(v: int):
    global MB_SCK_state
    MB_SCK_state = v
    print("MB_SCK_Callback: " + str(v))


def MB_SDA_Callback(v: int):
    global MB_SDA_state
    MB_SDA_state = v
    print("MB_SDA_Callback: " + str(v))


def MB_CS_Callback(v: int):
    global MB_CS_state
    MB_CS_state = v
    print("MB_CS_Callback: " + str(v))


def MB_MISO_Callback(v: int):
    global MB_MISO_state
    MB_MISO_state = v
    print("MB_MISO_Callback: " + str(v))


def MB_MOSI_Callback(v: int):
    global MB_MOSI_state
    MB_MOSI_state = v
    print("MB_MOSI_Callback: " + str(v))


print("gpio ready")
