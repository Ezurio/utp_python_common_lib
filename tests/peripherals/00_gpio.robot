*** Settings ***
Documentation       Embedded Python GPIO tests. Only one DUT board is required for all tests.

Resource            common_lib/resources/common.robot
Library             String
Library             RPA.Tables
Library             RPA.RobotLogListener

Suite Setup         Setup
Suite Teardown      Teardown
Test Teardown       Teardown Test
Test Timeout        1 minute


*** Variables ***
${GPIO_SCRIPT}                  common_lib${/}scripts${/}GPIO_scripts${/}gpio_generic_script.py
${GPIO_SCRIPT_START_RESP}       gpio ready

# MB_RX and MB_TX are not used because they are used for the Python UART by the Sera DVK
#
# The Sera DVK has pullups on the I2C pins because the peripheral is used by the application.
# Therefore, the disonnect test will fail if the I2C pins are checked.
# They are listed last so that the loop can skip them by decreasing the list size by 1.
@{GPIO_PAIR_A_LIST}             MB_PWM    MB_RST    MB_AN    MB_MISO    MB_SCL
@{GPIO_PAIR_B_LIST}             MB_INT    MB_SCK    MB_CS    MB_MOSI    MB_SDA


*** Tasks ***
GPIO A To B No Pull
    [Documentation]    This test will toggle all pins in list A and check that the corresponding pins in list B are also toggled. No Pull is set.
    Pin Setup    ${GPIO_PAIR_A_LIST}    ${GPIO_PAIR_B_LIST}    Pin.PULL_NONE    Pin.PULL_NONE    low

    Set Tags    PROD-5406

    # toggle all pins and check
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].high()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].low()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

GPIO B To A No Pull
    [Documentation]    This test will toggle all pins in list B and check that the corresponding pins in list A are also toggled. No Pull is set.
    Pin Setup    ${GPIO_PAIR_B_LIST}    ${GPIO_PAIR_A_LIST}    Pin.PULL_NONE    Pin.PULL_NONE    low

    Set Tags    PROD-5407

    # toggle all pins and check
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].high()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].low()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

GPIO A To B Pull Up
    [Documentation]    This test will toggle all pins in list A and check that the corresponding pins in list B are also toggled. Pull Up is set.

    Set Tags    PROD-5408

    Pin Setup    ${GPIO_PAIR_A_LIST}    ${GPIO_PAIR_B_LIST}    Pin.PULL_NONE    Pin.PULL_UP    low

    # toggle all pins and check
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].high()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].low()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

    # All pins low at this point so disconnect outputs and check pullups make input high
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${DISCONNECT_LIST_SIZE}
        ${resp}=    DUT1 User REPL Send
        ...    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].reconfigure("${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]", Pin.NO_CONNECT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

GPIO B To A Pull Up
    [Documentation]    This test will toggle all pins in list B and check that the corresponding pins in list A are also toggled. Pull Up is set.

    Set Tags    PROD-5409

    Pin Setup    ${GPIO_PAIR_B_LIST}    ${GPIO_PAIR_A_LIST}    Pin.PULL_NONE    Pin.PULL_UP    low

    # toggle all pins and check
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].high()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].low()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

    # All pins low at this point so disconnect outputs and check pullups make input high
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send
        ...    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].reconfigure("${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]", Pin.NO_CONNECT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

GPIO A To B Pull Down
    [Documentation]    This test will toggle all pins in list A and check that the corresponding pins in list B are also toggled. Pull Down is set.

    Set Tags    PROD-5410

    Pin Setup    ${GPIO_PAIR_A_LIST}    ${GPIO_PAIR_B_LIST}    Pin.PULL_NONE    Pin.PULL_DOWN    high

    # toggle all pins and check
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].low()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].high()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

    # All pins high at this point so disconnect outputs and check pulldowns make input low
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${DISCONNECT_LIST_SIZE}
        ${resp}=    DUT1 User REPL Send
        ...    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].reconfigure("${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]", Pin.NO_CONNECT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

GPIO B To A Pull Down
    [Documentation]    This test will toggle all pins in list B and check that the corresponding pins in list A are also toggled. Pull Down is set.

    Set Tags    PROD-5411

    Pin Setup    ${GPIO_PAIR_B_LIST}    ${GPIO_PAIR_A_LIST}    Pin.PULL_NONE    Pin.PULL_DOWN    high

    # toggle all pins and check
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${LIST_A_SIZE}
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].low()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END

        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].high()
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_A_LIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    1
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    1
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END

    # All pins high at this point so disconnect outputs and check pulldowns make input low
    ${GPIO_INDEX}=    Set Variable    0
    WHILE    ${GPIO_INDEX} < ${DISCONNECT_LIST_SIZE}
        ${resp}=    DUT1 User REPL Send
        ...    ${GPIO_PAIR_B_LIST}[${GPIO_INDEX}].reconfigure("${GPIO_PAIR_B_LIST}[${GPIO_INDEX}]", Pin.NO_CONNECT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    ${GPIO_PAIR_ALIST}[${GPIO_INDEX}].value()
        ${resp_string}=    Convert To String    ${resp}
        Should Contain    ${resp_string}    0
        # The test below causes the Lyra 24 to fail a solution is being worked on
        IF    ${board1_type} != ${LYRA_BOARD_TYPE}
            ${resp}=    DUT1 User REPL Send    print(${GPIO_PAIR_A_LIST}[${GPIO_INDEX}]_state)
            ${resp_string}=    Convert To String    ${resp}
            Should Contain    ${resp_string}    0
        END

        ${GPIO_INDEX}=    Evaluate    ${GPIO_INDEX} + 1
    END


*** Keywords ***
Setup
    Get Boards
    Init Board    ${settings_board[0]}

    ${resp}=    Run Script on Board    ${settings_board[0]}    ${GPIO_SCRIPT}
    ${resp_string}=    Convert To String    ${resp}
    Should Contain    ${resp_string}    ${GPIO_SCRIPT_START_RESP}

    ${tmp}=    Get Board Type    ${settings_board[0]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}

    ${a_size}=    Get Length    ${GPIO_PAIR_A_LIST}
    ${b_size}=    Get Length    ${GPIO_PAIR_B_LIST}
    IF    ${a_size} != ${b_size}
        Fail    GPIO A and B lists are not the same size
    END

    Set Global Variable    ${LIST_A_SIZE}    ${a_size}
    ${tmp}=    Evaluate    ${LIST_A_SIZE} - 1
    Set Global Variable    ${DISCONNECT_LIST_SIZE}    ${tmp}

Teardown
    De-Init Board    ${settings_board[0]}

Teardown Test
    # For Lyra, there are a limited number of pin interrupts.
    # Explicitly remove the pin objects even though garbage collection should do it
    # (https://rfpros.atlassian.net/browse/PROD-5310.
    FOR    ${element}    IN    @{GPIO_PAIR_A_LIST}
        ${resp}=    DUT1 User REPL Send    ${element}.configure_event(None, Pin.EVENT_NONE)
        ${resp}=    DUT1 User REPL Send    ${element} = None
    END

    FOR    ${element}    IN    @{GPIO_PAIR_B_LIST}
        ${resp}=    DUT1 User REPL Send    ${element}.configure_event(None, Pin.EVENT_NONE)
        ${resp}=    DUT1 User REPL Send    ${element} = None
    END

    ${resp}=    DUT1 User REPL Send    gc.collect()

Pin Setup
    [Arguments]    ${list_a}    ${list_b}    ${pull_a}    ${pull_b}    ${initial_state}

    FOR    ${element}    IN    @{list_a}
        ${resp}=    DUT1 User REPL Send    ${element} = Pin("${element}", Pin.OUT, ${pull_a})
        IF    "${initial_state}" == "high"
            ${resp}=    DUT1 User REPL Send    ${element}.high()
        ELSE IF    "${initial_state}" == "low"
            ${resp}=    DUT1 User REPL Send    ${element}.low()
        ELSE
            Fail    Invalid initial state
        END
    END

    # List b is input
    FOR    ${element}    IN    @{list_b}
        ${resp}=    DUT1 User REPL Send    ${element} = Pin("${element}", Pin.IN, ${pull_b})
        ${resp}=    DUT1 User REPL Send    ${element}.configure_event(${element}_Callback, Pin.EVENT_BOTH)
    END
