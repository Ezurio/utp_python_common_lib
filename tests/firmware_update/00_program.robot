*** Settings ***
Documentation       Program matching boards then Query Version

Resource            common_lib/resources/common.robot
Library             ./common_lib/libraries/discovery.py    WITH NAME    Discovery
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        5 minute


*** Variables ***
${file_name}            ${EMPTY}
${release_version}      ${EMPTY}
${board_name}           ${EMPTY}


*** Tasks ***
Program Boards
    FOR    ${b}    IN    @{settings_board}
        Call Method    ${b}    program_mcu    ${file_name}    ${board_name}
        Sleep    ${b.BOOT_TIME_SECONDS}    reason=Wait for board to boot
        Check Firmware Version    ${b}
    END


*** Keywords ***
Setup
    Should Not Be Empty    ${file_name}
    Should Not Be Empty    ${release_version}
    Should Not Be Empty    ${board_name}

    Get Boards

    # Only program and check boards that match the board name.
    ${boards}    Create List
    FOR    ${b}    IN    @{settings_board}
        ${match}=    Evaluate    '${board_name}'.lower() in '${b.user_board_name}'.lower()
        IF    ${match}
            Append To List    ${boards}    ${b}
        END
    END
    Set Global Variable    ${settings_board}    ${boards}

    ${length}=    Get Length    ${settings_board}
    IF    ${length} < 1
        Fail    No boards found matching name: ${board_name}
    END

    # Don't initialize the board here because it may fail depending on the firmware
    # that is currently on the device. 
    # It will be initialized normally before version is read.

Teardown
    FOR    ${b}    IN    @{settings_board}
        De-Init Board    ${b}
    END

Check Firmware Version
    [Documentation]    Check the firmware version of the board (knowing that MCU was reset)
    [Arguments]    ${board}

    Init Board    ${board}

    ${resp}    User REPL Send    ${board}    os.uname().release
    ${resp}    Replace String    ${resp}    '    ${EMPTY}
    Should Be Equal    ${resp}    ${release_version}
