# Pipeline debugging notes 

### --- WED 16/09 --- ###

## process_path()
- Meant to fix Windows backslash paths, but regex is broken (matches digit+dd, not backslash+3digits)
- Harmless on Mac paths, so leaving as-is for now

## process_files()
- Takes a folder, globs for *xst.dat files inside it
- datasource needs trailing slash or glob finds nothing!! Could make a note or error message for that 

## SkyMultiMap_vars.py
- hardcoded all of these filepaths for now to get the script to run but will want this to be improved

## get_matplotlib_ver()
- This lives in the plotallsky.py file. It basically checks what version of matplotlib is being used for plotting purposes. This might be a bit redundant now since I doubt anything older is used. It checks if it's older than 2.0.2 by checking if the version is <=202. 
- It broke because it only works if every number in the version type is a single digit. Since we're now at 3.11.1 this breaks and it tries to interpret int('.') which breaks because it cannot be converted to an integer.
- Have changed this so that now it splits the [3, 11, 1] based on '.' with .split


### --- THURS 17/09 --- ###

## process_files()
- Takes datasource from the command line and globs over all of the xst files within the folder. It counts how many there are to be processed.

## save2csv()
- Saves each xst file as a csv file. 
- datafile is one of these filenames. If the datasource is a dir, the CreatAllSky runs for datafile in filenames.


### --- MON 21/09 --- 

## acm2skyimage()
- antenna correlation matrix -> sky image 
- skymap is a map of the power. calculates beamformed power and assigns it to a pixel by taking the amplitude of the voltage squared averaed over time which is the power?

## CreateAllSky()
- sets up the all-sky image by making a field and masking outside the circle that represents the horizon
- uses station rotation and calls acm2skyimage() to get the skymap
- separates by X and Y polarisation
- also calls PlotAllSky.main for te actual plotting

## parseiHBAField()
- reads the antenna positions from the LOFAR config files
- applies the relevant offsets and identifies the array configuration before extracting the station's geographic posiyion to get a rotation matrix out
- this function reads antennafield.conf and iHBADeltas.conf which is the element offset info and it combines them to get the antenna coords
