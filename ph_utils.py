# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 21:48:52 2022

@author: stefa
"""

import os
from pyhamilton import (HamiltonInterface,  LayoutManager, normal_logging, 
                        initialize, move_sequence, get_plate_gripper_seq, place_plate_gripper_seq,
                        move_plate_gripper_seq, move_plate_gripper)

from pyhamilton import (ph_washer_wash,ph_dryer_start, ph_dryer_stop, ph_calibrate, ph_sleep,
                                            ph_wakeup, ph_calibrate_dynamically, ph_dryer_initialize, ph_washer_initialize,
                                            ph_measure, ph_initialize, ph_request_calibration)
import logging
import time
import sys




class pH_Module():
    def __init__(self, ham_int, module_id, comport, simulate, default_temperature = 25.0):
        self.hamilton = ham_int
        self.module_id = module_id
        self.default_temperature = default_temperature
        ph_initialize(self.hamilton, comport = comport, simulate = simulate)
        self.washer_module = ph_washer_initialize(self.hamilton, comport = comport, simulate=simulate)
        self.dryer_module = ph_dryer_initialize(self.hamilton, comport = comport, simulate=simulate)
        self.xdis = 0.0
        self.ydis = 0.0
        self.zdis = 0.0
        
    def handle_exceptions(f):
        from functools import wraps
        @wraps(f)
        def wrapper(self, *args, **kw):
           try:
               return f(self, *args, **kw)
           except Exception as e:
               print(str(e))
               place_plate_gripper_seq(self.hamilton, 'seqpH_Module_0001', tool_sequence='COREGripTool_1000ul_0001')
               sys.exit()
        return wrapper

        
    def measure(self, solution_pos, probe_pattern):
        move_plate_gripper(self.hamilton, solution_pos, xDisplacement = self.xdis,
                           yDisplacement = self.ydis, zDisplacement = self.zdis)
        ph_wakeup(self.hamilton, self.module_id)
        output = ph_measure(self.hamilton, 
                            module_id = self.module_id, 
                            temperature = self.default_temperature, 
                            probePattern = probe_pattern)
        ph_sleep(self.hamilton, module_id = self.module_id)
        self.wash_and_dry('seqWash_Module', 'seqDryer_Module', cycle_num = 2, dry_time = 3)
        return output
    
    @handle_exceptions
    def wash_and_dry(self, wash_seq, dry_seq, cycle_num, dry_time):
        move_plate_gripper_seq(self.hamilton, wash_seq)
        ph_washer_wash(self.hamilton, module_id=self.module_id, cycle_num = cycle_num)
        move_plate_gripper_seq(self.hamilton, dry_seq)
        ph_dryer_start(self.hamilton, module_id = 100)
        time.sleep(dry_time)
        move_sequence(self.hamilton, dry_seq, 0, 0, 20)
        move_plate_gripper_seq(self.hamilton, dry_seq)
        time.sleep(dry_time)
        ph_dryer_stop(self.hamilton, module_id = 100)
        ph_sleep(self.hamilton, module_id = self.module_id)
      
    @handle_exceptions
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
                         probe_pattern = probe_pattern)
            
            
        else:
            ph_calibrate_dynamically(self.hamilton, 
                                     module_id = self.module_id, 
                                     variance = 1, 
                                     timeout = 20, 
                                     cal_level = 0, 
                                     cal_value = solution_ph, 
                                     cal_temperature = self.default_temperature,
                                     probe_pattern = probe_pattern)
        
            self.wash_and_dry('seqWash_Module', 'seqDryer_Module', cycle_num = 2, dry_time = 3)
            ph_sleep(self.hamilton, module_id = 0)
    
    def request_calibration(self, probe_number):
        calibration_data = ph_request_calibration(self.hamilton, 1000, probe_number)
        return calibration_data
