import subprocess
from kivy.logger import Logger
import re
from .. import roboprinter
import os
import octoprint.filemanager
import os.path




class Meta_Reader():
    def __init__(self, _filename):
        self.filename = _filename
        self.gcode_name = os.path.basename(_filename)
        #.get_metadata(octoprint.filemanager.FileDestinations.LOCAL, self.gcode_name)
        self.octo_meta = roboprinter.printer_instance._file_manager
        
        

    def detirmine_slicer(self):
        cura = ";Generated with Cura_SteamEngine ([0-9.]+)"
        simplify3d = "Simplify3D"
        meta = None

        #read first 10 lines to detirmine slicer
        with open(self.filename, 'r') as file:
            for x in range(0,10):
                line  = file.readline()
            
                _cura = re.findall(cura, line)
                _simplify = re.findall(simplify3d, line)
            
                if _cura != []:
                    Logger.info("Sliced with Cura")
                    meta = self.cura_meta_reader()
                    break
                elif _simplify != []:
                    Logger.info("Sliced with Simplify 3D")
                    meta = self.simplify_meta_reader()
                    break
               
        file.close()
        if meta == None:
            meta = {
                'layer height' : "--",
                'layers' : "--",
                'infill' : "--"
            }
        self.save_data(meta)
        return meta

    #This function will check the filename against saved data on the machine and return saved meta data
    def check_saved_data(self):
        saved_data = self.octo_meta.get_metadata(octoprint.filemanager.FileDestinations.LOCAL, self.gcode_name)


    
        if 'robo_data' in saved_data:
            return saved_data['robo_data']
        else:
            return False

    #This function will save meta data to the machine
    def save_data(self, data):
        self.octo_meta.set_additional_metadata(octoprint.filemanager.FileDestinations.LOCAL,
                                               self.gcode_name,
                                               'robo_data',
                                               data)
        

    #This method reads the file to get the unread meta data from it. if there is none then it returns nothing
    def cura_meta_reader(self):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        meta = {}

        cura_lh = "layer_height = ([0-9.]+)"
        cura_ls = ";LAYER_COUNT:([0-9.]+)"
        cura_in = "sparse_density = ([0-9.]+)"

        _filename = self.filename
        output_filename = "/home/pi/."+ self.gcode_name+".txt"

        #read first 200 lines for Layer height
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    _cura_ls = re.findall(cura_ls, line)
                    _cura_lh = re.findall(cura_lh, line)
                    _cura_in = re.findall(cura_in, line)
    
                    if _cura_lh != []:
                        _layer_height = float(_cura_lh[0])                
    
                    if _cura_ls != []:
                        
                        _layers = int(_cura_ls[0])

                    if _cura_in != []:
                        
                        _infill = float(_cura_in[0])


        file.close()
        
        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill
        }
        return meta

    #This method reads the file to get the unread meta data from it. if there is none then it returns nothing
    def simplify_meta_reader(self):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        meta = {}

        s3d_lh = ";   layerHeight,([0-9.]+)"
        s3d_ls = "; layer ([0-9.]+)"
        s3d_in = ";   infillPercentage,([0-9.]+)"

        _filename = self.filename
        output_filename = "/home/pi/."+ self.gcode_name+".txt"

        #read first 200 lines for Layer height
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    
                    _s3d_lh = re.findall(s3d_lh, line)
                    _s3d_ls = re.findall(s3d_ls, line)
                    _s3d_in = re.findall(s3d_in, line)
    
                    if _s3d_lh != []:
                        _layer_height = float(_s3d_lh[0])
    
                    if _s3d_ls != []:
                        _layers = int(_s3d_ls[0])

                    if _s3d_in != []:
                        _infill = int(_s3d_in[0])
                    

        file.close()

        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill
        }
        return meta


    