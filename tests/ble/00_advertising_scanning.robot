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
${SCAN_SCRIPT_START_RESP}=          scan object available
${BLE_ADVERT_NAME}=                 C
${NAME_FILTER}=                     0
${ADDRESS_FILTER}=                  2
${RSSI_THRESHOLD}=                  -70
${SCAN_DATA}=                       [0x77, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]
${SCAN_BYTES}=                      \\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07
${SCAN_TIMOUT_SECONDS}=             ${20}
${SCAN_CMD_TIMOUT_SECONDS}=         ${21}


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
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    True
    ...    True
    ...    False
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${19}

BLE AdScan 1M Phy Legacy Non Connectible Scannable Passive Scan
    [Documentation]    DUT1 Advertises a legacy non connectible scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2458

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    False
    ...    True
    ...    False
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${18}

BLE AdScan 1M Phy Legacy Non Connectible Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises a legacy non connectible non scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2464

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    False
    ...    False
    ...    False
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${16}

BLE AdScan 1M Phy Extended Connectible Non Scannable Active Scan
    [Documentation]    DUT1 Advertises a legacy connectible non scannable advert using the 1M PHY
    ...    DUT2 Scans using the 1M PHY actively

    Set Tags    PROD-2463

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    1
    Check Scan Result    ${settings_board[1]}    ${33}

# **********************************************************************
# *
# * 125k Phy tests
# *
# **********************************************************************

BLE AdScan 125k Coded Phy Extended Non Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 125K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2462

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${32}

BLE Ad 1M Non Connectable Non Scannable Coded Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 1M PHY
    ...    DUT2 Scans using the coded PHY passively. The scanner should not find the advert.

    Set Tags    PROD-6133

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    ...    ${False}

BLE Ad 125k Non Connectable Non Scannable 1M Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 125k PHY
    ...    DUT2 Scans using the 1M PHY passively. The scanner should not find the advert.

    Set Tags    PROD-6134

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    ...    ${False}

BLE Ad 500k Non Connectable Non Scannable 1M Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 500k PHY
    ...    DUT2 Scans using the 1M PHY passively. The scanner should not find the advert.

    Set Tags    PROD-6135

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    ...    ${False}

BLE AdScan 125k Coded Phy Extended Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 125K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2461

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${33}

BLE AdScan 125k Coded Phy Extended Connectable Non Scannable Active Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 125K PHY
    ...    DUT2 Scans using the coded PHY actively

    Set Tags    PROD-2442

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_125K
    ...    ble.PHY_125K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    1
    Check Scan Result    ${settings_board[1]}    ${33}

# **********************************************************************
# *
# * 500k Phy tests
# *
# **********************************************************************

BLE AdScan 500k Coded Phy Extended Non Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended non connectible non scannable advert using the 500K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2440

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${32}

BLE AdScan 500k Coded Phy Extended Connectable Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 500K PHY
    ...    DUT2 Scans using the coded PHY passively

    Set Tags    PROD-2437

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${33}

BLE AdScan 500k Coded Phy Extended Connectable Non Scannable Active Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 500K PHY
    ...    DUT2 Scans using the coded PHY Actively

    Set Tags    PROD-2436

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_500K
    ...    ble.PHY_500K
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_CODED
    ...    ble.PHY_CODED
    ...    250
    ...    60
    ...    1
    Check Scan Result    ${settings_board[1]}    ${33}

# **********************************************************************
# *
# * 1M / 2M Phy tests
# *
# **********************************************************************

BLE AdScan 1M 2M Phy Extended Non Connectible Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended Non connectible non scannable advert using the 1M & 2M PHYs
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2434

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_2M
    ...    False
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${32}

BLE AdScan 1M 2M Phy Extended Connectible Non Scannable Passive Scan
    [Documentation]    DUT1 Advertises an Extended connectible non scannable advert using the 1M & 2M PHYs
    ...    DUT2 Scans using the 1M PHY passively

    Set Tags    PROD-2433

    Start Advertising
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_2M
    ...    True
    ...    False
    ...    True
    ...    240
    ...    250
    Scan With Filter
    ...    ${settings_board[1]}
    ...    ${board1_adv_name}
    ...    ${NAME_FILTER}
    ...    ble.PHY_1M
    ...    ble.PHY_2M
    ...    250
    ...    60
    ...    0
    Check Scan Result    ${settings_board[1]}    ${33}

# **********************************************************************
# *
# * 1M Legacy scan data
# *
# **********************************************************************

BLE AdScan 1M Phy Legacy Connectible Scannable Active Scan With Scan Response Data
    [Documentation]    DUT1 Advertises a legacy connectible scannable advert using the 1M PHY Scannable data is available
    ...    DUT2 Scans using custom scanner to catch the scan data response

    Set Tags    PROD-2439

    Start Scannable Advert
    ...    ${settings_board[0]}
    ...    ${board1_adv_name}
    ...    ble.PHY_1M
    ...    ble.PHY_1M
    ...    True
    ...    True
    ...    False
    ...    240
    ...    250
    Scan For Scan Response    ${settings_board[1]}    ${board1_adv_name}

    # Lyra 24 does not include some type information in type field
    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${expected_type}=    Set Variable    ${24}
    ELSE
        ${expected_type}=    Set Variable    ${27}
    END
    Check Scan Result     ${settings_board[1]}    ${expected_type}    ${True}


*** Keywords ***
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
    Set Global Variable    ${board2_adv_name}    ${BLE_ADVERT_NAME}${board1_addr}

    ${tmp}=    Get Board Type    ${settings_board[0]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}

    ${tmp}=    Get Board Type    ${settings_board[1]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board2_type}    ${tmp}

Teardown
    De-Init Board    ${settings_board[0]}
    De-Init Board    ${settings_board[1]}

Advert and Scan Test Teardown
    Board Soft Reboot    ${settings_board[0]}
    Board Soft Reboot    ${settings_board[1]}

Start Advertising
    [Arguments]
    ...    ${board}
    ...    ${board_adv_name}
    ...    ${phy1}
    ...    ${phy2}
    ...    ${connectible}
    ...    ${scannable}
    ...    ${extended}
    ...    ${min_interval}
    ...    ${max_interval}

    Run Advertising Script on Board    ${board}
    Switch Board to Raw REPL    ${board}
    Raw REPL Exec NoRet    ${board}    advert.add_tag_string(9, "${board_adv_name}", False)
    Raw REPL Exec NoRet    ${board}    advert.set_phys(${phy1}, ${phy2})
    Raw REPL Exec NoRet    ${board}    advert.set_properties(${connectible}, ${scannable}, ${extended})
    Raw REPL Exec NoRet    ${board}    advert.set_interval(${min_interval}, ${max_interval})
    Raw REPL Exec NoRet    ${board}    advert.start()
    Switch Board to User REPL    ${board}

Start Scannable Advert
    [Arguments]
    ...    ${board}
    ...    ${board_adv_name}
    ...    ${phy1}
    ...    ${phy2}
    ...    ${connectible}
    ...    ${scannable}
    ...    ${extended}
    ...    ${min_interval}
    ...    ${max_interval}

    Run Advertising Script on Board    ${board}
    Switch Board to Raw REPL    ${board}
    Raw REPL Exec NoRet    ${board}    advert.add_tag_string(9, "${board_adv_name}", False)
    Raw REPL Exec NoRet    ${board}    advert.add_ltv(255, bytes(${SCAN_DATA}), True)
    Raw REPL Exec NoRet    ${board}    advert.set_phys(${phy1}, ${phy2})
    Raw REPL Exec NoRet    ${board}    advert.set_properties(${connectible}, ${scannable}, ${extended})
    Raw REPL Exec NoRet    ${board}    advert.set_interval(${min_interval}, ${max_interval})
    Raw REPL Exec NoRet    ${board}    advert.start()
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
    ...    ${expect_device}=True
    
    Run Scan Script on Board    ${board}

    IF    ${filter_type} == ${NAME_FILTER}
        User REPL Send Error Not Expected    ${board}    set_scan_filter_name("${filter}")
    ELSE IF    ${filter_type} == ${ADDRESS_FILTER}
        User REPL Send Error Not Expected    ${board}    set_scan_filter_address("${filter}")
    ELSE
        Fail    Unknown scan filter type requested: ${filter_type}
    END

    User REPL Send NoRet    ${board}    scanner.set_phys(${phy1} | ${phy2})
    User REPL Send NoRet    ${board}    scanner.set_timing(${interval}, ${window})
    ${found}=    User REPL Send    ${board}    do_scan(${SCAN_TIMOUT_SECONDS}, ${active})    ${SCAN_CMD_TIMOUT_SECONDS}

    IF    ${expect_device}
        IF    ${found} == False    Fail    Failed to find Advert
    ELSE
        IF    ${found} == True    Fail    Should not have found Advert
    END

Scan For Scan Response
    [Arguments]    ${board}    ${filter}

    Run Scan Script on Board    ${board}

    ${found}=    User REPL Send    ${board}    do_scan_reponse_test(${SCAN_TIMOUT_SECONDS}, "${filter}")    ${SCAN_CMD_TIMOUT_SECONDS}

    IF    ${found} == False    Fail    Failed to find Advert

Check Scan Result
    [Arguments]    ${board}    ${type_expected}    ${check_scan_response}=False

    Switch Board to Raw REPL    ${board}
    ${resp}=    Raw REPL Exec    ${board}    print(result_obj.rssi)
    ${rssi}=    Convert To Integer    ${resp}
    ${resp}=    Raw REPL Exec    ${board}    print(result_obj.type)
    ${type}=    Convert To Integer    ${resp}
    ${data}=    Raw REPL Exec    ${board}    print(result_obj.data)
    Switch Board to User REPL    ${board}

    IF    ${type} != ${type_expected}    
        Fail    Advert type did not match expected value.
    END

    IF    ${rssi} < ${RSSI_THRESHOLD}    Fail    Poor RSSI found
    
    IF    ${check_scan_response}
        ${data}    Convert To Bytes    ${data}
        ${SCAN_BYTES}    Convert To Bytes    ${SCAN_BYTES}
        Should Contain    ${data}    ${SCAN_BYTES}
    END

Run Advertising Script on Board
    [Arguments]    ${board}

    Run Script on Board Expect Response    ${board}    ${ADVERTISER_SCRIPT}    ${ADVERTISER_SCRIPT_START_RESP}

Run Scan Script on Board
    [Arguments]    ${board}

    Run Script on Board Expect Response    ${board}    ${SCAN_SCRIPT}    ${SCAN_SCRIPT_START_RESP}
