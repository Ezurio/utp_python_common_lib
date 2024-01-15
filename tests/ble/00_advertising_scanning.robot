*** Settings ***
Documentation       Embedded Python BLE advertising and scanning Tests

Resource            common_lib/resources/common.robot
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Teardown       Advert and Scan Test Teardown
Test Timeout        1 minute


*** Variables ***
${ADVERTISER_SCRIPT}=               common_lib${/}scripts${/}BLE_scripts${/}advertiser.py
${ADVERTISER_SCRIPT_START_RESP}=    advert object available
${SCAN_SCRIPT}=                     common_lib${/}scripts${/}BLE_scripts${/}scan.py
${SCAN_DATA_SCRIPT}=                common_lib${/}scripts${/}BLE_scripts${/}scan_for_scan_data.py
${SCAN_SCRIPT_START_RESP}=          scan object available
${BLE_ADVERT_NAME}=                 C
${NAME_FILTER}=                     0
${ADDRESS_FILTER}=                  2
${RSSI_THRESHOLD}=                  -50
${SCAN_DATA}=                       [0x77, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]
${SCAN_BYTES}=                      \\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07


*** Tasks ***
# **********************************************************************
# *
# * 1M Phy tests
# *
# **********************************************************************
BLE AdScan 1M Phy Legacy Connectible Scannable Passive Scan
    [Documentation]    DUT1 Advertises a legacy connectible scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2459

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    True
    ...    True
    ...    False
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${19}

BLE AdScan 1M Phy Legacy Non Connectible Scannable Passive Scan
    [Documentation]    DUT1 Advertises a legacy non connectible scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2458

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    False
    ...    True
    ...    False
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${18}

BLE AdScan 1M Phy Legacy Non Connectible Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises a legacy non connectible non scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2464

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    False
    ...    False
    ...    False
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${16}

BLE AdScan 1M Phy Extended Connectible Non Scannable Active Scan
    [Documentation]    DUT1 Advertises a legacy connectible non scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY actively

    Set Tags    PROD-2463

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    1
    Check Scan result    ${settings_board2}    ${33}

# **********************************************************************
# *
# * 125k Phy tests
# *
# **********************************************************************

BLE AdScan 125k Coded Phy Extended Non Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 125K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2462

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${32}

BLE AdScan 125k Coded Phy Extended Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 125K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2461

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${33}

BLE AdScan 125k Coded Phy Extended Connectable Non Scannable Active Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 125K PHY
    ...    DUT2 Scans using the coded PHY actively

    Set Tags    PROD-2442

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    1
    Check Scan result    ${settings_board2}    ${33}

# **********************************************************************
# *
# * 500k Phy tests
# *
# **********************************************************************

BLE AdScan 500k Coded Phy Extended Non Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 500K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2440

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${32}

BLE AdScan 500k Coded Phy Extended Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 500K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2437

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${33}

BLE AdScan 500k Coded Phy Extended Connectable Non Scannable Active Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 500K PHY
    ...    DUT2 Scans using the coded PHY Actively

    Set Tags    PROD-2436

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    1
    Check Scan result    ${settings_board2}    ${33}

# **********************************************************************
# *
# * 1M / 2M Phy tests
# *
# **********************************************************************

BLE AdScan 1M 2M Phy Extended Non Connectible Non Scanable Passive Scan
    [Documentation]    DUT1 Advertises an Extended Non connectible non scannable advert using the 1M & 2M PHYs
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2434

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_2M
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${32}

BLE AdScan 1M 2M Phy Extended Connectible Non Scanable Passive Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 1M & 2M PHYs
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2433

    Skip If    condition=${board1_type}==${LYRA_BOARD_TYPE}    msg=Lyra 24 does not support extended scanning

    Start Advertising
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_2M
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board2}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_2M
    ...    250
    ...    60
    ...    0
    Check Scan result    ${settings_board2}    ${33}

# **********************************************************************
# *
# * 1M Legacy scan data
# *
# **********************************************************************

BLE AdScan 1M Phy Legacy Connectible Scannable Active Scan With Scan Data
    [Documentation]    DUT1 Advertises a legacy connectible scannable advert using the 1M PHY Scannable data is available
    ...    DUT2 Scans using custom scanner to catch the scan data response

    Set Tags    PROD-2439

    Start Scannable Advert
    ...    ${settings_board1}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    True
    ...    True
    ...    False
    ...    240
    ...    250
    Scan For Scan Data    ${settings_board2}    ${board1_adv_name}

    # Lyra 24 does not include some type information in type field
    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${expected_type}=    Set Variable    ${24}
    ELSE
        ${expected_type}=    Set Variable    ${27}
    END
    Check Scan Data result    ${settings_board2}    ${expected_type}


*** Keywords ***
Setup
    Get Boards    minimum_boards=2
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

Advert and Scan Test Teardown
    Board Soft Reboot    ${settings_board1}
    Board Soft Reboot    ${settings_board2}

Start Advertising
    [Arguments]
    ...    ${board}
    ...    ${board_adv_name}
    ...    ${phy1}
    ...    ${phy2}
    ...    ${connectible}
    ...    ${scanable}
    ...    ${extended}
    ...    ${min_interval}
    ...    ${max_interval}

    Run Advertising Script on Board    ${board}
    Switch Board to Raw REPL    ${board}
    ${resp}=    Raw REPL Exec    ${board}    advert.add_tag_string(9, "${board_adv_name}", False)
    ${resp}=    Raw REPL Exec    ${board}    advert.set_phys(${phy1}, ${phy2})
    ${resp}=    Raw REPL Exec    ${board}    advert.set_properties(${connectible}, ${scanable}, ${extended})
    ${resp}=    Raw REPL Exec    ${board}    advert.set_interval(${min_interval}, ${max_interval})
    ${resp}=    Raw REPL Exec    ${board}    advert.start()
    Switch Board to User REPL    ${board}

Start Scannable Advert
    [Arguments]
    ...    ${board}
    ...    ${board_adv_name}
    ...    ${phy1}
    ...    ${phy2}
    ...    ${connectible}
    ...    ${scanable}
    ...    ${extended}
    ...    ${min_interval}
    ...    ${max_interval}

    Run Advertising Script on Board    ${board}
    Switch Board to Raw REPL    ${board}
    ${resp}=    Raw REPL Exec    ${board}    advert.add_tag_string(9, "${board_adv_name}", False)
    ${resp}=    Raw REPL Exec    ${board}    advert.add_ltv(255, bytes(${SCAN_DATA}), True)
    ${resp}=    Raw REPL Exec    ${board}    advert.set_phys(${phy1}, ${phy2})
    ${resp}=    Raw REPL Exec    ${board}    advert.set_properties(${connectible}, ${scanable}, ${extended})
    ${resp}=    Raw REPL Exec    ${board}    advert.set_interval(${min_interval}, ${max_interval})
    ${resp}=    Raw REPL Exec    ${board}    advert.start()
    Switch Board to User REPL    ${board}

Scan With Filter
    [Arguments]
    ...    ${board}
    ...    ${filter}
    ...    ${filter_type}
    ...    ${phy1}
    ...    ${phy2}
    ...    ${interval}
    ...    ${window}
    ...    ${active}

    Run Scan Script on Board    ${board}

    IF    ${filter_type} == ${NAME_FILTER}
        ${resp}=    User REPL Send    ${board}    set_scan_filter_name("${filter}")
    ELSE
        IF    ${filter_type} == ${ADDRESS_FILTER}
            ${resp}=    User REPL Send    ${board}    set_scan_filter_address("${filter}")
        ELSE
            Fail    Unknown scan filter type requested: ${filter_type}
        END
    END

    Switch Board to Raw REPL    ${board}
    ${resp}=    Raw REPL Exec    ${board}    scanner.set_phys(${phy1} | ${phy2})
    ${resp}=    Raw REPL Exec    ${board}    scanner.set_timing(${interval}, ${window})
    ${resp}=    Raw REPL Exec    ${board}    scanner.start(${active})

    ${total_time}=    Set Variable    ${20}

    WHILE    $total_time > ${0}
        ${resp}=    Raw REPL Exec    ${board}    print(found)
        ${resp}=    Convert To String    ${resp}
        ${resp}=    Replace String    ${resp}    \r\n    ${EMPTY}
        IF    ${resp} == True    BREAK    ELSE    Sleep    1s
        ${total_time}=    Evaluate    ${total_time} - 1
    END
    ${result}=    Set Variable    ${resp}
    Switch Board to User REPL    ${board}
    IF    ${result} == False    Fail    Failed to find Advert

Scan For Scan Data
    [Arguments]    ${board}    ${filter}

    ${resp}=    User REPL Send    ${board}    filter_name = "${filter}"

    Run Scan Data Script on Board    ${board}

    Switch Board to Raw REPL    ${board}

    ${total_time}=    Set Variable    ${20}

    WHILE    $total_time > ${0}
        ${resp}=    Raw REPL Exec    ${board}    print(found)
        ${resp}=    Convert To String    ${resp}
        ${resp}=    Replace String    ${resp}    \r\n    ${EMPTY}
        IF    ${resp} == True    BREAK    ELSE    Sleep    1s
        ${total_time}=    Evaluate    ${total_time} - 1
    END
    ${result}=    Set Variable    ${resp}
    Switch Board to User REPL    ${board}
    IF    ${result} == False    Fail    Failed to find Advert

Get Scan result
    [Arguments]    ${board}

    Switch Board to Raw REPL    ${board}
    ${resp}=    Raw REPL Exec    ${board}    print(result_obj.rssi)
    ${rssi}=    Convert To Integer    ${resp}
    ${resp}=    Raw REPL Exec    ${board}    print(result_obj.type)
    ${type}=    Convert To Integer    ${resp}
    ${resp}=    Raw REPL Exec    ${board}    print(result_obj.data)
    ${data}=    Convert To Bytes    ${resp}
    ${resp}=    Raw REPL Exec    ${board}    print(result_obj.addr)
    ${addr}=    Convert To Bytes    ${resp}
    Switch Board to User REPL    ${board}
    RETURN    ${rssi}    ${type}    ${data}    ${addr}


Check Scan result
    [Arguments]    ${board}    ${type_expected}

    ${rssi}    ${type}    ${data}    ${addr}=    Get Scan result    ${board}

    IF    ${type} != ${type_expected}
        Fail    Advert type did not match expected value.
    END

    IF    ${rssi} < ${RSSI_THRESHOLD}    Fail    Poor RSSI found

Check Scan Data result
    [Arguments]    ${board}    ${type_expected}

    ${rssi}    ${type}    ${data}    ${addr}=    Get Scan result    ${board}

    IF    ${type} != ${type_expected}
        Fail    Advert type did not match expected value.
    END

    IF    ${rssi} < ${RSSI_THRESHOLD}    Fail    Poor RSSI found

    ${scan_bytes}=    Convert To Bytes    ${SCAN_BYTES}
    Should Contain    ${data}    ${scan_bytes}

Run Advertising Script on Board
    [Arguments]    ${board}

    ${resp}=    Run Script on Board    ${board}    ${ADVERTISER_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${ADVERTISER_SCRIPT_START_RESP}

Run Scan Script on Board
    [Arguments]    ${board}

    ${resp}=    Run Script on Board    ${board}    ${SCAN_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${SCAN_SCRIPT_START_RESP}

Run Scan Data Script on Board
    [Arguments]    ${board}

    ${resp}=    Run Script on Board    ${board}    ${SCAN_DATA_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${SCAN_SCRIPT_START_RESP}
