*** Settings ***
Documentation       Query Version using global variable

Resource            common_lib/resources/common.robot
Library             ./common_lib/libraries/discovery.py    WITH NAME    Discovery
Library             String

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        5 minute


*** Variables ***
${release_version}      ${EMPTY}
${board_name}           ${EMPTY}


*** Tasks ***
Check All Boards In List
    [Documentation]    Check the firmware version of the board (knowing that MCU was reset)

    FOR    ${b}    IN    @{settings_board}
        Init Board    ${b}

        ${resp}    User REPL Send    ${b}    os.uname().release
        ${resp}    Replace String    ${resp}    '    ${EMPTY}
        Should Be Equal    ${resp}    ${release_version}
    END


*** Keywords ***
Setup
    Should Not Be Empty    ${release_version}
    Should Not Be Empty    ${board_name}

    Get Boards

    # Only check boards with a matching name
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

Teardown
    FOR    ${b}    IN    @{settings_board}
        De-Init Board    ${b}
    END
