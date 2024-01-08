*** Settings ***
Documentation       Embedded Python Zephyr Board Tests. Only one Zephyr based DUT board is required for all tests.

Resource            common_lib/resources/common.robot

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        1 minute


*** Tasks ***
Python in Thread
    Set Tags    VAS-247

    ${resp}=    Zephyr Shell Send    ${settings_board1}    kernel threads
    Should Contain    ${resp}    micropython
    ${resp}=    Zephyr Shell Send    ${settings_board1}    kernel version
    Should Contain    ${resp}    Zephyr version


*** Keywords ***
Setup
    Get Boards    allow_list=['SeraNX040Dvk']
    Init Board    ${settings_board1}

Teardown
    De-Init Board    ${settings_board1}
