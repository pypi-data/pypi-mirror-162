import can
import os
import cantools
import time
import logging
import sys

broadcast_id = 0x600
board_ids = {0: "Standard Signals 1",
             1: "Standard Signals 2",
             2: "Standard Signals 3",
             3: "Standard Signals 4",
             4: "Analog Signals",
             5: "Bus Signals",
             6: "HV Signals",
             9: "Contactor Card",
             10: "HV Box Card",
             14: "DAC Board",
             15: "Break Out Box",
             16: "CMB Faults"
             }


class FaultInjection:
    """
    Base class for the Fault Injection Box
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    def __init__(self, bus=None, dbc_dir="./dbc/"):
        self.bus = bus
        self.can_db = cantools.database.Database()
        logging.info(f"Searching for DBCs in {dbc_dir}")
        for file in os.listdir(dbc_dir):
            if file.endswith(".dbc"):
                logging.info(f"adding {file}")
                self.can_db.add_dbc_file(os.path.join(os.getcwd(), dbc_dir + file))

    def can_connection(self, interface, channel, bitrate):
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()

    def read_FW_Response(self):
        time.sleep(1)
        wait_time = 1 + time.time()
        msg = self.bus.recv(timeout=1)
        rdy_IDs = []
        msg_buf = {}
        fw_versions = {}
        print("Searching for ready controllers.")
        while wait_time > time.time():
            if msg != None and msg.dlc > 0:
                if msg.arbitration_id < 0x6FF and msg.arbitration_id > 0x600:
                    rdy_IDs.append(msg.arbitration_id)
                    msg_buf[msg.arbitration_id] = msg.data
                sys.stdout.write(".")
                sys.stdout.flush()
            msg = self.bus.recv(timeout=0.1)
        try:
            for id in rdy_IDs:
                fw_versions[id] = msg_buf[id].decode("ASCII")
        except Exception as e:
            raise Exception(f"\nError in finding FW versions for all responses {e}")
        return rdy_IDs, fw_versions

    def read_FW_Versions(self):
        # Writing FW Update Request
        logging.info("Using broadcast ID " + hex(broadcast_id))
        msg = can.Message(arbitration_id=broadcast_id, data=[ord('F'), ord('W'), ord('?'), 0, 0, 0, 0, 0],
                          is_extended_id=False)
        self.bus.send(msg)
        # Block until ready
        ids, fw_versions = self.read_FW_Response()
        str_id = []

        for id in ids:
            try:
                logging.info("\nFW Information from board: " + board_ids[id - broadcast_id - 1] + " with FW version: "
                             + str(fw_versions[id]))
            except Exception as e:
                pass
                # raise Exception(f"ERR: Could not read FW version: {e}")
            return fw_versions

###########################
####### Setup Script#######
###########################
# Set to True if you want to create a logfile
# create_log_file = False
# # bus.set_filters([{"can_id": 0x600, "can_mask": 0x700, "extended": False}])
#
# # create logger with 'flasher_application'
# logger = logging.getLogger('flasher')
# logger.setLevel(logging.DEBUG)
# # create file handler which logs even debug messages
# t = time.strftime("%Y%m%d-%H%M%S")
# if create_log_file:
#     fh = logging.FileHandler('spam' + t + '.log')
#     fh.setLevel(logging.DEBUG)
# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# # create formatter and add it to the handlers
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# if create_log_file:
#     fh.setFormatter(formatter)
# ch.setFormatter(formatter)
# # add the handlers to the logger
# if create_log_file:
#     logger.addHandler(fh)
# logger.addHandler(ch)
