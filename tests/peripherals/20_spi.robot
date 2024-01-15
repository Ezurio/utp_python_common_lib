*** Settings ***
Documentation       SPI Tests. Only one DUT board is required for all tests.

Resource            common_lib/resources/common.robot
Library             String
Library             ./common_lib/libraries/StringLib.py    WITH NAME    STRING_LIB

Suite Setup         Setup
Suite Teardown      Teardown
Test Timeout        17 minute


*** Variables ***
${eeprom_step_size}         16
${eeprom_max_size}          2048
${write_address}            0x0000

${WREN}                     \\x06
${WRDI}                     \\x04
${RDSR}                     \\x05
${WRSR}                     \\x01
${READ}                     \\x03
${WRITE}                    \\x02

*** Tasks ***
Test SPI1 EEPROM
    [Documentation]    This test writes to every memory address in the first SPI EEPROM device connected.

    Set Tags    PROD-5417

    ${eeprom_address}=    Set Variable    ${write_address}
    WHILE    ${eeprom_address}<${eeprom_max_size}
        SPI TEST BANK    spi1    ${eeprom_address}
        ${eeprom_address}=    Evaluate    ${eeprom_address}+${eeprom_step_size}
    END

Test SPI2 EEPROM
    [Documentation]    This test writes to every memory address in the second SPI EEPROM device connected.

    Set Tags    PROD-5418
    Skip If    condition=${board1_type}==${ZEPHYR_BOARD_TYPE}    msg=Zephyr boards cannot support multiple SPI devices at present

    ${eeprom_address}=    Set Variable    ${write_address}
    WHILE    ${eeprom_address}<${eeprom_max_size}
        SPI TEST BANK    spi2    ${eeprom_address}
        ${eeprom_address}=    Evaluate    ${eeprom_address}+${eeprom_step_size}
    END

Test SPI1 and SPI2 EEPROM Interleaved
    [Documentation]    This test writes to every memory address in both SPI EEPROM devices connected in an interleaved manner.

    Set Tags    PROD-5419

    Skip If    condition=${board1_type}==${ZEPHYR_BOARD_TYPE}    msg=Zephyr boards cannot support multiple SPI devices at present

    ${eeprom_address}=    Set Variable    ${write_address}
    WHILE    ${eeprom_address}<${eeprom_max_size}
        SPI TEST BANK    spi1    ${eeprom_address}
        SPI TEST BANK    spi2    ${eeprom_address}
        ${eeprom_address}=    Evaluate    ${eeprom_address}+${eeprom_step_size}
    END


*** Keywords ***
Setup
    Get Boards
    Init Board    ${settings_board1}

    # Prerequisites for I2C control
    DUT1 User REPL Send    import canvas
    DUT1 User REPL Send    import machine
    DUT1 User REPL Send    from machine import Pin
    DUT1 User REPL Send    from machine import SPI

    ${tmp}=    Get Board Type    ${settings_board1}
    ${tmp}=    Replace String    ${tmp}    \r\n    ${EMPTY}
    Set Global Variable    ${board1_type}    ${tmp}

    IF    ${board1_type} == ${LYRA_BOARD_TYPE}
        ${resp}=    DUT1 User REPL Send    cs1 = Pin("MB_CS", Pin.OUT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    spi1 = SPI(("USART0","MB_SCK", "MB_MOSI", "MB_MISO"), cs1)

        ${resp}=    DUT1 User REPL Send    cs2 = Pin("MB_AN", Pin.OUT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    spi2 = SPI(("USART0","MB_SCK", "MB_MOSI", "MB_MISO"), cs2)
    ELSE
        ${resp}=    DUT1 User REPL Send    cs1 = Pin("SPI_CS", Pin.OUT, Pin.PULL_NONE)
        ${resp}=    DUT1 User REPL Send    spi1 = SPI("spi@40023000", cs1)

        # Set up cs2 / spi2 here once zephyr supports multiple SPI devices
    END


Teardown
    De-Init Board    ${settings_board1}

SPI TEST BANK
    [Arguments]    ${spi}    ${eeprom_address}

    ${dummy_data}=    Set Variable    \\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00

    # First generate the random data to be written.
    # -------------------------------------------------------------------------------
    ${hex_string_size}=    Evaluate    ${eeprom_step_size}*2
    ${write_string_data}=    STRING_LIB.BuildHexString    ${hex_string_size}
    # -------------------------------------------------------------------------------
    # Convert the address to hex
    ${hex_write_address}=    Convert To Hex    ${eeprom_address}    length=4
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
