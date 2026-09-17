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



