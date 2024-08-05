*** Settings ***
Documentation       Embedded Python BLE Peripheral and Central Connection tests.

Resource            common_lib/resources/common.robot
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Setup          Test Setup
Test Timeout        10 minutes


*** Variables ***
${PERIPHERAL_SCRIPT}=               common_lib${/}scripts${/}BLE_scripts${/}peripheral.py
${CENTRAL_SCRIPT}=                  common_lib${/}scripts${/}BLE_scripts${/}central.py

${BLE_ADVERT_NAME}=                 C
${RSSI_ERROR}=                      -127
${RSSI_DIFF_THRESHOLD}=             20

${SCAN_TIMOUT_SECONDS}=             ${20}
${SCAN_CMD_TIMOUT_SECONDS}=         ${21}
${CONNECTION_TIMOUT_SECONDS}=       ${20}


*** Tasks ***
# **********************************************************************
# *
# * 1M Phy tests
# *
# **********************************************************************
BLE Single Connection Legacy 1M PHY Central Disconnect
    [Documentation]    DUT1 Advertises a legacy connectible advert using the 1M PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2452

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_1M
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[1]}    ${settings_board[0]}

BLE Single Connection Legacy 1M PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises a legacy connectible advert using the 1M PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2451

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_1M
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[0]}    ${settings_board[1]}

BLE Single Connection Extended 125K PHY Central Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 125K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2450

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_125K
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[1]}    ${settings_board[0]}

BLE Single Connection Extended 125K PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 125K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2449

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_125K
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[0]}    ${settings_board[1]}

BLE Single Connection Extended 500K PHY Central Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 500K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2456

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_500K
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[1]}    ${settings_board[0]}

BLE Single Connection Extended 500K PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 500K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2455

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_500K
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[0]}    ${settings_board[1]}

BLE Single Connection Extended 2M PHY Central Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 1M and 2M PHYs as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2454

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_2M
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[1]}    ${settings_board[0]}

BLE Single Connection Extended 2M PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 1M and 2M PHYs as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2453

    Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_2M
    Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board[0]}    ${settings_board[1]}
    Disconnect    ${settings_board[0]}    ${settings_board[1]}

BLE Single Connection Legacy 1M PHY Stress
    [Documentation]    Repeated connect and disconnect with peripheral and central swapping between DUT1 and DUT2

    Set Tags    PROD-2457

    ${loops_remaining}=    Set Variable    ${10}

    WHILE    ${loops_remaining} > ${0}
        Start Peripheral    ${settings_board[0]}    ${board1_adv_name}    ble.PHY_1M
        Connect Central    ${settings_board[1]}    ${board1_adv_name}    ble.PHY_1M
        Check Connection    ${settings_board[0]}    ${settings_board[1]}
        Disconnect    ${settings_board[1]}    ${settings_board[0]}
        ${resp}=    User REPL Send    ${settings_board[0]}    advert.stop()

        Test Setup
        Start Peripheral    ${settings_board[1]}    ${board2_adv_name}    ble.PHY_1M
        Connect Central    ${settings_board[0]}    ${board2_adv_name}    ble.PHY_1M
        Check Connection    ${settings_board[1]}    ${settings_board[0]}
        Disconnect    ${settings_board[0]}    ${settings_board[1]}
        ${resp}=    User REPL Send    ${settings_board[1]}    advert.stop()

        Test Setup
        ${loops_remaining}=    Evaluate    ${loops_remaining} - 1
        Log To Console    Loops remaining: ${loops_remaining}
    END


*** Keywords ***
Start Peripheral
    [Arguments]    ${primary_board}    ${board_adv_name}    ${phy}

    Run Script on Board Expect Response    ${primary_board}    ${PERIPHERAL_SCRIPT}
    User REPL Send Expect True    ${primary_board}    init_and_start_advert("${board_adv_name}", ${phy})

Connect Central
    [Arguments]    ${primary_board}    ${board_adv_name}    ${phy}

    Run Script on Board Expect Response    ${primary_board}    ${CENTRAL_SCRIPT}
    User REPL Send Expect True
    ...    ${primary_board}
    ...    scan_for_dut("${board_adv_name}", ${phy}, ${SCAN_TIMOUT_SECONDS})
    ...    ${SCAN_CMD_TIMOUT_SECONDS}
    User REPL Send Expect True    ${primary_board}    request_connection()

Check Connection
    [Arguments]    ${primary_board}    ${secondary_board}

    ${total_time}=    Set Variable    ${CONNECTION_TIMOUT_SECONDS}
    ${result}=    Set Variable    ${False}

    WHILE    $total_time > ${0}
        ${connected1}=    User REPL Send Error Not Expected    ${primary_board}    connected()
        ${connected2}=    User REPL Send Error Not Expected    ${secondary_board}    connected()
        IF    ${connected1} == ${True} and ${connected2} == ${True}
            ${result}=    Set Variable    ${True}
            BREAK
        ELSE
            Sleep    1s
            ${total_time}=    Evaluate    ${total_time} - 1
        END
    END

    IF    ${result} == False    Fail    Failed to connect

    ${resp1}=    User REPL Send Error Not Expected    ${primary_board}    print(connection.get_rssi())
    ${resp2}=    User REPL Send Error Not Expected    ${secondary_board}    print(connection.get_rssi())

    IF    ${resp1} == ${RSSI_ERROR}    Fail    RSSI 1 not read correctly

    IF    ${resp2} == ${RSSI_ERROR}    Fail    RSSI 2 not read correctly

    ${diff}=    Evaluate    abs(${resp1} - ${resp2})
    IF    ${diff} > ${RSSI_DIFF_THRESHOLD}
        Fail    RSSI difference between DUTs too great
    END

Disconnect
    [Arguments]    ${primary_board}    ${secondary_board}
    ${resp1}=    User REPL Send Error Not Expected    ${primary_board}    connection.disconnect()

    ${total_time}=    Set Variable    ${CONNECTION_TIMOUT_SECONDS}
    ${result}=    Set Variable    ${False}

    WHILE    $total_time > ${0}
        ${connected1}=    User REPL Send Error Not Expected    ${primary_board}    connected()
        ${connected2}=    User REPL Send Error Not Expected    ${secondary_board}    connected()
        IF    ${connected1} == ${False} and ${connected2} == ${False}
            ${result}=    Set Variable    ${True}
            BREAK
        ELSE
            Sleep    1s
            ${total_time}=    Evaluate    ${total_time} - 1
        END
    END

    IF    ${result} == False    Fail    Failed to disconnect

Setup
    ${list}=    Create List    DUT    BLE
    ${desired_properties}=    Create List    ${list}    ${list}
    Get Boards    minimum_boards=2    desired_properties=${desired_properties}
    Init Board    ${settings_board[0]}
    Init Board    ${settings_board[1]}

    ${tmp}=    Get Board Addr    ${settings_board[0]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_addr}    ${tmp}
    Set Global Variable    ${board1_adv_name}    ${BLE_ADVERT_NAME}${board1_addr}

    ${tmp}=    Get Board Addr    ${settings_board[1]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board2_addr}    ${tmp}
    Set Global Variable    ${board2_adv_name}    ${BLE_ADVERT_NAME}${board2_addr}

    ${tmp}=    Get Board Type    ${settings_board[0]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}

    ${tmp}=    Get Board Type    ${settings_board[1]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board2_type}    ${tmp}

Teardown
    De-Init Board    ${settings_board[0]}
    De-Init Board    ${settings_board[1]}

Test Setup
    Board Soft Reboot    ${settings_board[0]}
    Board Soft Reboot    ${settings_board[1]}

    User REPL Send Error Not Expected    ${settings_board[0]}    import canvas_ble as ble
    User REPL Send Error Not Expected    ${settings_board[1]}    import canvas_ble as ble
