# -*- coding: utf-8 -*-
"""
Created on Sat Dec 02 09:53:39 2017

@author: Joe McCauley (joe.mccauley@tcd.ie)
Originally written for Python 2.7
Upgraded for Python 3.8 April 2021
uses matplotlib v2.0.2 or 2.1.1, NOT 2.1.0
This script can plot a suitably prepared matrix made from LOFAR xst data but would more usually be called from a script called SkyMultiMap.py

"""
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
import re

#supress the warning about vector transforms so as not to clutter the doc build log
import warnings

warnings.filterwarnings('ignore',module='astropy.coordinates.baseframe')
#from .exceptions import TargetNeverUpWarning, TargetAlwaysUpWarning

from astropy.utils.iers import conf
conf.auto_max_age = None

def update_annot( xdata, ydata ):
    y, x = pol2cart( ydata/180, xdata, px )
    annot.xy = ( xdata, ydata )
    text = 'Az=' + str( round( xdata * 180 / np.pi, 1 ) )+  ', El=' + str( round( np.arccos( ydata/180 ) * 180/np.pi, 1) ) + u'\xb0' + '\nInt.=' + '{:.3E}'.format((rawdata[int(y),int(x)]))
    annot.set_text( text )
    annot.get_bbox_patch().set_alpha( 0.4 )

def onclick(event): # Callbacks only work on the last plot made
    vis = annot.get_visible()
    if event.inaxes == ax:
        if vis == False:
            update_annot( event.xdata, event.ydata )
            annot.set_visible( True )
            event.canvas.draw()
        else:
            annot.set_visible( False )
            event.canvas.draw()
            #fig.canvas.draw_idle()

def hover(event): # Callbacks only work on the last plot made
    global cb_cursor
    if event.xdata:# if you have 2 plots on screen, for some reason the hover event is triggered if you hover over the first one giving errors
      if event.inaxes == ax:
        y,x = pol2cart( event.ydata / 180, event.xdata, px )
        z=rawdata[ int( y ), int( x ) ]
        zline = ( z - np.nanmin( rawdata ) ) / np.nanmax( rawdata-np.nanmin( rawdata ) ) # calculate where to put the z line
        cb_cursor.pop( 0 ).remove() #loose the old line
        cb_cursor = ax_cb.plot( [ 0, 1 ], [ zline, zline ], 'w-' ) #plot the new one
        event.canvas.draw()
        #fig.canvas.draw_idle()

def onaxesleave(event): # Callbacks only work on the last plot made
    global cb_cursor
    if event.inaxes == ax:
        cb_cursor.pop(0).remove()
        cb_cursor = ax_cb.plot([0, 1],[0, 0], 'k-')
        event.canvas.draw()

def get_matplotlib_ver(): # convert the string version to a number for comparison
    ver_str_full = mpl.__version__
    ver_str = ver_str_full.split('.')
    ver_num = int(ver_str[0])*100 + int(ver_str[1])*10 + int(ver_str[2])
    return ver_num

def CalcFreq(rcumode, subband):
    if rcumode == 5:
        freqoff = 100e6;
        basefreq = 200.0;
    elif rcumode == 6:
        freqoff = 160e6;
        basefreq = 160.0;
    elif rcumode == 7:
        freqoff = 200e6;
        basefreq = 200.0;
    else:
        freqoff = 0;
        basefreq = 200.0;
    freq = ( ( basefreq / 1024 ) * subband + ( freqoff / 1e6 ) )
    return freq

def cart2pol( x, y ):
    rho = np.sqrt( x ** 2 + y ** 2)
    phi = np.arctan2( y, x )
    return( rho, phi )

def pol2cart( rho, phi, pixels ):
    x = rho * np.cos( phi )
    y = rho * np.sin( phi )
    x=( pixels/2 )-( pixels/2 )*x
    y=( pixels/2 )-( pixels/2 )*y
    return( x, y )

def process_path( datafile )  : #converts '\' to '/' in paths pasted in from windows PCs
    datafile=re.sub( r"\ddd", "/ddd", datafile ) # just in case you have a '/nnn' in the string which might be interpeted as an escape sequence
    #datafile=re.sub( r"\\", "/", datafile )
    #datafile=os.path.normpath( datafile )
    return datafile

def main( datafile, data, rcumode, polarity, logplot, pixels, ol_col, grid_thick, back_color, fore_color, save_image, multiple_files, radial_label_angle, color_bar, obs_site, int_time ):

    global px
    px = pixels
    color_bar = 1
    if  'Birr' in obs_site or 'IE613' in obs_site:
        site = EarthLocation( lat = 53.095 * u.deg, lon = -7.9218 * u.deg, height = 100 * u.m )#Birr
    else:
        site = EarthLocation.of_site( obs_site )
    SiteLatLon = site.to_geodetic()
    global rawdata
    if len( data[ 0 : ] ) < 50:
        print ('Plotting data from file')
        rawdata = np.loadtxt( datafile, skiprows = 0 )
        rawdata = np.fliplr( rawdata )
        rawdata = np.flipud( rawdata )
        subband = datafile[ datafile.find( '_sb' ) + 3 : datafile.find( '_', datafile.find( '_sb' ) + 3 ) ]
    else:
        print ('Plotting data from memory')
        print (data.shape)
        rawdata = data
        subband = datafile[ datafile.find( '_sb' ) + 3 : datafile.find( '_', datafile.find( '_sb' ) + 3 ) ]
        print(subband)
    
    stdate = datafile.find('_sb');
    filedate = datafile[ stdate - 15 : stdate - 11 ] + '-' + datafile[ stdate - 11 : stdate - 9 ] + '-' + datafile[ stdate - 9 : stdate - 7 ];

    if '_xst_' in datafile:
        im_num = int(datafile.split('_xst_')[-1].replace('.dat', '')) - 1
        filetime = datafile[stdate-6:stdate-4] + ':' + datafile[stdate-4:stdate-2] + ':' + datafile[stdate-2:stdate]
        obstime = Time(filedate + ' ' + filetime) + im_num * int_time * u.s
    else:
        filetime = datafile[stdate-6:stdate-4] + ':' + datafile[stdate-4:stdate-2] + ':' + datafile[stdate-2:stdate]
        obstime = Time(filedate + ' ' + filetime)
    # trying to fix obs time issue

    '''
    if datafile == '*xst_*.dat':
        im_num = datafile.split('_')[-1].replace('.dat', '')
        filetime = datafile[ stdate - 6 : stdate - 4 ] + ':' + datafile[ stdate - 4 : stdate - 2 ] + ':' + (datafile[ stdate - 2 : stdate ] + (im_num * int_time)); # need to figure out how to deal w this if it spills over a minute
    else:
        filetime = datafile[ stdate - 6 : stdate - 4 ] + ':' + datafile[ stdate - 4 : stdate - 2 ] + ':' + datafile[ stdate - 2 : stdate ];
    obstime=Time( filedate + ' ' + filetime )
    '''
    print(obstime)
    freq = CalcFreq( int( rcumode ), int( subband ) )
    Object1Name = "Cas A"
    Object2Name = "Cyg A"
    Object3Name = "Sun"
    altazframe = AltAz( obstime = obstime, location=site )
    altazframe = AltAz( obstime = obstime, location=site )

    Object1 = SkyCoord.from_name( "Cas A" ) # same as SkyCoord.from_name('Object'): use the explicit coordinates to allow building doc plots w/o internet
    Object1altazs = Object1.transform_to( altazframe )
    Object2 = SkyCoord.from_name( "Cyg A" ) # same as SkyCoord.from_name('Object'): use the explicit coordinates to allow building doc plots w/o internet
    Object2altazs = Object2.transform_to( altazframe )
    Object3altazs = get_sun( obstime ).transform_to( altazframe )

    gs = gridspec.GridSpec( 1, 2, width_ratios = [ 18, 1 ] )
    gs2 = gridspec.GridSpec( 1, 2, width_ratios = [ 18, 1 ] )
    global fig
    fig = plt.figure()
    fig.patch.set_facecolor(back_color)
    plt.get_current_fig_manager().resize( 1024, 768 )
    plt.suptitle( 'LOFAR mode ' + str( rcumode ) + polarity + ' all sky plot at ' + str( round( freq, 2 ) ) + 'MHz (sb' + subband + ') for ' + obs_site + '\n', fontsize = 18, color=fore_color )#, va = 'top')
    plt.rcParams["text.color"] = fore_color
    plt.rcParams["axes.labelcolor"] = fore_color
    plt.rcParams["xtick.color"] =  fore_color
    plt.rcParams["ytick.color"] = fore_color
    plt.rcParams['axes.edgecolor'] = fore_color
    plt.rcParams['axes.linewidth'] = grid_thick
    global ax
    global ax_image
    ax_image = fig.add_subplot( gs[ 0 ] , label = 'ax_image' )
    ax_image.axis( 'off' )
    if logplot == True:
        rawdatal=np.log( rawdata )
        image=ax_image.imshow( rawdatal,vmin = np.nanmin(rawdatal), vmax = np.nanmax(rawdatal), alpha = 1, cmap='jet', label = 'ax_image' )
    else:
        image=ax_image.imshow( rawdata,vmin = np.nanmin(rawdata), vmax = np.nanmax(rawdata), alpha = 1, cmap='jet', label = 'ax_image' )
    ax_image.axis( 'off' )  # don't show the axes ticks/lines/etc. associated with the image
    print(np.nanmin(rawdata))
    print(np.nanmax(rawdata))
    if color_bar == 1:
        global ax_cb
        ax_cb = plt.subplot(gs[1])
        cb = plt.colorbar(image, ax_cb)
#        cbytick_obj = plt.getp(ax_cb, 'yticklabels' ) #Set y tick label color
#        plt.setp(cbytick_obj, color=fore_color)
        ax_cb.tick_params(which = 'minor', length = 2)#, color = fore_color )
        ax_cb.tick_params(which = 'major', length = 4, width = 1)#, colors = fore_color )
        ax_cb.yaxis.set_minor_locator(AutoMinorLocator(10))
        global data_min
        global data_max
        data_min=np.nanmin( rawdata )
        data_max=np.nanmax( rawdata )
        #data_min=1e9
        #data_max=0.7e9
        global cb_cursor
        cb_cursor = ax_cb.plot( [ 0, 1 ], [ 0, 0 ], 'k-')
        fig.canvas.mpl_connect("motion_notify_event", hover) # if you don't need the cursor on the colorbar, comment this out
    ax = fig.add_subplot( gs2[ 0 ] , label = 'ax', polar = True )

    if Object1altazs.alt.deg > 0:
      y, x = pol2cart( np.sin( ( 90*np.pi/180 ) - Object1altazs.alt.rad ), Object1altazs.az.rad, pixels )
      CasA = ax_image.scatter( x, y, color = ol_col, marker = 'D', s=30, label = 'Cas A' + ' - Az=' + str( round( Object1altazs.az.deg, 1) ) + u'\xb0' + ', El=' + str( round( Object1altazs.alt.deg, 1) ) + u'\xb0', alpha =1 )#, cmap='hsv', alpha=1, linestyle='--', label=ObjectName)
      ax_image.annotate( Object1Name, xy = ( x, y ), xytext = ( x+2, y+2 ), color = ol_col )

    if Object2altazs.alt.deg > 0:
      y, x = pol2cart( np.sin( ( 90*np.pi/180 )-Object2altazs.alt.rad ), Object2altazs.az.rad, pixels )
      CygA = ax_image.scatter( x, y, color = ol_col, marker = 'D', s=30, label = 'Cyg A' + ' - Az=' + str( round( Object2altazs.az.deg, 1 ) ) + u'\xb0' + ', El=' + str( round( Object2altazs.alt.deg, 1) ) + u'\xb0', alpha = 1 )#, cmap='hsv', alpha=1, linestyle='--', label=ObjectName)
      ax_image.annotate( Object2Name, xy=( x, y ), xytext=( x+2, y+2), color = ol_col )
    Sun=''
    if Object3altazs.alt.deg > 0:
      y, x=pol2cart(np.sin( ( 90*np.pi/180 )-Object3altazs.alt.rad), Object3altazs.az.rad, pixels )
      Sun = ax_image.scatter( x, y, color = ol_col, marker = 'o', s=30, label='Sun' + ' - Az=' + str( round( Object3altazs.az.deg, 1 ) ) + u'\xb0' + ', El=' + str(round(Object3altazs.alt.deg,1)) + u'\xb0', alpha=1)#, cmap='hsv', alpha=1, linestyle='--', label=ObjectName)
      ax_image.annotate( Object3Name, xy = ( x, y ), xytext = ( x + 2, y + 2 ) )
    y,x=pol2cart(np.sin( ( ( 90 * np.pi/180 ) - 53.3 * np.pi/180 ) ), 0, pixels ) # plot NCP
    ax_image.scatter( x, y, cmap = 'hsv', alpha = 1, color = ol_col, marker = 'o', s = 30 )#label='NCP', s=30)
    ax_image.annotate( 'NCP', xy = ( x,y ), xytext = ( x + 2, y ), color = ol_col )
    plt.rcParams["text.color"] = fore_color
    legend = ax_image.legend( loc = 8, bbox_to_anchor = ( 0.5, -0.128 ), ncol = 4, framealpha = 0.0, fontsize = 10, title = str( obstime )[ : len( str( obstime ) )-4])#, color = fore_color )
#    for text in legend.get_texts():
#      text.set_color( fore_color )
    ax_image.set_xlim( ( 0, pixels ) )
    ax_image.set_ylim( ( pixels, 0 ) )
    ax.set_theta_zero_location( "N" )
    ax.set_theta_direction( 1 )
    radii = []
    for r in range( 0, 90, 15 ): # r grid at 15 degree intervals
        radii.append( 180 * np.cos( r * np.pi/180 ) ) # plot the radii so as to display as an orthographic grid
        ax.set_rgrids( radii )
    if radial_label_angle != 0: # you would not want to put y ticks on 0 anyhow as it would be messy
        yLabel = [ '', '15' + u'\xb0', '30' + u'\xb0', '45' + u'\xb0', '60' + u'\xb0', '75' + u'\xb0' ]
        ax.set_yticklabels( yLabel, color = ol_col )
        ax.set_rlabel_position( radial_label_angle )
    else:
        yLabel = []
        ax.set_yticklabels( yLabel )
    thetaticks = np.arange( 0, 360, 45 )
    if get_matplotlib_ver() <= 202:
        ax.set_thetagrids( thetaticks, weight = 'bold', frac = 0.95, color = ol_col )
        ax.tick_params( 'x', pad = 3 ) #if matplotlib 2.0.2 or below
    if get_matplotlib_ver() >= 211:
        ax.set_thetagrids( thetaticks, weight = 'bold', color = ol_col )
        ax.tick_params( 'x', pad = -20, rotation = 'auto' ) #if matplotlib version is >= 2.1.1
    #ax.tick_params( 'both', direction = 'out', pad = -15 )
    ax.grid( False, 'both', color = ol_col, linestyle = 'dotted', linewidth = grid_thick )
    ax.patch.set( alpha = 0.0 )
    plt.sca( ax_image )
    # setup the annotation that appears when the mouse is clicked on the plot
    global annot
    annot = ax.annotate( "", xy = ( 0, 0 ), xytext = ( 15, 15 ), textcoords = "offset points", bbox = dict( boxstyle = "round", fc = "w" ), arrowprops = dict( arrowstyle = "->" ) )
    annot.set_visible( False )
    fig.canvas.mpl_connect( 'button_press_event', onclick )
    fig.canvas.mpl_connect( 'axes_leave_event', onaxesleave )
    plt.show()
    plt.pause( 0.1 ) #its an interactive plot, got to wait for it to initialise before moving on....
    if save_image == True:
      plotfilename=datafile[0:len( datafile ) - 8] + polarity + '_xst.png'
      print (plotfilename)
      plt.savefig( plotfilename,facecolor=fig.get_facecolor(), edgecolor='none' )#, bbox_inches='tight')
    if multiple_files == True:
        plt.close()
#Today = str(datetime.utcnow())[0:10] #extract today's date only

if __name__ == '__main__':
    from optparse import OptionParser
    o = OptionParser()
    o.set_usage('%prog datafile [options]')
    o.set_description(__doc__)
    o.add_option('-s', '--site', dest='site', default='Birr',
        help = 'The observing site name')
    o.add_option('-m', '--multiple_files', action='store_true', dest='multiple_files', default=False,
        help = 'We are processing multiple files so close the plot each time')
    o.add_option('-p', '--pixels', default=200, dest='pixels',
        help = 'option -p sets the # of pixels in the output data')
    o.add_option('-o', '--overlay_col', default='black', dest='ol_col',
        help = 'option -o sets the color of the overlay in the plot')
    o.add_option('-b', '--back_color', default='black', dest='back_color',
        help = 'option -b sets the color of the figure background')
    o.add_option('-f', '--fore_color', default='white', dest='fore_color',
        help = 'option -f sets the color of the title, legend & colorbar ticks in the plot')
    o.add_option('-g', '--grid_thick', default=0.5, dest='grid_thick',
        help = 'option -g sets the thickness of the overlay grid in the plot. Valid values are 0.1 to 1')
    o.add_option('-c', '--colorbar', action='store_true', default=False, dest='color_bar',
        help = 'option -c adds a colorbar')
    o.add_option('-y', '--radial_label_angle', dest='radial_label_angle', default='0',
        help = 'The angle Y tic labels are displayed at on the polar plot, if zero, then don\'t display')
    o.add_option('-i', '--image', action='store_true', default=False, dest='save_image',
        help = 'option -i saves a processed image in the data folder')
    o.add_option('-l', '--logplot', action='store_true', default=False, dest='logplot',
        help = 'option -l produces a log plot of the lofar xst data')
    o.add_option('-e', '--int_time', default=False, dest='int_time', help='option -e gives the exposure/integration time (needed for xst files with multiple observations embedded)')
    opts, args = o.parse_args( sys.argv[1:] )

    datafile = process_path( args[0] ) #you CAN run this in standalone mode with a suitably prepared matrix file.
    data = np.array( [], dtype=np.float64 ) #a blank array, if were running this from cmd line we'll be getting data from a file
    obs_site = opts.site
    pixels = float( opts.pixels )
    save_image = opts.save_image
    color_bar = opts.color_bar
    int_time = float(opts.int_time) if opts.int_time else 0 # help got for this bug 
    ol_col = opts.ol_col
    back_color = opts.back_color
    fore_color = opts.fore_color
    grid_thick = opts.grid_thick
    multiple_files = opts.multiple_files
    logplot = opts.logplot
    rcumode = datafile[len( datafile )-6:len( datafile ) - 5]
    polarity = datafile[len( datafile )-5:len( datafile ) - 4]
    radial_label_angle = float( opts.radial_label_angle )

    main(datafile, data, rcumode, polarity, logplot, pixels, ol_col, grid_thick, back_color, fore_color, save_image, multiple_files, radial_label_angle, color_bar, obs_site )

