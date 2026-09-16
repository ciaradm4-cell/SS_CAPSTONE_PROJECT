# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 12:46:52 2017

@author: Joe McCauley (joe.mccauley@tcd.ie)

This file includes file name vaieavles needed to run the SkyMultimap.py code. It should reside in the same folder as the SkyMultimap.py file
it must include the following string variables in the following format:
antennafile = <full path to the antennafile file> (a string value)
ihbadeltafile = <full path to the ihbadelta file> (a string value)
mode3caldata = <full path to the mode 3 calibration data file> (a string value)
mode5caldata = <full path to the mode 5 calibration data file> (a string value)
mode7caldata = <full path to the mode 7 calibration data file> (a string value)

Variable names must be exactly as entered above. Typos will break the code!
"""

antennafile='/Matlab/AntennaFields/IE613-AntennaField.conf'
ihbadeltafile='/Matlab/iHBADeltas/IE613-iHBADeltas.conf'
mode3caldata = '/Matlab/caltables/data/CalTable-613-LBA_INNER-10_90.dat'
mode5caldata = '/Matlab/caltables/data/CalTable-613-HBA-110_190.dat'
mode7caldata = '/Matlab/caltables/data/CalTable-613-HBA-210_250.dat'

