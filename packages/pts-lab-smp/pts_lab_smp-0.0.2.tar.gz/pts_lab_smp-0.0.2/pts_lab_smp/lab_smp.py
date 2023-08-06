import logging
import time
import socket


class LabSmp:
    """
    Base class for the LAB SMP HV PSU
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    def __init__(self, host_addr, port):
        self.sock = None
        self.ls_psu = None
        self.resource_manager = None
        self.host_addr = host_addr
        self.port = port

    def open_connection(self):
        """
        Opens a TCP/IP connection to connect to the LAB SMP PSU
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host_addr, self.port))
            logging.info(f": Opening LAB-SMP Resource at {self.host_addr} and port {self.port}")
        except Exception as e:
            raise Exception(f": ERROR {e}: Could not open Resource")

    def close_connection(self):
        """
        Closes the TCP/IP connection to the TDK Lambda PSU
        """
        self.sock.close()
        print(f": Closing serial connection!")

    def clear_status(self):
        """
        This command deletes the status byte
        :return: No return
        """
        self.sock.send(f'CLS')
        time.sleep(0.3)
        logging.info(f": CLEAR STATUS")
        print(f"CLEAR STATUS")

    def clear_device(self):
        """
        This command resets the initialization data.
        :return: No return value.
        """
        self.sock.send(f'DCL')
        time.sleep(0.3)
        logging.info(": CLEAR DEVICE")
        print(": CLEAR DEVICE")

    def identification_number(self):
        """
        This command checks the identification number
        :return: str: Identification number
        """
        self.sock.send(b'ID \n')
        time.sleep(0.3)
        idn = self.sock.recv(1024)
        logging.info(f": Identification number: {idn.decode()}")
        print(f": Identification number: {idn.decode()}")
        return str(idn.decode())

    def optical_idn(self):
        """
        This command checks the optical identification number
        :return: str: optical idn
        """
        self.sock.send(b'*OPT? \n')
        time.sleep(0.3)
        optical_idn = self.sock.recv(1024)
        logging.info(f": Optical Identification Query: {optical_idn.decode()}")
        print(f": Optical Identification Query: {optical_idn.decode()}")
        return str(optical_idn.decode())

    def interface_status(self):
        """
        This command checks the interface status
        :return: str: Interface status
        """
        self.sock.send(b'*STB? \n')
        time.sleep(0.3)
        interface_status = self.sock.recv(1024)
        logging.info(f": Interface Status: {interface_status.decode()}")
        print(f": Interface Status: {interface_status.decode()}")
        return str(interface_status.decode())

    def local_lockout(self):
        """
        This command deactivates the LOCAL button
        :return: None return
        """
        self.sock.send(b'LLO \n')
        logging.info(": LOCAL button Deactivated")
        print(f": LOCAL button deactivated")

    def activate_local(self):
        """
        This command activates the front panel operation and also resets Local lockout button
        :return: None return
        """
        self.sock.send(b'GTL \n')
        logging.info(": Front panel activated")
        print(f": Front panel activated")

    def toggle_device_output(self, state):
        """
        This function enables/disables the LAB SMP output setting -
        S|1: puts the unit in Standby, Output is disabled
        R|0: disables Standby mode, Output is enabled
        :param state: the required output state
        :return: Success or failure
        """
        states = {'R': 'ENABLED', 'S': 'DISABLED'}
        self.sock.send(b'SB \n')
        resp = self.sock.recv(1024)
        check_standby = resp.decode().rstrip().split(",")[-1]
        if check_standby != str(state):
            new_state = f'SB,{state} \n'
            self.sock.send(new_state.encode())
            self.sock.send(b'SB \n')
            ack = self.sock.recv(1024)
            ack2 = ack.decode().rstrip().split(",")[-1]
            if ack2 == 'S':
                logging.info(f": PSU Output : DISABLED")
                print(f": PSU Output : DISABLED")
            elif ack2 == 'R':
                logging.info(f": PSU Output : ENABLED")
                print(f": PSU Output : ENABLED")
        else:
            logging.info(f": PSU Output is already: {states[str(state)]}")
            print(f": PSU Output is already: {states[str(state)]}")
        return True

    def get_interface(self, interface_id):
        """
        This command will query the three interface parameters (possibly only one available)
        :param interface_id: PC1 - Serial, PC2 - LAN, PC3 - GPIB (Empty)
        :return: list: Interface Parameters
        """
        self.sock.send(str(interface_id+'\n').encode())
        time.sleep(0.3)
        comm_intf = self.sock.recv(1024)
        logging.info(f": Query of the interface: {comm_intf.decode()}")
        print(f": Query of the interface: {comm_intf.decode()}")
        return str(comm_intf.decode())

    def set_voltage(self, volt):
        """
        This command will query the three interface parameters (possibly only one available)
        :param volt: output voltage in Volts
        :return: list: Interface Parameters
        """
        b_volt = 'UA,'+str(volt)
        self.sock.send(b_volt.encode()+b'\n')
        time.sleep(0.3)
        logging.info(f": Voltage set to: 3")

    def set_current_limit(self, curr_limit):
        """
        This command will query the three interface parameters (possibly only one available)
        :param curr_limit: current limit in Amps
        :return: list: Interface Parameters
        """
        b_curr_lim = 'IA,'+str(curr_limit)
        self.sock.send(b_curr_lim.encode()+b'\n')
        time.sleep(0.3)
        logging.info(f": Current limit set to: {curr_limit}")

    def set_interface_params(self):
        """
        This command will set the different interface parameters
        ONLY TO BE USED WITH SERIAL RS232 CONNECTION - PC1
        :return: No return value
        """
        self.sock.send(b'PC1,9600,N,8,2,N,E \n')
        time.sleep(0.3)
        self.sock.send(b'SS \n')
        logging.info(f": Interface Arguments changed")
        print(f": Interface Arguments changed")

    def check_voltage_limit(self):
        """
        This function reads maximum adjustable voltage limitation
        :return: float: Voltage limit in Volts
        """
        self.sock.send(b'LIMU \n')
        volt_limit = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Maximum adjustable voltage limit : {volt_limit} Volts")
        print(f": Maximum adjustable voltage limit : {volt_limit} Volts")
        return str(volt_limit)

    def check_current_limit(self):
        """
        This function reads maximum adjustable current limitation
        :return: float: Current limit in Amps
        """
        self.sock.send(b'LIMI \n')
        curr_limit = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Maximum adjustable current limit : {curr_limit} Amps")
        print(f": Maximum adjustable current limit : {curr_limit} Amps")
        return str(curr_limit)

    def check_unit_output(self):
        """
        This function reads maximum unit output
        :return: float: Unit output in Watts
        """
        self.sock.send(b'LIMP \n')
        unit_out = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Maximum unit output : {unit_out} Watts")
        print(f": Maximum unit output : {unit_out} Watts")
        return str(unit_out)

    def check_resistance_range(self):
        """
        This function reads the adjustable range for Ri in UIR mode
        :return: tuple: Resistance in Ohms
        """
        self.sock.send(b'LIMR \n')
        r_limit = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Limit of Ri in UIR mode : {r_limit} Ohms")
        print(f": Limit of Ri in UIR mode : {r_limit} Ohms")
        return str(r_limit)

    def measure_output_voltage(self):
        """
        This function measures present output voltage
        :return: float: Programmed output voltage in Volts
        """
        self.sock.send(b'MU \n')
        meas_volt = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Present Output Voltage: {meas_volt} Volts")
        print(f": Present Output Voltage: {meas_volt} Volts")
        return str(meas_volt)

    def get_ovp_limit(self):
        """
        This command displays the present set over-voltage protection point.
        :return: Over-voltage range
        """
        self.sock.send(b'OVP \n')
        ovp = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Over-voltage protection point: {ovp} Volts")
        print(f": Over-voltage protection point: {ovp} Volts")
        return str(ovp)

    def measure_output_current(self):
        """
        This function measures present output current
        :return: float: Programmed output Current in Amps
        """
        self.sock.send(b'MI \n')
        meas_curr = self.sock.recv(1024).decode().rstrip().split(",")[-1]
        logging.info(f": Present Output Current: {meas_curr} Amps")
        print(f": Present Output Current: {meas_curr} Amps")
        return str(meas_curr)

    def reset(self):
        """
        This function Resets hardware/Instrument
        :return: (no return value)
        """
        self.sock.send(b'*RST \n')
