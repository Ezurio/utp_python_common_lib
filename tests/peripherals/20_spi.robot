*** Settings ***
Documentation       SPI Tests. Only one DUT board is required for all tests.

Resource            common_lib/resources/common.robot
Library             String
Library             ./common_lib/libraries/StringLib.py    WITH NAME    STRING_LIB

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        2 minute


*** Variables ***
# The DUT in the test rack uses a https://www.mikroe.com/eeprom-5-click board.
# A shuttle click board may be used to connect multiple boards to the DUT.
${eeprom_chunk_size}    16
${eeprom_step_size}     4096
${eeprom_max_size}      524288
${write_address}        0

${WREN}                 \\x06
${WRDI}                 \\x04
${RDSR}                 \\x05
${WRSR}                 \\x01
${READ}                 \\x03
${WRITE}                \\x02


*** Tasks ***
Test SPI1 EEPROM
    [Documentation]    Writes to memory addresses in the EEPROM and reads them back.

    Set Tags    PROD-5417

    ${eeprom_address}=    Set Variable    ${write_address}
    WHILE    ${eeprom_address}<${eeprom_max_size}
        SPI TEST BANK    spi1    ${eeprom_address}
        ${eeprom_address}=    Evaluate    ${eeprom_address}+${eeprom_step_size}
    END


*** Keywords ***
Setup
    ${desired_properties} =    Create List    DUT    SPI_CLICK
    Get Boards    desired_properties=${desired_properties}
    Init Board    ${settings_board[0]}

    # Prerequisites for I2C control
    DUT1 User REPL Send    import canvas
    DUT1 User REPL Send    import machine
    DUT1 User REPL Send    from machine import Pin
    DUT1 User REPL Send    from machine import SPI

    ${tmp}=    Get Board Type    ${settings_board[0]}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}

    # Set active low Hold and Write Protect to 1
    # Note: On the Sera NX040 DVK, there are other devices on this SPI bus.
    ${resp}=    DUT1 User REPL Send    hold = Pin("MB_RST", Pin.OUT, Pin.PULL_NONE)
    ${resp}=    DUT1 User REPL Send    hold.high()
    ${resp}=    DUT1 User REPL Send    wp = Pin("MB_PWM", Pin.OUT, Pin.PULL_NONE)
    ${resp}=    DUT1 User REPL Send    wp.high()

    # Set up the SPI bus
    ${resp}=    DUT1 User REPL Send    cs1 = Pin("MB_CS", Pin.OUT, Pin.PULL_NONE)
    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${resp}=    DUT1 User REPL Send    spi1 = SPI(("USART0","MB_SCK", "MB_MOSI", "MB_MISO"), cs1)
    ELSE
        ${resp}=    DUT1 User REPL Send    spi1 = SPI("spi@40023000", cs1)
    END

Teardown
    De-Init Board    ${settings_board[0]}

SPI TEST BANK
    [Arguments]    ${spi}    ${eeprom_address}

    ${dummy_data}=    Set Variable    \\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00

    # First generate the random data to be written.
    # -------------------------------------------------------------------------------
    ${hex_string_size}=    Evaluate    ${eeprom_chunk_size}*2
    ${write_string_data}=    STRING_LIB.BuildHexString    ${hex_string_size}
    # -------------------------------------------------------------------------------
    # Convert the address to hex
    ${hex_write_address}=    Convert To Hex    ${eeprom_address}    length=6
    # -------------------------------------------------------------------------------
    # Let the device know we want to access its write array. Do this by clocking in
    # a WREN instruction.
    # -------------------------------------------------------------------------------
    ${resp}=    DUT1 User REPL Send    ${spi}.transceive(b"${WREN}")
    # -------------------------------------------------------------------------------
    # Now write it - the write command is 0x2.
    # -------------------------------------------------------------------------------
    # Need to strip off the exta \\x in front of the write command
    ${write_cmd}=    STRING_LIB.Right    ${WRITE}    2
    ${hex_write_address_data}=    Set Variable    ${write_cmd}${hex_write_address}${write_string_data}
    ${byte_write_address_data}=    STRING_LIB.ConvertHexadecimalStringtoByteArray    ${hex_write_address_data}
    ${resp}=    DUT1 User REPL Send    ${spi}.transceive(b"${byte_write_address_data}")
    # -------------------------------------------------------------------------------
    # Verify the write enable latch is set by reading it back.
    # -------------------------------------------------------------------------------
    ${resp}=    DUT1 User REPL Send    status = ${spi}.transceive(b"${RDSR}")
    ${resp}=    DUT1 User REPL Send    status = ${spi}.transceive(b"${WRDI}")
    # -------------------------------------------------------------------------------
    # Write cycle delay.
    # -------------------------------------------------------------------------------
    Sleep    10ms
    # -------------------------------------------------------------------------------
    # Read back the data - same address with dummy data the read command is 0x3.
    # -------------------------------------------------------------------------------
    ${byte_write_address}=    STRING_LIB.ConvertHexadecimalStringtoByteArray    ${hex_write_address}
    ${read_cmd_address_dummy}=    Set Variable    ${READ}${byte_write_address}${dummy_data}
    ${resp}=    DUT1 User REPL Send    rdata = ${spi}.transceive(b"${read_cmd_address_dummy}")
    ${Read_result}=    DUT1 User REPL Send    print(rdata)
    ${Read_string}=    Convert To String    ${Read_result}
    ${HEX}=    STRING_LIB.ConvertASCIIToHexadecimalNoCRLF    ${Read_string}
    # remove the first 3 bytes that form the address and command
    ${HEX}=    STRING_LIB.Right    ${HEX}    ${hex_string_size}
    Should Be Equal    ${HEX}    ${write_string_data}
