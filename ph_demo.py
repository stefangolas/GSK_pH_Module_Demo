# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 21:12:47 2022

@author: stefa
"""
import os
from pyhamilton import (HamiltonInterface,  LayoutManager, normal_logging, 
                        initialize, move_sequence, get_plate_gripper_seq, place_plate_gripper_seq,
                        move_plate_gripper_seq, ResourceType, Plate96)

import logging

from ph_utils import pH_Module
import sys


lmgr = LayoutManager('Demo.lay')

sample_plate = lmgr.assign_unused_resource(ResourceType(Plate96, 'Cos_96_Rd_0001'))


default_temperature = 25.0
calibration_time = 30.0
solution_seq = 'seqVerify'

if __name__ == '__main__': 
    with HamiltonInterface(simulate=True) as ham_int:
        normal_logging(ham_int, os.getcwd())
        initialize(ham_int)
        
        #pH Module Commands
        
        ph_module = pH_Module(ham_int, module_id = 0, comport = 1, simulate = True, default_temperature = 25.0)
        

        get_plate_gripper_seq(ham_int, 'seqpH_Module_0001', 39.0, 81.0, 90.0, 
                              lid = False, tool_sequence = 'COREGripTool_1000ul_0001')
        
        #ph_module.calibration(solution_seq = 'seqCalibration_1', 
        #                      solution_ph = 4.0, 
        #                      dynamic_calibration = False, 
        #                      probe_pattern = '1111',
        #                      calibration_time = 5)
        
        #ph_module.calibration(solution_seq = 'seqCalibration_2', 
        #                      solution_ph = 8.0, 
        #                      dynamic_calibration = False, 
        #                      probe_pattern = '1111',
        #                      calibration_time = 5)
        
        output = ph_module.measure([(sample_plate, 0)], '1111') #Integer indexing
        
        place_plate_gripper_seq(ham_int, 'seqpH_Module_0001', tool_sequence = 'COREGripTool_1000ul_0001')

        for i in range(1,5):
            data = ph_module.request_calibration(probe_number = i)
            print(data)
