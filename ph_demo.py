# -*- coding: utf-8 -*-
"""
Created on Sun Jul 17 21:12:47 2022

@author: stefa
"""
import os
from pyhamilton import (HamiltonInterface,  LayoutManager, normal_logging, 
                        initialize, move_sequence, get_plate_gripper_seq, place_plate_gripper_seq,
                        move_plate_gripper_seq)

import logging

from ph_utils import pH_Module

import csv

lmgr = LayoutManager('Demo.lay')

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
        
        ph_module.calibration(solution_seq = 'seqCalibration_1', 
                              solution_ph = 4.0, 
                              dynamic_calibration = False, 
                              probe_pattern = '1111',
                              calibration_time = 1)
        
        ph_module.calibration(solution_seq = 'seqCalibration_2', 
                              solution_ph = 8.0, 
                              dynamic_calibration = False, 
                              probe_pattern = '1111',
                              calibration_time = 1)
        
        output = ph_module.measure(solution_seq, '1111')
        
        place_plate_gripper_seq(ham_int, 'seqpH_Module_0001', tool_sequence = 'COREGripTool_1000ul_0001')

        calibration_data_list = []
        for i in range(4):
            data = ph_module.request_calibration(probe_number = i)
            calibration_data_list.append(data)
        
        with open('dict.csv', 'w') as csv_file:  
            writer = csv.writer(csv_file)
            for key, value in calibration_data_list[0].items():
                writer.writerow([key, value])

