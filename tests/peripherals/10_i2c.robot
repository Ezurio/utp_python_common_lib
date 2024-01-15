*** Settings ***
Documentation       I2C Tests. Only one DUT board is required for all tests.

Resource            common_lib/resources/common.robot
Library             String
Library             ./common_lib/libraries/StringLib.py    WITH NAME    STRING_LIB
Library    RPA.RobotLogListener

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        30 minute


*** Variables ***
${I2C_BUS_LYRA}             \"I2C0\", \"MB_SDA\", \"MB_SCL\"
${I2C_BUS_ZEPHYR}           \"i2c@40003000\"
${eeprom_step_size}         32
${eeprom_max_size}          65536
${address_device1}          0x50
${address_device2}          0x57
${write_address}            0x0000

*** Tasks ***
Test I2C EEPROM 1
    [Documentation]    This test writes to every memory address in the first I2C EEPROM device connected.

    Set Tags    PROD-5413

    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_LYRA})
    ELSE
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_ZEPHYR})
    END
    ${resp}=    DUT1 User REPL Send    i2c = I2C(i2c_description,${address_device1})

    ${eeprom_access_address}=    Set Variable    ${write_address}
    WHILE    ${eeprom_access_address}<${eeprom_max_size}
        I2C EEPROM READ Write    ${eeprom_access_address}
	    ${eeprom_access_address}=    Evaluate    ${eeprom_access_address}+${eeprom_step_size}
    END

Test I2C EEPROM 2
    [Documentation]    This test writes to every memory address in the second I2C EEPROM device connected.

    Set Tags    PROD-5414

    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_LYRA})
    ELSE
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_ZEPHYR})
    END
    ${resp}=    DUT1 User REPL Send    i2c = I2C(i2c_description,${address_device2})

    ${eeprom_access_address}=    Set Variable    ${write_address}
    WHILE    ${eeprom_access_address}<${eeprom_max_size}
        I2C EEPROM READ Write    ${eeprom_access_address}
	    ${eeprom_access_address}=    Evaluate    ${eeprom_access_address}+${eeprom_step_size}
    END

Test I2C EEPROM Interleaved
    [Documentation]    This test writes to every memory address in both I2C EEPROM devices connected in an interleaved manner.

    Set Tags    PROD-5415

    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_LYRA})
    ELSE
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_ZEPHYR})
    END
    ${eeprom_access_address}=    Set Variable    ${write_address}

    WHILE    ${eeprom_access_address}<${eeprom_max_size}
        ${resp}=    DUT1 User REPL Send    i2c = I2C(i2c_description,${address_device1})
        I2C EEPROM READ Write    ${eeprom_access_address}
        ${resp}=    DUT1 User REPL Send    i2c = I2C(i2c_description,${address_device2})
        I2C EEPROM READ Write    ${eeprom_access_address}
    	${eeprom_access_address}=    Evaluate    ${eeprom_access_address}+${eeprom_step_size}
    END

*** Keywords ***
Setup
    Get Boards
    Init Board    ${settings_board1}

    # Prerequisites for I2C control
    DUT1 User REPL Send    import canvas
    DUT1 User REPL Send    import machine
    DUT1 User REPL Send    from machine import Pin
    DUT1 User REPL Send    from machine import I2C

    ${tmp}=    Get Board Type    ${settings_board1}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}


Teardown
    De-Init Board    ${settings_board1}

I2C EEPROM READ Write
    [Arguments]    ${eeprom_access_address}
    # First generate the random data to be written.
    # -------------------------------------------------------------------------------
    ${hex_string_size}=    Evaluate    ${eeprom_step_size}*2
    ${write_string_data}=    STRING_LIB.BuildHexString    ${hex_string_size}
    # -------------------------------------------------------------------------------
    # Convert the address to hex
    ${hex_write_address}=    Convert To Hex    ${eeprom_access_address}    length=4
    # -------------------------------------------------------------------------------
    # Now write it - the device type is 0xA0, the address address_device and a write indicated
    # by a low lsb. This gives us a command byte of 0xA0. The write address is sent
    # as a further two bytes, followed by the write data.
    # -------------------------------------------------------------------------------
    ${hex_write_address_data}=    Catenate    ${hex_write_address}${write_string_data}
    ${byte_write_address_data}=    STRING_LIB.ConvertHexadecimalStringtoByteArray    ${hex_write_address_data}
    ${resp}=    DUT1 User REPL Send    i2c.write(b"${byte_write_address_data}")

    # -------------------------------------------------------------------------------
    # Read back the data - same id and address but set the lsb for a read.
    # -------------------------------------------------------------------------------
    ${byte_write_address}=    STRING_LIB.ConvertHexadecimalStringtoByteArray    ${hex_write_address}
    ${resp}=    DUT1 User REPL Send    read = i2c.write_read(b"${byte_write_address}",${eeprom_step_size})
    ${Read_result}=    DUT1 User REPL Send    print(read)
    ${Read_string}=    Convert To String    ${Read_result}
    ${HEX}=    STRING_LIB.ConvertASCIIToHexadecimalNoCRLF    ${Read_string}

    # END
    Should Be Equal    ${HEX}    ${write_string_data}
