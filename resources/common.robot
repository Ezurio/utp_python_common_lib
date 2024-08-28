*** Settings ***
Library     Collections
Library     ./common_lib/libraries/discovery.py    WITH NAME    Discovery
Library     String
Library     ./common_lib/libraries/upload_robot_xray.py    WITH NAME    Upload
Library     ./common_lib/libraries/xray_listener.py    WITH NAME    XListen
Library     ./common_lib/libraries/read_board_config.py    WITH NAME    BoardConfig


*** Variables ***
${rack_config}                  ${EMPTY}
${settings_board}               @{EMPTY}
${LYRA_BOARD_TYPE}              'Lyra'
${ZEPHYR_BOARD_TYPE}            'zephyr'
${BLE_ADDR_SCRIPT}              common_lib${/}scripts${/}BLE_scripts${/}get_ble_addr.py
${BLE_ADDR_FAIL_RESP}           Error
${JIRA_PROJECT}                 PROD
${allow_xray_upload}            True
${DEFAULT_RUN_SCRIPT_RESP}      Script Completed Successfully


*** Keywords ***
Is List Empty
    [Arguments]    ${value}
    ${is_empty}=    Run Keyword And Return Status    Should Be Empty    ${value}    strip=${TRUE}
    RETURN    ${is_empty}

Delay for USB Enumeration
    [Arguments]    ${delay}=2s
    Sleep    ${delay}    reason=USB enumeration delay

Get Boards
    [Documentation]
    ...    Get the boards connected to the system.
    ...    If a board configuration file is specified, then it wil override the allow list.
    [Arguments]
    ...    ${allow_many}=${True}
    ...    ${allow_list}=@{EMPTY}
    ...    ${minimum_boards}=1
    ...    ${desired_properties}=@{EMPTY}

    ${boards_conf}=    BoardConfig.Read Board Config    ${rack_config}    ${desired_properties}
    ${boards_config_empty}=    Is List Empty    ${boards_conf}

    Delay for USB Enumeration

    IF    ${boards_config_empty}
        @{boards}=    Discovery.Get Connected Boards    ${allow_list}
    ELSE
        @{boards}=    Discovery.Get Specified Boards    ${boards_conf}
    END

    ${num_boards}=    Get Length    ${boards}
    Log    ${num_boards} boards found!

    IF    ${num_boards} < ${minimum_boards}
        Fail    Minimum number of boards (${minimum_boards}) not found
    END

    IF    ${num_boards} > ${1}
        IF    ${allow_many} == ${False}
            Fail    Please ensure only one board is connected!
        END
    END

    Set Global Variable    ${settings_board}    ${boards}

Init Board
    [Arguments]    ${board}

    IF    ${board.is_initialized} == ${False}
        Call Method    ${board}    open_and_init_board
        IF    ${board.is_initialized} == ${False}    Fail    Board is not ready
    END
    # For all automated testing, upload an empty boot.py to the board to
    # prevent the default script from running.
    Upload Script to Board    ${board}    common_lib/scripts/empty_boot.py    boot.py
    # Remove main.py (if it exists) to prevent it from running.
    Board Delete Script    ${board}    main.py
    Board Reset Module    ${board}
    ${resp}=    Call Method    ${board.python_uart}    send    import os
    ${resp}=    Call Method    ${board.python_uart}    send    import sys

    # Setup the XRay uploader to use the test plan associated with DUT1
    # (This reads the machine name from the board.)
    IF    ${board.is_initialized} == ${True}
        IF    ${allow_xray_upload} == ${True}
            IF    $board==$settings_board[0]    Setup Xray Upload
        END
    END

De-Init Board
    [Arguments]    ${board}
    IF    ${board.is_initialized} == ${True}
        Call Method    ${board}    close_ports_and_reset
    END

Switch Board to Raw REPL
    [Arguments]    ${board}
    Call Method    ${board}    close_repl_uart
    Call Method    ${board}    open_raw_repl_uart

Switch Board to User REPL
    [Arguments]    ${board}

    Call Method    ${board}    close_raw_repl_uart
    Call Method    ${board}    open_repl_uart

Run Script on Board
    [Documentation]    Run a script on the board and return the output. This uses raw REPL.
    ...    Callbacks don't run in Raw REPL mode.
    [Arguments]    ${board}    ${script}

    Switch Board to Raw REPL    ${board}
    ${resp}=    Call Method    ${board.python_raw_repl_uart}    execfile    ${script}
    Switch Board to User REPL    ${board}

    RETURN    ${resp}

Run Script on Board Expect Response
    [Documentation]    Like Run Script on Board but checks for a specific response string.
    [Arguments]    ${board}    ${script}    ${expected_response}=${DEFAULT_RUN_SCRIPT_RESP}

    Switch Board to Raw REPL    ${board}
    ${resp}=    Call Method    ${board.python_raw_repl_uart}    execfile    ${script}
    Switch Board to User REPL    ${board}

    # Convert byte string into text before comparison 
    # (Should be Equals As Strings doesn't do this)
    ${resp_str}=    Convert To String    ${resp}
    Should Contain    ${resp_str}    ${expected_response}    ignore_case=True

Get Board Device ID
    [Documentation]    Get the device ID of the board.
    [Arguments]    ${board}
    ${resp}=    Call Method    ${board.python_uart}    send    import machine
    ${resp}=    Call Method    ${board.python_uart}    send    import binascii
    ${resp}=    Call Method    ${board.python_uart}    send    binascii.hexlify(machine.unique_id()).decode()
    ${id}=    Replace String    ${resp}    '    ${EMPTY}
    RETURN    ${id}

Upload Script to Board
    [Documentation]    Uses raw REPL to upload a script to the board and save it to the file system.
    [Arguments]    ${board}    ${src_script}    ${dst_script}

    Switch Board to Raw REPL    ${board}
    ${resp}=    Call Method    ${board}    upload_py_file    ${src_script}    ${dst_script}
    Switch Board to User REPL    ${board}

User REPL Send
    [Documentation]    Send a command using the board's user REPL interface.
    [Arguments]    ${board}    ${cmd}    ${timeout}=${1.0}

    ${resp}=    Call Method    ${board.python_uart}    send    ${cmd}    ${timeout}

    RETURN    ${resp}

User REPL Send NoRet
    [Documentation]    Send a command using the board's user REPL interface.
    [Arguments]    ${board}    ${cmd}    ${timeout}=${1.0}

    Call Method    ${board.python_uart}    send    ${cmd}    ${timeout}

User REPL Send Error Not Expected
    [Documentation]    Send a command using REPL and check for error string.
    [Arguments]    ${board}    ${cmd}    ${timeout}=${1.0}

    ${check}=    Call Method    ${board.python_uart}    send    ${cmd}    ${timeout}
    Should Not Contain    ${check}    error    ignore_case=True

    RETURN    ${check}

User REPL Send Expect True
    [Documentation]    Send a command using REPL and check for True
    [Arguments]    ${board}    ${cmd}    ${timeout}=${1.0}

    ${check}=    Call Method    ${board.python_uart}    send    ${cmd}    ${timeout}
    Should Be True    ${check}

Raw REPL Exec
    [Documentation]    Execute a command using the board's raw REPL interface.
    [Arguments]    ${board}    ${cmd}

    ${resp}=    Call Method    ${board.python_raw_repl_uart}    exec    ${cmd}

    RETURN    ${resp}

Raw REPL Exec NoRet
    [Documentation]    Execute a command using the board's raw REPL interface.
    [Arguments]    ${board}    ${cmd}

    Call Method    ${board.python_raw_repl_uart}    exec    ${cmd}

Zephyr Shell Send
    [Documentation]    Send a command using the board's Zephyr shell interface.
    [Arguments]    ${board}    ${cmd}    ${timeout}=${1.0}

    ${resp}=    Call Method    ${board.zephyr_uart}    send    ${cmd}    ${timeout}

    RETURN    ${resp}

DUT1 User REPL Send
    [Arguments]    ${cmd}    ${timeout}=${1.0}

    ${resp}=    User REPL Send    ${settings_board[0]}    ${cmd}    ${timeout}

    RETURN    ${resp}

Board Reset Module
    [Arguments]    ${board}

    Call Method    ${board}    reset_module

Board Terminate Script
    [Arguments]    ${board}

    Call Method    ${board}    quit_running_app
    Sleep    100ms

Board Delete Script
    [Arguments]    ${board}    ${script}

    User REPL Send Error Not Expected    ${board}    import os
    # If the file doesn't exist, then any error can be ignored.
    User REPL Send NoRet    ${board}    os.unlink('${script}')

Board Soft Reboot
    [Arguments]    ${board}

    ${resp}=    Call Method    ${board}    soft_reset_module

    RETURN    ${resp}

Get Board Addr
    [Arguments]    ${board}

    ${resp}=    Run Script on Board    ${board}    ${BLE_ADDR_SCRIPT}
    ${resp}=    Convert To String    ${resp}

    Should Not Contain    ${resp}    ${BLE_ADDR_FAIL_RESP}
    ${resp}=    Replace String    ${resp}    \r\n    ${EMPTY}

    RETURN    ${resp}

Get Board Type
    [Arguments]    ${board}

    ${resp}=    User REPL Send    ${board}    os.uname().sysname
    ${resp}=    Replace String    ${resp}    \r\n    ${EMPTY}

    ${is_lyra}=    Run Keyword And Return Status    Should Contain    ${resp}    lyra    ignore_case=True
    IF   ${is_lyra} == ${True}
        RETURN    ${LYRA_BOARD_TYPE}
    ELSE
        RETURN    ${resp}
    END

Setup Xray Upload
    ${machine_name}=    DUT1 User REPL Send    os.uname().machine
    ${machine_name}=    Replace String    ${machine_name}    \r\n    ${EMPTY}

    ${resp}=    Upload.Get Test Set Value    ${machine_name}
    ${test_plan}=    Set Variable    ${JIRA_PROJECT}-${resp}

    XListen.Setup    ${JIRA_PROJECT}    ${test_plan}    ${OUTPUT_FILE}
