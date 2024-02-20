*** Settings ***
Documentation       I2C Tests. Only one DUT board is required for all tests.

Resource            common_lib/resources/common.robot
Library             String
Library             ./common_lib/libraries/StringLib.py    WITH NAME    STRING_LIB
Library             RPA.RobotLogListener

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        6 minute


*** Variables ***
# The test fixture uses the DUAL EE Click board (https://www.mikroe.com/dual-ee-click).
# It contains two EEPROMs (https://download.mikroe.com/documents/datasheets/atmel-8828-seeprom-at24cm02-datasheet.pdf).
${I2C_BUS_LYRA}                 \"I2C0\", \"MB_SDA\", \"MB_SCL\"
${I2C_BUS_ZEPHYR}               \"i2c@40003000\"
${EEPROM_CHUNK_SIZE}            1
${EEPROM_PAGE_SIZE}             256
${EEPROM_TEST_SIZE}             65535
# For simplicity, the most significant two address bits in each chip are static
# (not counting the chip selector addr bit).
# These addresses are shifted right one bit (r/w bit is handled by peripheral/driver).
${ADDRESS_DEVICE_1}             0x50
# 0x04 selects second chip. 0x01 selects second 64K
${ADDRESS_DEVICE_2}             0x55
${STARTING_WRITE_ADDRESS}       0x0000
${eeprom_access_address}        0x0000


*** Tasks ***
Test I2C EEPROM 1
    [Documentation]    Write to every page in the first 64K of the first I2C EEPROM device connected.

    Set Tags    PROD-5413

    Reset EEPROM Address
    WHILE    ${eeprom_access_address}<${EEPROM_TEST_SIZE}
        ${hex_write_address}    ${write_string_data}=    I2C EEPROM Setup and Write    i2c1    ${eeprom_access_address}
        I2C EEPROM Read and Compare    i2c1    ${hex_write_address}    ${write_string_data}
        Increment EEPROM Address
    END

Test I2C EEPROM 2
    [Documentation]    Write to every page in the second 64K of the second I2C EEPROM device connected.

    Set Tags    PROD-5414

    Reset EEPROM Address
    WHILE    ${eeprom_access_address}<${EEPROM_TEST_SIZE}
        ${hex_write_address}    ${write_string_data}=    I2C EEPROM Setup and Write    i2c2    ${eeprom_access_address}
        I2C EEPROM Read and Compare    i2c2    ${hex_write_address}    ${write_string_data}
        Increment EEPROM Address
    END

Test I2C EEPROM Interleaved
    [Documentation]    Write to both I2C EEPROM devices in an interleaved manner.

    Set Tags    PROD-5415

    Reset EEPROM Address
    WHILE    ${eeprom_access_address}<${EEPROM_TEST_SIZE}
        ${hex_write_address_1}    ${write_string_data_1}=    I2C EEPROM Setup and Write
        ...    i2c1
        ...    ${eeprom_access_address}
        ${hex_write_address_2}    ${write_string_data_2}=    I2C EEPROM Setup and Write
        ...    i2c2
        ...    ${eeprom_access_address}
        I2C EEPROM Read and Compare    i2c1    ${hex_write_address_1}    ${write_string_data_1}
        I2C EEPROM Read and Compare    i2c2    ${hex_write_address_2}    ${write_string_data_2}
        Increment EEPROM Address
    END


*** Keywords ***
Setup
    Get Boards
    Init Board    ${settings_board[0]}

    # Prerequisites for I2C control
    DUT1 User REPL Send    import canvas
    DUT1 User REPL Send    import machine
    DUT1 User REPL Send    from machine import I2C

    ${tmp}=    Get Board Type    ${settings_board[0]}
    ${board1_type}=    Replace String    ${tmp}    \r\n    ${EMPTY}

    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_LYRA})
    ELSE
        ${resp}=    DUT1 User REPL Send    i2c_description = (${I2C_BUS_ZEPHYR})
    END
    ${resp}=    DUT1 User REPL Send    i2c1 = I2C(i2c_description,${ADDRESS_DEVICE_1})
    ${resp}=    DUT1 User REPL Send    i2c2 = I2C(i2c_description,${ADDRESS_DEVICE_2})

Teardown
    De-Init Board    ${settings_board[0]}

I2C EEPROM Setup and Write
    [Arguments]    ${i2c}    ${eeprom_access_address}
    # First generate the random data to be written.
    # -------------------------------------------------------------------------------
    ${hex_string_size}=    Evaluate    ${EEPROM_CHUNK_SIZE}*2
    ${write_string_data}=    STRING_LIB.BuildHexString    ${hex_string_size}
    # -------------------------------------------------------------------------------
    # Convert the address to hex
    ${hex_write_address}=    Convert To Hex    ${eeprom_access_address}    length=4
    # -------------------------------------------------------------------------------
    # The peripheral handles sending the device address and sets the r/w bit.
    # The write address is two bytes, followed by the write data (1 byte).
    # -------------------------------------------------------------------------------
    ${hex_write_address_data}=    Catenate    ${hex_write_address}${write_string_data}
    ${byte_write_address_data}=    STRING_LIB.ConvertHexadecimalStringtoByteArray    ${hex_write_address_data}
    ${resp}=    DUT1 User REPL Send    ${i2c}.write(b"${byte_write_address_data}")

    Sleep    10ms

    RETURN    ${hex_write_address}    ${write_string_data}

I2C EEPROM Read and Compare
    [Arguments]    ${i2c}    ${hex_write_address}    ${write_string_data}
    # -------------------------------------------------------------------------------
    # Read back the data - same id and address but set the lsb for a read.
    # -------------------------------------------------------------------------------
    ${byte_write_address}=    STRING_LIB.ConvertHexadecimalStringtoByteArray    ${hex_write_address}
    ${resp}=    DUT1 User REPL Send    read = ${i2c}.write_read(b"${byte_write_address}",${EEPROM_CHUNK_SIZE})
    ${Read_result}=    DUT1 User REPL Send    print(read)
    ${Read_string}=    Convert To String    ${Read_result}
    ${HEX}=    STRING_LIB.ConvertASCIIToHexadecimalNoCRLF    ${Read_string}

    # Compare the read data with the written data
    Should Be Equal    ${HEX}    ${write_string_data}

Reset EEPROM Address
    Set Global Variable    ${eeprom_access_address}    ${STARTING_WRITE_ADDRESS}

Increment EEPROM Address
    # Cycle through each page address and each byte within a page.
    ${tmp}=    Evaluate    ${eeprom_access_address}+${EEPROM_PAGE_SIZE}+${EEPROM_CHUNK_SIZE}
    Set Global Variable    ${eeprom_access_address}    ${tmp}
