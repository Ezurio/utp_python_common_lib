from board import Board
from lc_util import logger_setup

logger = logger_setup(__file__)


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
    b1 = Board.get_by_com_port("COM8")
    logger.info(b1)
    assert b1 != None
    assert "Lyra" in str(b1)
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
        id.replace("'", "")
        assert len(id) == 16
    except:
        raise Exception


def test6():
    b1 = Board.get_single()


#
# uncomment tests that you want to run
#
# test1()
from lyra_board import LyraBoard
from zephyr_board import ZephyrBoard
test2()
# test3()
# test4()
# test5()
# test6()
