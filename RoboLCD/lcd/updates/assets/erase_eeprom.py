import serial
import time
class Erase_eeprom():

    def __init__(self):
        self.setup_serial()

    def setup_serial(self):
        with serial.Serial() as self.ser:
            time.sleep(5)
            self.ser.baudrate = 250000
            self.ser.port = ('/dev/ttyACM0')  # open serial port
            self.ser.open()
            self.ser.setDTR(False) # Drop DTR
            time.sleep(0.03)    # Read somewhere that 22ms is what the UI does.
            self.ser.setDTR(True)  # UP the DTR back


            time.sleep(5) #sleep to let the arduino catch up
            for x in range (0,100):
                line = "echo:SD init fail\n"
                ard_line = self.ser.readline()
                print(ard_line)
                if ard_line == line:
                    break

            print("Writing M105")
            val = "M105\n"
            written = self.ser.write(val)
            print(written)  

            print(self.ser.readline()) #wait for the ok command
            
            print("Writing M502")
            val = "M502\n"
            written = self.ser.write(val)
            print(written)  
            
            print(self.ser.readline()) # wait for the confirmation
            print(self.ser.readline()) # wait for the ok command

            print("Writing M500")
            val = "M500\n"
            written = self.ser.write(val)
            print(written)  
            
            print(self.ser.readline()) # wait for the confirmation
            print(self.ser.readline()) # wait for the ok command


            print("Closing Connection")
            self.ser.close()
            print("Connection Closed")
  
           


ee = Erase_eeprom()