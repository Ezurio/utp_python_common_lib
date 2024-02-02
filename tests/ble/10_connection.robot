*** Settings ***
Documentation       Embedded Python BLE Peripheral and Central Connection tests.

Resource            common_lib/resources/common.robot
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Setup          Test Setup
Test Timeout        10 minutes


*** Variables ***
${PERIPHERAL_SCRIPT}=                       common_lib${/}scripts${/}BLE_scripts${/}peripheral.py
${PERIPHERAL_SCRIPT_START_RESP}=            advert started

${CENTRAL_SCAN_SCRIPT}=                     common_lib${/}scripts${/}BLE_scripts${/}central_scan.py
${CENTRAL_SCAN_SCRIPT_START_RESP}=          central scan started
${CENTRAL_CONNECT_SCRIPT}=                  common_lib${/}scripts${/}BLE_scripts${/}central_connect.py
${CENTRAL_CONNECT_SCRIPT_START_RESP}=       connection started

${BLE_ADVERT_NAME}=                         C
${RSSI_ERROR}=                              -127
${RSSI_DIFF_THRESHOLD}=                     20


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

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_1M
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board2}    ${settings_board1}

BLE Single Connection Legacy 1M PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises a legacy connectible advert using the 1M PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2451

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_1M
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board1}    ${settings_board2}

BLE Single Connection Extended 125K PHY Central Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 125K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2450

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_125K
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board2}    ${settings_board1}

BLE Single Connection Extended 125K PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 125K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2449

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_125K
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board1}    ${settings_board2}

BLE Single Connection Extended 500K PHY Central Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 500K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2456

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_500K
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board2}    ${settings_board1}

BLE Single Connection Extended 500K PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 500K PHY as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2455

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_500K
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_CODED
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board1}    ${settings_board2}

BLE Single Connection Extended 2M PHY Central Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 1M and 2M PHYs as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Central Disconnects

    Set Tags    PROD-2454

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_2M
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board2}    ${settings_board1}

BLE Single Connection Extended 2M PHY Peripheral Disconnect
    [Documentation]    DUT1 Advertises an extended connectible advert using the 1M and 2M PHYs as peripheral
    ...    DUT2 Scans and connects to DUT1 as central
    ...    RSSI is read from both devices
    ...    Peripheral Disconnects

    Set Tags    PROD-2453

    Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_2M
    Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_1M
    Check Connection    ${settings_board1}    ${settings_board2}
    Disconnect    ${settings_board1}    ${settings_board2}

BLE Single Connection Legacy 1M PHY Stress
    [Documentation]    Repeated connect and disconnect with peripheral and central swapping between DUT1 and DUT2

    Set Tags    PROD-2457

    ${loops_remaining}=    Set Variable    ${10}

    WHILE    ${loops_remaining} > ${0}
        Start Peripheral    ${settings_board1}    ${board1_adv_name}    ble.PHY_1M
        Connect Central    ${settings_board2}    ${board1_adv_name}    ble.PHY_1M
        Check Connection    ${settings_board1}    ${settings_board2}
        Disconnect    ${settings_board2}    ${settings_board1}
        ${resp}=    User REPL Send    ${settings_board1}    advert.stop()

        Test Setup
        Start Peripheral    ${settings_board2}    ${board2_adv_name}    ble.PHY_1M
        Connect Central    ${settings_board1}    ${board2_adv_name}    ble.PHY_1M
        Check Connection    ${settings_board2}    ${settings_board1}
        Disconnect    ${settings_board1}    ${settings_board2}
        ${resp}=    User REPL Send    ${settings_board2}    advert.stop()

        Test Setup
        ${loops_remaining}=    Evaluate    ${loops_remaining} - 1
        Log To Console    Loops remaining: ${loops_remaining}
    END


*** Keywords ***
Start Peripheral
    [Arguments]    ${primary_board}    ${board_adv_name}    ${phy}

    ${resp}=    User REPL Send    ${primary_board}    required_name = "${board_adv_name}"
    ${resp}=    User REPL Send    ${primary_board}    required_phy = ${phy}
    ${resp}=    Run Script on Board    ${primary_board}    ${PERIPHERAL_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${PERIPHERAL_SCRIPT_START_RESP}

Connect Central
    [Arguments]    ${primary_board}    ${board_adv_name}    ${phy}

    ${resp}=    User REPL Send    ${primary_board}    required_filter_name = "${board_adv_name}"
    ${resp}=    User REPL Send    ${primary_board}    required_phy = ${phy}
    ${resp}=    Run Script on Board    ${primary_board}    ${CENTRAL_SCAN_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${CENTRAL_SCAN_SCRIPT_START_RESP}

    ${total_time}=    Set Variable    ${20}
    ${result}=    Set Variable    ${False}
    WHILE    $total_time > ${0}
        ${resp1}=    User REPL Send    ${primary_board}    print(found)
        ${resp1}=    Convert To String    ${resp1}
        ${resp1}=    Replace String    ${resp1}    \r\n    ${EMPTY}
        IF    ${resp1} == True
            ${result}=    Set Variable    ${True}
            BREAK
        ELSE
            Sleep    1s
            ${total_time}=    Evaluate    ${total_time} - 1
        END
    END
    IF    ${result} == False    Fail    Failed to connect

    ${resp}=    Run Script on Board    ${primary_board}    ${CENTRAL_CONNECT_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${CENTRAL_CONNECT_SCRIPT_START_RESP}

Check Connection
    [Arguments]    ${primary_board}    ${secondary_board}

    ${total_time}=    Set Variable    ${20}
    ${result}=    Set Variable    ${False}

    WHILE    $total_time > ${0}
        ${resp1}=    User REPL Send    ${primary_board}    print(current_state)
        ${resp2}=    User REPL Send    ${secondary_board}    print(current_state)
        ${resp1}=    Convert To String    ${resp1}
        ${resp2}=    Convert To String    ${resp2}
        ${resp1}=    Replace String    ${resp1}    \r\n    ${EMPTY}
        ${resp2}=    Replace String    ${resp2}    \r\n    ${EMPTY}
        IF    ${resp1} == 1 and ${resp2} == 1
            ${result}=    Set Variable    ${True}
            BREAK
        ELSE
            Sleep    1s
            ${total_time}=    Evaluate    ${total_time} - 1
        END
    END

    IF    ${result} == False    Fail    Failed to connect

    ${resp1}=    User REPL Send    ${primary_board}    print(connection.get_rssi())
    ${resp2}=    User REPL Send    ${secondary_board}    print(connection.get_rssi())

    IF    ${resp1} == ${RSSI_ERROR}    Fail    RSSI 1 not read correctly

    IF    ${resp2} == ${RSSI_ERROR}    Fail    RSSI 2 not read correctly

    ${diff}=    Evaluate    abs(${resp1} - ${resp2})
    IF    ${diff} > ${RSSI_DIFF_THRESHOLD}
        Fail    RSSI difference between DUTs too great
    END

Disconnect
    [Arguments]    ${primary_board}    ${secondary_board}
    ${resp1}=    User REPL Send    ${primary_board}    connection.disconnect()

    ${total_time}=    Set Variable    ${20}
    ${result}=    Set Variable    ${False}

    WHILE    $total_time > ${0}
        ${resp1}=    User REPL Send    ${primary_board}    print(current_state)
        ${resp2}=    User REPL Send    ${secondary_board}    print(current_state)
        ${resp1}=    Convert To String    ${resp1}
        ${resp2}=    Convert To String    ${resp2}
        ${resp1}=    Replace String    ${resp1}    \r\n    ${EMPTY}
        ${resp2}=    Replace String    ${resp2}    \r\n    ${EMPTY}
        IF    ${resp1} == 2 and ${resp2} == 2
            ${result}=    Set Variable    ${True}
            BREAK
        ELSE
            Sleep    1s
            ${total_time}=    Evaluate    ${total_time} - 1
        END
    END

    IF    ${result} == False    Fail    Failed to disconnect

Setup
    Get Boards
    Init Board    ${settings_board1}
    Init Board    ${settings_board2}

    ${tmp}=    Get Board Addr    ${settings_board1}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_addr}    ${tmp}
    Set Global Variable    ${board1_adv_name}    ${BLE_ADVERT_NAME}${board1_addr}

    ${tmp}=    Get Board Addr    ${settings_board2}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board2_addr}    ${tmp}
    Set Global Variable    ${board2_adv_name}    ${BLE_ADVERT_NAME}${board1_addr}

    ${tmp}=    Get Board Type    ${settings_board1}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}

    ${tmp}=    Get Board Type    ${settings_board2}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board2_type}    ${tmp}

Teardown
    De-Init Board    ${settings_board1}
    De-Init Board    ${settings_board2}

Test Setup
    ${resp}=    Board Soft Reboot    ${settings_board1}
    ${resp}=    Board Soft Reboot    ${settings_board2}

    ${resp}=    User REPL Send    ${settings_board1}    import canvas_ble as ble
    ${resp}=    User REPL Send    ${settings_board2}    import canvas_ble as ble
