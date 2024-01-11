*** Settings ***
Documentation       Embedded Python Common Tests. Only one DUT board is required for all tests.

Resource            common_lib/resources/common.robot
Library             String
Library             DateTime

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        1 minute


*** Variables ***
${FILE_WRITE_TEXT}      w
${FILE_WRITE_BINARY}    wb
${FILE_READ_TEXT}       r
${FILE_READ_BINARY}     rb


*** Tasks ***
Query firmware version
    Set Tags    PROD-2640

    ${resp}=    DUT1 User REPL Send    os.uname()
    Should Contain    ${resp}    version
    Log    ${resp}
    ${resp}=    DUT1 User REPL Send    sys.implementation
    Should Contain    ${resp}    version
    Log    ${resp}

File Operations
    Set Tags    PROD-2441

    ${file_name}=    Set Variable    test_file
    ${string_file_contents}=    Set Variable    'This is a test file'
    ${binary_file_contents}=    Set Variable    b'\\xde\\xad\\xbe\\xef'

    Write Read Rename Delete File
    ...    ${file_name}
    ...    ${string_file_contents}
    ...    ${FILE_WRITE_TEXT}
    ...    ${FILE_READ_TEXT}

    Write Read Rename Delete File
    ...    ${file_name}
    ...    ${binary_file_contents}
    ...    ${FILE_WRITE_BINARY}
    ...    ${FILE_READ_BINARY}

    Make Change Delete Directory    test_dir

Query Device ID
    Set Tags    PROD-2438

    ${resp}=    DUT1 User REPL Send    import machine
    ${resp}=    DUT1 User REPL Send    import binascii
    ${resp}=    DUT1 User REPL Send    binascii.hexlify(machine.unique_id()).decode()
    ${id}=    Replace String    ${resp}    '    ${EMPTY}
    Length Should Be    ${id}    ${16}

Time delay
    Set Tags    PROD-2443

    ${delay_ms}=    Set Variable    ${2000}
    ${wait_respose_sconds}=    Evaluate    ${delay_ms} / 1000.0 + 1.0
    ${tolerance_percent}=    Set Variable    ${2.0}
    ${tolerance_percent_board}=    Set Variable    ${3.0}

    ${resp}=    DUT1 User REPL Send    import time
    ${resp}=    DUT1 User REPL Send    time.ticks_ms()
    ${then_board}=    Convert To Integer    ${resp}
    ${then}=    Get Current Date
    ${resp}=    DUT1 User REPL Send    time.sleep_ms(${delay_ms})    ${wait_respose_sconds}
    ${now}=    Get Current Date
    Should Not Contain    ${resp}    error    ignore_case=True
    ${resp}=    DUT1 User REPL Send    time.ticks_ms()
    ${now_board}=    Convert To Integer    ${resp}
    ${delta}=    Subtract Date From Date    ${now}    ${then}
    ${delta}=    Evaluate    ${delta} * 1000
    ${delta_board}=    Evaluate    ${now_board} - ${then_board}
    IF    ${delta} < ${delay_ms} or ${delta_board} < ${delay_ms}
        Fail    Time delay was less than expected
    END
    ${error_percent}=    Evaluate    abs((${delay_ms} - ${delta}) / ${delay_ms} * 100.0)
    ${error_percent_board}=    Evaluate    abs((${delay_ms} - ${delta_board}) / ${delay_ms} * 100.0)
    IF    ${error_percent} > ${tolerance_percent} or ${error_percent_board} > ${tolerance_percent_board}
        Fail    Time delay was outside the tolerance
    END

Heap overflow test
    Set Tags    PROD-2432

    ${buff_var}=    Set Variable    b
    ${buff_size}=    Set Variable    ${1000}

    ${resp}=    DUT1 User REPL Send    import gc
    ${resp}=    DUT1 User REPL Send    gc.collect()
    ${resp}=    DUT1 User REPL Send    gc.mem_free()
    ${free1}=    Convert To Integer    ${resp}
    ${resp}=    DUT1 User REPL Send    ${buff_var}\=bytearray(${buff_size})
    ${resp}=    DUT1 User REPL Send    gc.mem_free()
    ${free2}=    Convert To Integer    ${resp}
    ${diff}=    Evaluate    ${free1}-${free2}
    IF    ${diff} < ${buff_size}
        Fail    Not enough space allocated for buffer
    END
    ${resp}=    DUT1 User REPL Send    ${buff_var}\=None
    ${resp}=    DUT1 User REPL Send    gc.collect()
    ${resp}=    DUT1 User REPL Send    gc.mem_free()
    ${free3}=    Convert To Integer    ${resp}
    IF    ${free3} > ${free1} and ${free3} < ${free2}
        Fail    ${free3} should be less than ${free1} and greater than ${free2}
    END
    ${resp}=    DUT1 User REPL Send    ${buff_var}\=bytearray(${free1})
    Should Contain    ${resp}    MemoryError
    ${resp}=    DUT1 User REPL Send    gc.mem_free()
    ${free4}=    Convert To Integer    ${resp}
    IF    ${free4} > ${free3}    Fail    ${free4} should be less than ${free3}
    ${resp}=    DUT1 User REPL Send    os.uname()
    Should Contain    ${resp}    version

Switch REPL Modes
    [Documentation]    This test switches the REPL to raw REPL mode and back to REPL mode
    ...    and verifies the device is still responsive.
    Set Tags    PROD-2435

    ${resp}=    DUT1 User REPL Send    os.uname()
    Should Contain    ${resp}    version
    Switch Board to Raw REPL    ${settings_board1}
    ${resp}=    Raw REPL Exec    ${settings_board1}    print(os.uname())
    Switch Board to User REPL    ${settings_board1}
    ${resp}=    Convert To String    ${resp}
    Should Contain    ${resp}    version
    ${resp}=    DUT1 User REPL Send    os.uname()
    Should Contain    ${resp}    version

ZCBOR Encode Decode
    Set Tags    PROD-2466

    ${obj}=    Set Variable    o
    ${obj_data}=    Set Variable    {'string': 'ryan', 'int': 5, 'list': [4, 6, 7]}
    ${cbor}=    Set Variable    c
    ${new_obj}=    Set Variable    n

    DUT1 User REPL Send    import canvas
    DUT1 User REPL Send    ${obj}\=${obj_data}
    DUT1 User REPL Send    ${cbor}\=canvas.zcbor_from_obj(${obj},0)
    DUT1 User REPL Send    ${new_obj}\=canvas.zcbor_to_obj(${cbor})
    ${resp}=    DUT1 User REPL Send    print(${new_obj})
    Should Be Equal As Strings    ${resp}    ${obj_data}

REPL Control Characters
    [Documentation]    This test sends control characters (Ctrl+C, Ctrl+D)
    ...    to the REPL and verifies the device is still responsive.
    Set Tags    PROD-2446

    ${dut}=    Set Variable    ${settings_board1}

    ${resp}=    Upload Script to Board    ${dut}    common_lib/scripts/loop_forever.py    main.py
    Board Reset Module    ${dut}
    Board Terminate Script    ${dut}
    Board Delete Script    ${dut}    main.py
    Board Soft Reboot    ${dut}


*** Keywords ***
Setup
    Get Boards
    Init Board    ${settings_board1}

Teardown
    De-Init Board    ${settings_board1}

Write Read Rename Delete File
    [Arguments]    ${file_name}    ${file_contents}    ${write_mode}    ${read_mode}

    ${file}=    Set Variable    f
    ${file_rename}=    Set Variable    rename_test_1234

    DUT1 User REPL Send    ${file}\=open('${file_name}','${write_mode}')
    ${resp}=    DUT1 User REPL Send    ${file}.write(${file_contents})
    ${write_len}=    Convert To Integer    ${resp}
    DUT1 User REPL Send    ${file}.close()
    ${resp}=    DUT1 User REPL Send    os.stat('${file_name}')
    ${file_stat}=    Evaluate    eval('${resp}')
    Should Be Equal As Integers    ${write_len}    ${file_stat[5]}
    DUT1 User REPL Send    ${file}\=open('${file_name}','${read_mode}')
    ${resp}=    DUT1 User REPL Send    ${file}.read()
    Should Contain    ${resp}    ${file_contents}
    DUT1 User REPL Send    ${file}.close()
    DUT1 User REPL Send    os.rename('${file_name}','${file_rename}')
    ${resp}=    DUT1 User REPL Send    os.listdir()
    Should Not Contain    ${resp}    ${file_name}
    Should Contain    ${resp}    ${file_rename}
    DUT1 User REPL Send    os.unlink('${file_rename}')
    ${resp}=    DUT1 User REPL Send    os.listdir()
    Should Not Contain    ${resp}    ${file_rename}

Make Change Delete Directory
    [Arguments]    ${dir_name}

    ${resp}=    DUT1 User REPL Send    os.getcwd()
    ${resp}=    DUT1 User REPL Send    os.mkdir('${dir_name}')
    ${resp}=    DUT1 User REPL Send    os.listdir()
    Should Contain    ${resp}    ${dir_name}
    ${resp}=    DUT1 User REPL Send    os.chdir('${dir_name}')
    ${resp}=    DUT1 User REPL Send    os.getcwd()
    # remove quotes
    ${current_dir}=    Replace String    ${resp}    '    ${EMPTY}
    Should End With    ${current_dir}    ${dir_name}
    ${resp}=    DUT1 User REPL Send    os.chdir('..')
    ${resp}=    DUT1 User REPL Send    os.rmdir('${dir_name}')
    ${resp}=    DUT1 User REPL Send    os.listdir()
    Should Not Contain    ${resp}    ${dir_name}
