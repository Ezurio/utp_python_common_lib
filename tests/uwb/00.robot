*** Settings ***
Documentation       Embedded Python UWB Tests

Resource            common_lib/resources/common.robot
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        1 minute


*** Variables ***
${TWO_WAY_RANGE_SCRIPT}     canvas_python_samples/apps/sera_nx040_dvk/uwb_ranging_demo/uwb_ranging_demo.py
${INVALID_RANGE}            ${65535}


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
    # Both devices must support UWB and BLE
    ${list}=    Create List    DUT    UWB    BLE
    ${desired_properties}=    Create List    ${list}    ${list}
    Get Boards    allow_list=['SeraNX040Dvk']    minimum_boards=2    desired_properties=${desired_properties}
    Init Board    ${settings_board[0]}
    Init Board    ${settings_board[1]}

Teardown
    De-Init Board    ${settings_board[0]}
    De-Init Board    ${settings_board[1]}

Run Ranging Script on Board
    [Arguments]    ${board}

    # The variable robot_test_rack is used to prevent the script from
    # starting because callbacks don't occur in the raw REPL.
    User REPL Send Error Not Expected    ${board}    robot_test_rack = True
    Run Script on Board Expect Response    ${board}    ${TWO_WAY_RANGE_SCRIPT}
    User REPL Send Error Not Expected    ${board}    start_demo()

Setup Board for Ranging
    [Arguments]    ${board}

    Run Ranging Script on Board    ${board}
    User REPL Send Error Not Expected    ${board}    config['anchor_mode']=1
    User REPL Send Error Not Expected    ${board}    config_save()
    ${resp}=    User REPL Send    ${board}    os.listdir()
    Should Contain    ${resp}    config.cb
    Board Reset Module    ${board}

Verify Board Range
    [Arguments]    ${board}    ${peer_board_id}

    ${total_time}=    Set Variable    ${30}
    ${range}=    Set Variable    ${INVALID_RANGE}

    WHILE    $total_time > ${0}
        # This print is for debugging/logging purposes only.
        User REPL Send Error Not Expected    ${board}    print(devices)
        TRY
            ${resp}=    User REPL Send    ${board}
            ...    print(devices['${peer_board_id}']['range'])
            ${range}=    Convert To Integer    ${resp}
        EXCEPT
            Log    No range found yet
        END
        IF    ${range} == ${INVALID_RANGE}    Sleep    1s    ELSE    BREAK
        ${total_time}=    Evaluate    ${total_time} - 1
    END
    IF    ${range} == ${INVALID_RANGE}    Fail    Failed to get range
