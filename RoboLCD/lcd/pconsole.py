import octoprint.printer
from .. import roboprinter
import re
import signal
import time


class PConsole(octoprint.printer.PrinterCallback):



    position = []
    position_ready = False
    #dictionary for eeprom
    eeprom_ready = False
    steps_per_unit = {}
    maximum_feed_rate = {}
    maximum_acceleration = {}
    accelerations = {}
    advanced_variables = {}
    home_offset = {}
    PID = {}
    BPID = {}
    filament_settings = {}
    zoffset = {}
    eeprom = {}
    counter = 0
    t_counter = 2
    temperature = {}
    sent_M114 = False
    cur_time = 0

    busy = False
    temperature = {
                    'tool1': 0,
                    'tool1_desired': 0,
                    'tool2': 0,
                    'tool2_desired': 0,
                    'bed': 0,
                    'bed_desired': 0,
                    }

    def on_printer_add_message(self, data):

        ##roboprinter.printer_instance._logger.info(data)

        if data.find("echo:busy: processing") != -1:
            self.busy = True
        else:
            self.busy = False
        
        find_data = ['M92', 'M203', 'M201', 'M204', 'M205', 'M206', 'M301', 'M304', 'M200', 'M851', 'Z Offset']

        acceptable_finds = {
                            'M92': self.find_M92,
                            'M203': self.find_M203,
                            'M201': self.find_M201,
                            'M204': self.find_M204,
                            'M205': self.find_M205,
                            'M206': self.find_M206,
                            'M301': self.find_M301,
                            'M304': self.find_M304,
                            'M200': self.find_M200,
                            'M851': self.find_M851,
                            'Z Offset': self.find_zoffset

        }

        for query in find_data:
            found = data.find(query)

            if found != -1:
                #execute dictionary function
                acceptable_finds[query](data)
                break        

        #Disconnect and reconnect if Marlin stops because of bed heater issues
        printer_bed_error = 'Error:MINTEMP triggered, system stopped! Heater_ID: bed'
        printer_bed_error2 = "Error:Heating failed, system stopped! Heater_ID: bed"
        general_error = "Error:Printer halted. kill() called!"
        connection_error = "Error:No Line Number with checksum, Last Line: 0"

        if re.match(printer_bed_error, data) or re.match(printer_bed_error2,data) or re.match(general_error, data) or re.match(connection_error,data):
            roboprinter.printer_instance._logger.info("Disconnecting")
            roboprinter.printer_instance._printer.disconnect()
            time.sleep(2)
            roboprinter.printer_instance._logger.info("Reconnecting")
            roboprinter.printer_instance._printer.connect()

        #Find out if octoprint is not reporting a bed temp loss
        model = roboprinter.printer_instance._settings.get(['Model'])
        if model == "Robo R2":
            
            def find_temps():
                ext1 = -1
                ext1_dual = -1
                ext2 = -1
                bed = -1
                if data.find('T:') != -1:
                    ext1 = data.find('T:')
                if data.find('T0:') != -1:
                    ext_dual = data.find('T0:')
                if data.find('T1:') != -1:
                    ext2 = data.find('T1:')
                if data.find('B:') != -1:
                    bed = data.find('B:')

                #Dual Extrusion R2
                if ext1_dual != -1 and ext2 != -1 and bed != -1:
                    bed_s = temp[bed:ext1_dual]
                    bed = extract_data(bed_s)

                    self.temperature['bed'] = bed['current']
                    self.temperature['bed_desired'] = bed['desired']

                    ext1_s = temp[ext1_dual+2:ext2]
                    tool1 = extract_data(ext1_s)

                    self.temperature['tool1'] = tool1['current']
                    self.temperature['tool1_desired'] = tool1['desired']

                    ext2_s = temp[ext2+2:temp.find('@')]
                    tool2 = extract_data(ext2_s)

                    self.temperature['tool2'] = tool2['current']
                    self.temperature['tool2_desired'] = tool2['desired']


                    

                #Single Nozzle R2
                elif ext1 != -1 and bed != -1:
                    ext1_s = data[ext1:bed]
                    tool1 = extract_data(ext1_s)

                    self.temperature['tool1'] = tool1['current']
                    self.temperature['tool1_desired'] = tool1['desired']

                    bed_s = data[bed:data.find('@')]
                    bed = extract_data(bed_s)

                    self.temperature['bed'] = bed['current']
                    self.temperature['bed_desired'] = bed['desired']

                else:
                    roboprinter.printer_instance._logger.info("Model is R2 and we cannot find bed and extruder!!!")
                    roboprinter.printer_instance._logger.info(data)

            def extract_data(temp_string):
                temperature =  "[+-]?\d+(?:\.\d+)?"
                current_temp = re.findall(temperature, temp_string)

                temp = {
                        'current':current_temp[0],
                        'desired':current_temp[1]
                       }
                return temp

            #disconnect if the bed reports a negative number two times in a row
            if data.find('T:') != -1 and data.find('B:') != -1:
                
                find_temps()

                if float(self.temperature['bed']) < 0:
                    self.t_counter -= 1
                    roboprinter.printer_instance._logger.info(str(self.t_counter))
                    if self.t_counter == 0:
                        roboprinter.printer_instance._logger.info("Shutting down")
                        roboprinter.printer_instance._printer.disconnect()
                        self.t_counter = 2



        #get the position
        if self.sent_M114:
            p = "X:([-0-9.00]+)Y:([-0-9.00]+)Z:([-0-9.00]+)E:([-0-9.00]+)CountX:([-0-9]+)Y:([-0-9]+)Z:([-0-9]+)"
            temp_pos = re.findall(p, data.replace(" ", ""))
            if temp_pos != []:
                self.position = temp_pos[0]
                #roboprinter.printer_instance._logger.info('Position Update')
                #roboprinter.printer_instance._logger.info(str(self.position))
                self.position_ready = True
            finished_time = (time.time() - self.cur_time) * 1000
            roboprinter.printer_instance._logger.info("position getting it in " + str(finished_time) + " ms")

        

    #Steps Per Unit
    def find_M92(self, data):
        #roboprinter.printer_instance._logger.info("M92 "+ str(self.counter))
        p = "X([-0-9.00]+) Y([-0-9.00]+) Z([-0-9.00]+) E([-0-9.00]+)"
        spu = re.findall(p, data)
        if spu != []:
            self.steps_per_unit = {
                'X' : float(spu[0][0]),
                'Y' : float(spu[0][1]),
                'Z' : float(spu[0][2]),
                'E' : float(spu[0][3])
            }
            self.eeprom['steps per unit'] = self.steps_per_unit
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M92 getting it in " + str(finished_time) + " ms")

    #Maximum Feed Rate
    def find_M203(self, data):
        #roboprinter.printer_instance._logger.info("M203 "+ str(self.counter))
        p = "X([-0-9.00]+) Y([-0-9.00]+) Z([-0-9.00]+) E([-0-9.00]+)"
        mfr = re.findall(p, data)

        if mfr != []:
            self.maximum_feed_rate = {
                'X' : float(mfr[0][0]),
                'Y' : float(mfr[0][1]),
                'Z' : float(mfr[0][2]),
                'E' : float(mfr[0][3])
            }
            self.eeprom['max feed rate'] = self.maximum_feed_rate
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M203 getting it in " + str(finished_time) + " ms")

    #Maximun Acceleration
    def find_M201(self, data):

        p = "X([-0-9.00]+) Y([-0-9.00]+) Z([-0-9.00]+) E([-0-9.00]+)"
        ma = re.findall(p, data)
        if ma != []:
            #roboprinter.printer_instance._logger.info("M201 "+ str(self.counter))
            self.maximum_acceleration = {
                'X' : float(ma[0][0]),
                'Y' : float(ma[0][1]),
                'Z' : float(ma[0][2]),
                'E' : float(ma[0][3])
            }
            self.eeprom['max acceleration'] = self.maximum_acceleration
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M201 getting it in " + str(finished_time) + " ms")

    #Accelerations
    def find_M204(self, data):
        #roboprinter.printer_instance._logger.info("M204 "+ str(self.counter))
        p = "P([-0-9.00]+) R([-0-9.00]+) T([-0-9.00]+)"
        accel = re.findall(p, data)

        if accel != []:
            self.accelerations = {
                'P' : float(accel[0][0]),
                'R' : float(accel[0][1]),
                'T' : float(accel[0][2])

                }
            self.eeprom['accelerations'] = self.accelerations
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M204 getting it in " + str(finished_time) + " ms")

    #advanced variables
    def find_M205(self, data):
        #roboprinter.printer_instance._logger.info("M205 "+ str(self.counter))
        p = "S([-0-9.00]+) T([-0-9.00]+) B([-0-9.00]+) X([-0-9.00]+) Z([-0-9.00]+) E([-0-9.00]+)"
        av = re.findall(p, data)
        if av != []:
            self.advanced_variables = {
                'S' : float(av[0][0]),
                'T' : float(av[0][1]),
                'B' : float(av[0][2]),
                'X' : float(av[0][3]),
                'Z' : float(av[0][4]),
                'E' : float(av[0][5])
            }
            self.eeprom['advanced variables'] = self.advanced_variables
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M205 getting it in " + str(finished_time) + " ms")

    #home offset
    def find_M206(self, data):
        p = "X([-0-9.00]+) Y([-0-9.00]+) Z([-0-9.00]+)"
        ho = re.findall(p, data)

        if ho != []:
            self.home_offset = {

                'Z' : float(ho[0][2])
            }
            self.eeprom['home offset'] = self.home_offset
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M206 getting it in " + str(finished_time) + " ms")


    #PID settings
    def find_M301(self, data):
        #roboprinter.printer_instance._logger.info("M301 "+ str(self.counter))
        p = "P([-0-9.00]+) I([-0-9.00]+) D([-0-9.00]+)"
        pid = re.findall(p, data)

        if pid != []:
            self.PID = {
                'P' : float(pid[0][0]),
                'I' : float(pid[0][1]),
                'D' : float(pid[0][2])
            }
            self.eeprom['PID']  = self.PID
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M301 getting it in " + str(finished_time) + " ms")

    def find_M304(self, data):
        #roboprinter.printer_instance._logger.info("M301 "+ str(self.counter))
        p = "P([-0-9.00]+) I([-0-9.00]+) D([-0-9.00]+)"
        pid = re.findall(p, data)

        if pid != []:
            self.BPID = {
                'P' : float(pid[0][0]),
                'I' : float(pid[0][1]),
                'D' : float(pid[0][2])
            }
            self.eeprom['BPID'] = self.BPID
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M304 getting it in " + str(finished_time) + " ms")


    #filament settings

    def find_M200(self, data):
        #roboprinter.printer_instance._logger.info("M200 "+ str(self.counter))
        p = "D([-0-9.00]+)"
        fs = re.findall(p, data)

        if fs != []:
            self.filament_settings = {
                'D' : float(fs[0])
            }
            self.eeprom['filament settings'] = self.filament_settings
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M200 getting it in " + str(finished_time) + " ms")

    #Zoffset
    def find_M851(self, data):

        p = "Z([-0-9.00]+)"
        zo = re.findall(p, data)

        if zo != []:
            self.zoffset = {

                'Z' : float(zo[0])

            }
            self.eeprom['z offset'] = self.zoffset
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("M851 getting it in " + str(finished_time) + " ms")

        roboprinter.printer_instance._logger.info(str(self.eeprom))

            #roboprinter.printer_instance._logger.info("M851 "+ str(self.counter))

    #Zoffset update
    def find_zoffset(self,data):
        p = "Z Offset ([-0-9.00]+)"
        zo = re.findall(p, data)

        if zo != []:
            #roboprinter.printer_instance._logger.info('Zoffset Background Update ' + str(zo[0]))
            self.zoffset['Z'] =  float(zo[0])
            self.eeprom['z offset'] = self.zoffset
        finished_time = (time.time() - self.cur_time) * 1000
        roboprinter.printer_instance._logger.info("ZOffset getting it in " + str(finished_time) + " ms")

    def query_eeprom(self):
        self.cur_time = time.time()
        roboprinter.printer_instance._printer.commands('M501')

    def get_eeprom(self):
        self.counter = 0
        self.eeprom_ready = False
        roboprinter.printer_instance._printer.commands('M501')

        while (self.eeprom_ready == False):
            pass

        return self.eeprom
    def generate_eeprom(self):
        self.eeprom_ready = False
        roboprinter.printer_instance._printer.commands('M501')

    def get_old_eeprom(self):
        pass
        return self.eeprom

    def get_position(self):

        if not self.busy:
            self.sent_M114 = True
            self.cur_time = time.time()
            roboprinter.printer_instance._printer.commands('M114')
            
            while (self.position_ready == False):
                pass
    
            self.position_ready = False
            self.sent_M114 = False
            return self.position
        else:
            return False

        
    def initialize_eeprom(self):
        self.steps_per_unit = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.maximum_feed_rate = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.maximum_acceleration = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.accelerations = {
            'P' : 0,
            'R' : 0,
            'T' : 0
        }
        self.advanced_variables = {
            'S' : 0,
            'T' : 0,
            'B' : 0,
            'X' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.home_offset = {
            #'X' : 0,
            #'Y' : 0,
            'Z' : 0
        }
        self.PID = {
            'P' : 0,
            'I' : 0,
            'D' : 0
        }
        self.BPID = {
            'P' : 0,
            'I' : 0,
            'D' : 0
        }
        self.filament_settings = {
            'D' : 0
        }
        self.zoffset = {
            'Z' : 0
        }
        self.eeprom = {
            'steps per unit' : self.steps_per_unit,
            'max feed rate' : self.maximum_feed_rate,
            'max acceleration' : self.maximum_acceleration,
            'accelerations' : self.accelerations,
            'advanced variables' : self.advanced_variables,
            'home offset' : self.home_offset,
            'PID' : self.PID,
            'BPID': self.BPID,
            'filament settings' : self.filament_settings,
            'z offset' : self.zoffset
        }



pconsole = PConsole()
