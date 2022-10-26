# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 21:48:52 2022

@author: stefa
"""

import os
from pyhamilton import (HamiltonInterface,  LayoutManager, normal_logging, 
                        initialize, move_sequence, get_plate_gripper_seq, place_plate_gripper_seq,
                        move_plate_gripper_seq)

from pyhamilton.pH_command_wrappers import (ph_washer_wash,ph_dryer_start, ph_dryer_stop, ph_calibrate, ph_sleep,
                                            ph_wakeup, ph_calibrate_dynamically, 
                                            ph_measure, ph_initialize, ph_request_calibration)
import logging
import time




class pH_Module():
    def __init__(self, ham_int, module_id, comport, simulate, default_temperature = 25.0):
        self.hamilton = ham_int
        self.module_id = module_id
        self.default_temperature = default_temperature
        ph_initialize(self.hamilton, comport = comport, simulate = simulate)
        
    def measure(self, solution_seq, probe_pattern):
        move_plate_gripper_seq(self.hamilton, solution_seq)
        ph_wakeup(self.hamilton, self.module_id)
        output = ph_measure(self.hamilton, 
                            module_id = self.module_id, 
                            temperature = self.default_temperature, 
                            probePattern = probe_pattern)
        ph_sleep(self.hamilton, module_id = self.module_id)
        self.wash_and_dry('seqWash_Module', 'seqDryer_Module', cycle_num = 2, dry_time = 3)
        return output
    
    def wash_and_dry(self, wash_seq, dry_seq, cycle_num, dry_time):
        move_plate_gripper_seq(self.hamilton, wash_seq)
        ph_washer_wash(self.hamilton, module_id=self.module_id, cycle_num = cycle_num)
        move_plate_gripper_seq(self.hamilton, dry_seq)
        ph_dryer_start(self.hamilton, module_id = self.module_id)
        time.sleep(dry_time)
        move_sequence(self.hamilton, dry_seq, 0, 0, 20)
        move_plate_gripper_seq(self.hamilton, dry_seq)
        time.sleep(dry_time)
        ph_dryer_stop(self.hamilton, self.module_id)
        ph_sleep(self.hamilton, module_id = self.module_id)
        
    def calibration(self, solution_seq, solution_ph, dynamic_calibration, probe_pattern, calibration_time):
        
        move_plate_gripper_seq(self.hamilton, solution_seq)
        ph_wakeup(self.hamilton, module_id = self.module_id)
            #_Success or moveback        
        if not dynamic_calibration:
            time.sleep(calibration_time)
            ph_calibrate(self.hamilton, 
                         module_id = self.module_id, 
                         cal_level = 0, 
                         cal_value = solution_ph, 
                         cal_temperature = self.default_temperature, 
                         probe_pattern = '1111')
            
            
        else:
            ph_calibrate_dynamically(self.hamilton, 
                                     module_id = self.module_id, 
                                     variance = 1, 
                                     timeout = 20, 
                                     cal_level = 0, 
                                     cal_value = solution_ph, 
                                     cal_temperature = self.default_temperature,
                                     probe_pattern = '1111')
        
            self.wash_and_dry('seqWash_Module', 'seqDryer_Module', cycle_num = 2, dry_time = 3)
            ph_sleep(self.hamilton, module_id = 0)
    
    def request_calibration(self, probe_number):
        calibration_dictionary = {}
        calibration_data = ph_request_calibration(self.hamilton, self.module_id, probe_number)
        calibration_dictionary['LowValue'] = calibration_data[0]
        calibration_dictionary['LowVoltage'] = calibration_data[1]
        calibration_dictionary['HighValue'] = calibration_data[2]
        calibration_dictionary['HighVoltage'] = calibration_data[3]
        calibration_dictionary['Temperature'] = calibration_data[4]
        calibration_dictionary['Offset'] = calibration_data[5]
        calibration_dictionary['Slope'] = calibration_data[6]
        calibration_dictionary['Ratio'] = calibration_data[7]
        return calibration_dictionary
