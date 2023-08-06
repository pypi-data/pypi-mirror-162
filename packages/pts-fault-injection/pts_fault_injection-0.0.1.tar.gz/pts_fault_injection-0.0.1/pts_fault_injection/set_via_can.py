from pprint import pprint
import can
import time
import cantools
import os
import json
import platform
import sys
from cantools.database.can.signal import NamedSignalValue

'''
Please Define Boad to test here !!!!
'''
BOARD_TO_TEST = "StandardSignal"  # AnalogSignal  BusSignal HVSignal
dac_setpoints = dac_setpoints = [-1, -1, -1, -1, -1, -1, -1, -1]  # 8 DAC Channels

dac_mapping = {0: 9,
               1: 1,
               2: 5,
               3: 3,
               4: 4,
               5: 5,
               6: 6,
               7: 7}  # DAC Channel : Message Channel


# Usage with PEAK CAN Dongle
can.rc['interface'] = 'pcan'
can.rc['channel'] = 'PCAN_USBBUS3'
can.rc['bitrate'] = 500000
can0 = can.interface.Bus()
can0.flush_tx_buffer()  # Reset transmit after start

can_db = cantools.database.Database()
dbc_dir = "./dbc/"
print(f"Searching for DBCs in {dbc_dir}")
for file in os.listdir(dbc_dir):
    if file.endswith(".dbc"):
        print(f"adding {file}")
        can_db.add_dbc_file(os.path.join(os.getcwd(), dbc_dir + file))


def send_can_message(msg_name, commands):
    try:
        cmd_message = can_db.get_message_by_name(msg_name)
    except Exception as e:
        print(f"ERROR: Message {msg_name} not found in Databases")
        print(e)
        return None

    # prepare a message with all signals
    signals = {}
    for signal in cmd_message.signals:
        if signal.name in commands:
            signals[signal.name] = commands[signal.name]
        else:
            signals[signal.name] = 0

    message = can.Message(arbitration_id=cmd_message.frame_id,
                          data=cmd_message.encode(signals, strict=False),
                          is_extended_id=False)
    # print(f"sending message {message}")
    can0.send(message)


def set_dac_value(channel, value):
    """Short summary.
    creates a can message out of the  dac state and sends it to the can connector

    CAN Message is DAC_BMS_Cntrl , ID 0x220
    Be aware of a weird channel mapping
    """
    dac_setpoints[channel] = value
    cmd = {}
    # Generate Signal name DAC_BMS_Cntrl_XX_YY_Voltage
    channel_msg = dac_mapping[channel] - 1
    dac_no = str(channel_msg // 4 + 1).zfill(2)  # Calculate Dac index, each dac has 4 channels
    ch_no = str((channel_msg % 4) + 1).zfill(2)  # channel is mod 4, both have to be filled to two digits
    mux = (0x10 * (channel_msg // 4)) + (channel_msg % 4)  # mux is 0-3 + 0x10 after each 4 channels
    cmd = {'DAC_BMS_Cntrl_Channel': mux, f"DAC_BMS_Cntrl_{dac_no}_{ch_no}_Voltage": value}
    # print(cmd)
    send_can_message("DAC_BMS_Cntrl", cmd)


def send_relay_can_message(card, data):
    mux_name = "RC_cntrl" + str(card).zfill(2)
    cmd = {'RC_mux': card, mux_name: data}
    send_can_message("RC_Cntrl", cmd)


def send_cmb_relay_can_message(cell, type, val):
    cmd = {f'RCCMBCntrl_CV{cell}_{type}': val}
    send_can_message("RCCMBCntrl", cmd)


def check_card(card, relays=None):
    if card > 7:
        return
    if range == None:
        max_relays = [32, 32, 32, 32, 48, 48, 32]  # max relays of cards
        relays = range(max_relays[card])
    if card == 4:  # analog card also set dac
        for ch in range(8):
            set_dac_value(ch, 2)
    for relay_no in relays:
        rly_set = 1 << (relay_no)
        print(f"Setting Card {card}, relay {relay_no}")
        print(bin(rly_set))
        send_relay_can_message(card, rly_set)
        time.sleep(0.5)
        send_relay_can_message(card, 0)
        time.sleep(0.1)


def test_standard_signal_card1():
    used_ports = list(range(15)) + list(range(16, 31))  # zero based
    check_card(1, used_ports)


def test_standard_signal_card2():
    used_ports = list(range(15)) + list(range(16, 31))  # zero based
    check_card(2, used_ports)


def test_standard_signal_card3():
    used_ports = list(range(15)) + list(range(16, 31))  # zero based
    check_card(3, used_ports)


def test_standard_signal_card4():
    used_ports = list(range(15)) + list(range(16, 31))  # zero based
    check_card(4, used_ports)


def test_analog_signal_card():
    used_ports = list(range(32)) + list(range(32, 39)) + list(range(40, 48))  # zero based
    check_card(4, used_ports)


def test_bus_signal_card():
    used_ports = list(range(3 * 16))  # zero based
    check_card(5, used_ports)


def test_cell_fault_board():
    for cell in range(18):
        print(f"Testing Open Circiut on cell {cell}")
        send_cmb_relay_can_message(cell, "OC", 1)
        time.sleep(0.5)
        send_cmb_relay_can_message(cell, "OC", 0)
        time.sleep(0.1)

    for cell in range(18):
        print(f"Testing High Impedance on cell {cell}")
        send_cmb_relay_can_message(cell, "HImp", 1)
        time.sleep(0.5)
        send_cmb_relay_can_message(cell, "HImp", 0)
        time.sleep(0.1)


#####################
##  Main Function  ##
#####################
if __name__ == '__main__':
    args = sys.argv
    if args and len(args) > 1 and args[1] == "-c":
        BOARD_TO_TEST = args[2]

    funcs = {
        "AnalogSignal": test_analog_signal_card,
        "StandardSignal1": test_standard_signal_card1,
        "StandardSignal2": test_standard_signal_card2,
        "StandardSignal3": test_standard_signal_card3,
        "StandardSignal4": test_standard_signal_card4,
        "BusSignal": test_bus_signal_card,
        "CellFault": test_cell_fault_board
    }

    print(f"TESTING BOARD {BOARD_TO_TEST}")
    funcs[BOARD_TO_TEST]()
