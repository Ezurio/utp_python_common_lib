*** Settings ***
Documentation       Embedded Python UWB Tests

Resource            common_lib/resources/common.robot
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        1 minute


*** Variables ***
${TWO_WAY_RANGE_SCRIPT}                 canvas_python_sample_apps/uwb_simple/main.py
${TWO_WAY_RANGE_SCRIPT_START_RESP}      My device ID is
${INVALID_RANGE}                        ${65535}


*** Tasks ***
UWB Two-Way-Range
    [Documentation]    This test runs the same script used for our Tag-to-Tag ranging demo.
    ...    UWB, BLE scanning, advertising, and Python callbacks are all tested as part of this test.
    Set Tags    PROD-2476

    ${board1_id}=    Get Board Device ID    ${settings_board[0]}
    ${board2_id}=    Get Board Device ID    ${settings_board[1]}

    Setup Board for Ranging    ${settings_board[0]}
    Setup Board for Ranging    ${settings_board[1]}

    Run Ranging Script on Board    ${settings_board[0]}
    Run Ranging Script on Board    ${settings_board[1]}

    Verify Board Range    ${settings_board[0]}    ${board2_id}
    Verify Board Range    ${settings_board[1]}    ${board1_id}


*** Keywords ***
Setup
    Get Boards    allow_list=['SeraNX040Dvk']    minimum_boards=2
    Init Board    ${settings_board[0]}
    Init Board    ${settings_board[1]}

Teardown
    De-Init Board    ${settings_board[0]}
    De-Init Board    ${settings_board[1]}

Run Ranging Script on Board
    [Arguments]    ${board}

    ${resp}=    Run Script on Board    ${board}    ${TWO_WAY_RANGE_SCRIPT}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    ${TWO_WAY_RANGE_SCRIPT_START_RESP}

Setup Board for Ranging
    [Arguments]    ${board}

    Run Ranging Script on Board    ${board}
    Switch Board to Raw REPL    ${board}
    ${resp}=    Raw REPL Exec    ${board}    config['anchor_mode']\=1
    ${resp}=    Raw REPL Exec    ${board}    config_save()
    Switch Board to User REPL    ${board}
    ${resp}=    User REPL Send    ${board}    os.listdir()
    Should Contain    ${resp}    config.cb
    ${resp}=    Board Reset Module    ${board}

Verify Board Range
    [Arguments]    ${board}    ${peer_board_id}

    ${total_time}=    Set Variable    ${5}
    ${range}=    Set Variable    ${INVALID_RANGE}

    Switch Board to Raw REPL    ${board}
    WHILE    $total_time > ${0}
        ${resp}=    Raw REPL Exec    ${board}    print(devices)
        TRY
            ${resp}=    Raw REPL Exec    ${board}
            ...    print(devices['${peer_board_id}']['range'])
            ${range}=    Convert To Integer    ${resp}
        EXCEPT
            Log    No range found yet
        END
        IF    ${range} == ${INVALID_RANGE}    Sleep    1s    ELSE    BREAK
        ${total_time}=    Evaluate    ${total_time} - 1
    END
    Switch Board to User REPL    ${board}
    IF    ${range} == ${INVALID_RANGE}    Fail    Failed to get range
