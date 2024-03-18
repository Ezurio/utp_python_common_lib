from board import Board, BoardConfig
from lc_util import logger_setup
import json

logger = logger_setup(__file__)

# Example boards configuration showing all properties for a board
# Then name properties are metadata and are not required to find a board.
boards_all_props = """
    {
        "boards": [
            {
                "name": "p100_dvk_9517",
                "ports": [
                    {
                        "sn": "1649CC3B1086D8A9",
                        "index": 0,
                        "type": "repl",
                        "source": "device",
                        "name": "Python REPL"
                    },
                    {
                        "sn": "1649CC3B1086D8A9",
                        "index": 1,
                        "type": "zephyr",
                        "source": "device",
                        "name": "Zephyr shell"
                    }
                ],
                "probe": {
                    "sn": "483067853",
                    "type": "jlink",
                    "name": "P100 DVK Jlink OB"
                }
            }
        ]
    }
"""

# Test that the board is not found if the serial number is not present.
# sn is required to find a board.
# This should fail gracefully and not throw an exception.
boards_repl_no_sn = """
    {
        "boards": [
            {
                "name": "p100_dvk_9517",
                "ports": [
                    {
                        "index": 0,
                        "type": "repl",
                        "source": "device",
                        "name": "Python REPL"
                    }
                ]
            }
        ]
    }
"""

# This is the minimum set of properties required to find a board
boards_min_props = """
    {
        "boards": [
            {
                "ports": [
                    {
                        "sn": "1649CC3B1086D8A9",
                        "index": 0,
                        "type": "repl",
                        "source": "device"
                   }
                ]
            }
        ]
    }
"""


def test1():
    logger.info(
        "Zero boards in scope - Class method requires boards to be in scope")
    boards = Board.get_connected()
    logger.info(f"Boards found: {len(boards)}")
    for b in boards:
        logger.info(b)
    assert len(boards) == 0
    del (b)
    del (boards)


def test2():
    logger.info("Get all boards")
    boards = Board.get_connected()
    logger.info(f"Boards found: {len(boards)}")
    for b in boards:
        logger.info(b)
    assert len(boards) != 0


def test3():
    logger.info("Get Nx040 boards")
    allow_list = ['SeraNX040Dvk']
    boards = Board.get_connected(allow_list)
    logger.info(f"Boards found: {len(boards)}")
    i = 0
    for b in boards:
        logger.info(b)
        assert "Nx040" in str(b)
        if i == 0:
            logger.info(f"{b._initialized=}")
            logger.debug(dir(b))
            b.open_and_init_board()
            logger.info(f"{b._initialized=}")
            logger.debug(dir(b))
            i = 1


def test4():
    logger.info("Select board by com port")
    # This is specific to setup
    b1 = Board.get_by_com_port("COM6")
    b2 = Board.get_by_com_port("COM7")
    logger.info(b1)
    assert str(b1) == str(b2)


def test5():
    logger.info("Select board by com port (that doesn't have Zephyr port)")
    # This is specific to setup
    b1 = Board.get_by_com_port(
        "/dev/cu.usbmodem43101", boards_conf=read_boards_conf(boards_all_props))
    logger.info(b1)
    assert b1 != None
    logger.info(f"{b1._initialized=}")
    logger.info(f"{b1.is_initialized=}")
    try:
        b1.open_and_init_board()
        logger.info(f"{b1._initialized=}")
        logger.info(f"{b1.is_initialized=}")
        b1.close_repl_uart()
        b1.open_raw_repl_uart()
        b1.close_raw_repl_uart()
        b1.open_repl_uart()
    except:
        logger.error(dir(b1))
        raise Exception
    # send some commands
    try:
        timeout = 1
        logger.info("f")
        b1.python_uart.send("import machine", timeout)
        b1.python_uart.send("import binascii", timeout)
        logger.info("g")
        id = b1.python_uart.send(
            "binascii.hexlify(machine.unique_id()).decode()", timeout)
        logger.info("h")
        id = id.replace("'", "")
        assert len(id) == 16
    except:
        raise Exception


def test6():
    b1 = Board.get_single()


def read_boards_conf(boards_conf: str):
    data = json.loads(boards_conf)
    boards_in = list[BoardConfig]()
    for b in data['boards']:
        boards_in.append(BoardConfig(b))
    return boards_in


def discover_boards_with_config(boards_conf: str):
    logger.info("Get all boards")
    boards = Board.get_connected(boards_conf=read_boards_conf(boards_conf))
    return boards


def test7():
    boards = discover_boards_with_config(boards_all_props)
    logger.info(f"Boards found: {len(boards)}")
    for b in boards:
        logger.info(b)
    assert len(boards) != 0


def test8():
    boards = discover_boards_with_config(boards_repl_no_sn)
    logger.info(f"Boards found: {len(boards)}")
    for b in boards:
        logger.info(b)
        assert b.__class__.__name__ != "MicroPythonBoard"


def test9():
    boards = discover_boards_with_config(boards_min_props)
    logger.info(f"Boards found: {len(boards)}")
    for b in boards:
        logger.info(b)
    assert len(boards) != 0


def test10():
    logger.info("Get MicroPython boards")
    allow_list = ['MicroPythonBoard']
    boards = Board.get_connected(
        allow_list, read_boards_conf(boards_all_props))
    logger.info(f"Boards found: {len(boards)}")
    i = 0
    for b in boards:
        logger.info(b)
        assert "Micro" in str(b)


#
# uncomment tests that you want to run
#
# test1()
from micro_python_board import MicroPythonBoard
from lyra_board import LyraBoard
from zephyr_board import ZephyrBoard
# test2()
# test3()
# test4()
test5()
# test6()
test7()
test8()
test9()
test10()
