*** Settings ***
Documentation       Embedded Python GATT tests. 2 boards are required for these tests.

Resource            common_lib/resources/common.robot
Library             String
Library             DateTime

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        5 minute


*** Variables ***
${SERVER_SCRIPT}=           common_lib${/}scripts${/}BLE_scripts${/}init_server.py
${CLIENT_SCRIPT}=           common_lib${/}scripts${/}BLE_scripts${/}init_client.py

${BLE_ADVERT_NAME}=         C
${RSSI_ERROR}=              -127
${RSSI_DIFF_THRESHOLD}=     10
${CMD_TIMEOUT}=             ${15.0}


*** Tasks ***
Gatt Database Initialise
    [Documentation]    Initialize GATT database on the server. Connect to the server and read the GATT database. Check the custom service and characteristics are present.

    Set Tags    PROD-5400

    User REPL Send Error Not Expected    ${settings_board[1]}    gatt_dict = gatt_client.get_dict()    ${5.0}
    # In order to limit the size of the print, only the test service is requested.
    ${resp}=    User REPL Send    ${settings_board[1]}    print(gatt_dict['Service 1'])
    ${resp}=    Convert To String    ${resp}

    Should Contain    ${resp}    B8D00001-6329-EF96-8A4D-55B376D8B25A
    Should Contain    ${resp}    WriteChar
    Should Contain    ${resp}    B8D00002-6329-EF96-8A4D-55B376D8B25A
    Should Contain    ${resp}    ReadChar
    Should Contain    ${resp}    B8D00003-6329-EF96-8A4D-55B376D8B25A
    Should Contain    ${resp}    NotifyChar
    Should Contain    ${resp}    B8D00004-6329-EF96-8A4D-55B376D8B25A
    Should Contain    ${resp}    IndicateChar

Gatt Database Read
    [Documentation]    Initialize GATT database on the server. Connect to the server and read the GATT database. Set a custom value on the server, read it on the client.

    Set Tags    PROD-5401

    ${resp}=    User REPL Send    ${settings_board[0]}    gatt_server.write("ReadChar", bytes("Hello Client", "utf-8"))
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[1]}    read_val = gatt_client.read("ReadChar")
    ${resp}=    Convert To String    ${resp}

    ${resp}=    User REPL Send    ${settings_board[1]}    print(read_val.decode("utf-8"))
    ${resp}=    Convert To String    ${resp}

    Should Contain    ${resp}    Hello Client

Gatt Database Write
    [Documentation]    Initialize GATT database on the server. Connect to the server and read the GATT database. Set a custom value on the server, read it on the client.

    Set Tags    PROD-5402
    ${resp}=    User REPL Send
    ...    ${settings_board[1]}
    ...    gatt_client.write("WriteChar", bytes("Hello Server", "utf-8"))
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[0]}    print(write_value)
    ${resp}=    Convert To String    ${resp}

    Should Contain    ${resp}    Hello Server

Gatt Database Notify
    [Documentation]    Initialize GATT database on the server. Connect to the server and read the GATT database. Set a custom value on the server, read it on the client.

    Set Tags    PROD-5403
    ${resp}=    User REPL Send    ${settings_board[1]}    gatt_client.set_callbacks(cb_notify, cb_indicate)
    ${resp}=    Convert To String    ${resp}

    ${resp}=    User REPL Send
    ...    ${settings_board[1]}
    ...    gatt_client.enable("NotifyChar", ble.GattClient.CCCD_STATE_NOTIFY)
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[0]}    print(do_notify)
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    True

    ${resp}=    User REPL Send
    ...    ${settings_board[0]}
    ...    gatt_server.notify(connection, "NotifyChar", bytes("Notify Client", "utf-8"))
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[1]}    print(notify_message)
    ${resp}=    Convert To String    ${resp}

    Should Contain    ${resp}    Notify Client

    ${resp}=    User REPL Send
    ...    ${settings_board[1]}
    ...    gatt_client.enable("NotifyChar", ble.GattClient.CCCD_STATE_DISABLE)
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[0]}    print(do_notify)
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    False

Gatt Database Indicate
    [Documentation]    Initialize GATT database on the server. Connect to the server and read the GATT database. Set a custom value on the server, read it on the client.

    Set Tags    PROD-5404

    ${resp}=    User REPL Send    ${settings_board[1]}    gatt_client.set_callbacks(cb_notify, cb_indicate)
    ${resp}=    Convert To String    ${resp}

    ${resp}=    User REPL Send
    ...    ${settings_board[1]}
    ...    gatt_client.enable("IndicateChar", ble.GattClient.CCCD_STATE_INDICATE)
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[0]}    print(do_indicate)
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    True

    ${resp}=    User REPL Send
    ...    ${settings_board[0]}
    ...    gatt_server.indicate(connection, "IndicateChar", bytes("Indicate Client", "utf-8"))
    ${resp}=    Convert To String    ${resp}

    Wait for data

    ${resp}=    User REPL Send    ${settings_board[1]}    print(indicate_message)
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    Indicate Client

    ${resp}=    User REPL Send    ${settings_board[0]}    print(indicate_ack)
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    True


*** Keywords ***
Setup
    # TODO: PROD-7432 Add support for only one board being a client
    ${list1}=    Create List    DUT    BLE    GATT_SERVER
    ${list2}=    Create List    BLE    GATT_CLIENT
    ${desired_properties}=    Create List    ${list1}    ${list2}
    Get Boards    minimum_boards=2    desired_properties=${desired_properties}
    Init Board    ${settings_board[0]}
    Init Board    ${settings_board[1]}

    ${tmp}=    Get Board Addr    ${settings_board[0]}
    Set Global Variable    ${board1_addr}    ${tmp}
    Set Global Variable    ${board1_adv_name}    ${BLE_ADVERT_NAME}${board1_addr}

    ${tmp}=    Get Board Addr    ${settings_board[1]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board2_addr}    ${tmp}
    Set Global Variable    ${board2_adv_name}    ${BLE_ADVERT_NAME}${board1_addr}

    Init Server    ${settings_board[0]}    ${board1_adv_name}
    Init Client    ${settings_board[1]}    ${board1_addr}

Teardown
    De-Init Board    ${settings_board[0]}
    De-Init Board    ${settings_board[1]}
    Sleep    3s

Wait for data
    [Documentation]    Delay to allow previous command to execute and callback to fire.
    ...    If this is not present we can sometimes miss the callback.
    ...
    ...    This latency is dependent on the BLE connection parameters.
    ...    To make testing more robust, this value should be calculated based on
    ...    the connection parameters.
    ...    This could be dynamically calculated in the future.

    Sleep    0.5

Init Server
    [Arguments]    ${board}    ${adv_name}

    User REPL Send Error Not Expected    ${board}    import canvas_ble as ble
    User REPL Send Error Not Expected    ${board}    required_name = "${adv_name}"
    User REPL Send Error Not Expected    ${board}    required_phy1 = ble.PHY_1M
    User REPL Send Error Not Expected    ${board}    required_phy2 = ble.PHY_1M
    User REPL Send Error Not Expected    ${board}    required_extended = False
    Run Script on Board Expect Response    ${board}    ${SERVER_SCRIPT}
    User REPL Send Expect True    ${board}    init_server()    ${CMD_TIMEOUT}

Init Client
    [Arguments]    ${board}    ${adv_addr}

    User REPL Send Error Not Expected    ${board}    import canvas_ble as ble
    User REPL Send Error Not Expected    ${board}    required_address = ble.str_to_addr("${adv_addr}")
    User REPL Send Error Not Expected    ${board}    required_phy = ble.PHY_1M
    Run Script on Board Expect Response    ${board}    ${CLIENT_SCRIPT}
    User REPL Send Expect True    ${board}    init_client()    ${CMD_TIMEOUT}
