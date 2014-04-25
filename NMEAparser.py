# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# NMEA 0183 Data Parser with Python Pandas

# <markdowncell>

# Assume we have a NMEA Logfile with [GST](http://www.nmea.de/nmea0183datensaetze.html#gst) and [GGA](http://www.nmea.de/nmea0183datensaetze.html#gga) sentences in it. Here is an example on how to parse and plot it with Python Pandas.

# <codecell>

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from IPython.display import Image as ImageDisp
from pandas import DataFrame
import string
import os
import matplotlib.pyplot as plt

# <codecell>

%pylab inline --no-import-all

# <headingcell level=4>

# Function to parse the NMEA Date

# <codecell>

def nmeatime(date):
    return datetime.strptime(date, "%H%M%S.%f")

# <headingcell level=2>

# Read Logfile

# <codecell>

fto = './DataLogs/Messfahrt_2_start64.log' #  File to Open
data = pd.read_table(fto, sep=',', header=None, index_col=1, parse_dates=True, date_parser=nmeatime, comment='*')

# <headingcell level=1>

# GNSS Message Types

# <headingcell level=2>

# GST - GNSS Pseudorange Error Statistics

# <codecell>

GSTData = data[1::2].drop(0,1)

# <markdowncell>

# 
# ```
#        1         2   3   4   5   6   7   8 
#        |         |   |   |   |   |   |   | 
# $--GST,hhmmss.ss,x.x,x.x,x.x,x.x,x.x,x.x,x.x*hh<CR><LF>
# ```
# 1. UTC time of the GGA or GNS fix associated with this sentence.
# 2. RMS value of the standard deviation of the range inputs to the navigation process. Range inputs include preudoranges & DGNSS corrections.
# 3. Standard deviation of semi-major axis of error ellipse (meters) 
# 4. Standard deviation of semi-minor axis of error ellipse (meters) 
# 5. Orientation of semi-major axis of error ellipse (degrees from true north) 
# 6. Standard deviation of latitude error (meters) 
# 7. Standard deviation of longitude error (meters) 
# 8. Standard deviation of altitude error (meters) 
# 
# This message is used to support Receiver Autonomous Integrity Monitoring (RAIM). Pseudorange measurement error statistics can be translated in the position domain in order to give statistical measures of the quality of the position solution. 
# If only GPS, GLONASS, etc. is used for the reported position solution, the talker ID is GP, GL, etc., and the error data pertains to the individual system. If satellites from multiple systems are used to obtain the reported position solution, the talker ID is GN and the errors pertain to the combined solution.

# <codecell>

GSTData.rename(columns={1: 'UTC Time', 2: 'RMS', 3: 'SigmaMajorAxis', 4: 'SigmaMinorAxis', 5: 'OrientMajorAxis', 6: 'SigmaLat', 7: 'SigmaLon', 8: 'SigmaAlt'}, inplace=True)
GSTData=GSTData.drop([9, 10, 11, 12, 13, 14],1)

# <codecell>

GSTData.head(10)

# <headingcell level=2>

# GGA - Global Positioning System Fix Data, Time, Position and fix related data fora GPS receiver.

# <markdowncell>

# ```
#                                                       11 
#         1         2       3 4        5 6 7  8   9  10 |  12 13  14   15 
#         |         |       | |        | | |  |   |   | |   | |   |    | 
#  $--GGA,hhmmss.ss,llll.ll,a,yyyyy.yy,a,x,xx,x.x,x.x,M,x.x,M,x.x,xxxx*hh<CR><LF>
# ```
# Field Number:
# 
# 1. Universal Time Coordinated (UTC)
# 2. Latitude
# 3. N or S (North or South) 
# 4. Longitude
# 5. E or W (East or West) 
# 6. GPS Quality Indicator,
#  `0 - fix not available`
#  `1 - GPS fix`
#  `2 - Differential GPS fix`
#  
# 7. Number of satellites in view, 00 - 12 
# 8. Horizontal Dilution of precision 
# 9. Antenna Altitude above/below mean-sea-level (geoid)  
# 10. Units of antenna altitude, meters 
# 11. Geoidal separation, the difference between the WGS-84 earth ellipsoid and mean-sea-level (geoid), "-" means mean-sea-level below ellipsoid 
# 12. Units of geoidal separation, meters 
# 13. Age of differential GPS data, time in seconds since last SC104 type 1 or 9 update, null field when DGPS is not used 
# 14. Differential reference station ID, 0000-1023 
# 15. Checksum

# <codecell>

GGAData = data[::2].drop(0,1)

# <codecell>

GGAData.rename(columns={1: 'UTC Time', 2: 'Lat', 3: 'NorS', 4: 'Lon', 5: 'EorW', 6: 'Fix', 7: 'NumSats', 8: 'HDOP', 9: 'Alt', 10: 'Unit', 11: 'GeoidSeparation', 12: 'UnitGeoSep', 13: 'DGPSage', 14: 'DGPSStation'}, inplace=True)

# <headingcell level=4>

# Convert from DDMM.MMMM to DD.dddd

# <codecell>

GGAData['LatDD'] = (GGAData.Lat/100).fillna(0).astype(int)
GGAData['LatDD'] = GGAData.LatDD + (GGAData.Lat - 100.0*GGAData.LatDD)/60.0

# <codecell>

GGAData['LonDD'] = (GGAData.Lon/100).fillna(0).astype(int)
GGAData['LonDD'] = GGAData.LonDD + (GGAData.Lon - 100.0*GGAData.LonDD)/60.0

# <headingcell level=2>

# GNSS Data

# <codecell>

GNSSData = pd.merge(GSTData, GGAData, left_index=True, right_index=True, how='outer')

# <codecell>

GNSSData.index.names = ['UTC Time']

# <headingcell level=2>

# Time Offset

# <codecell>

GNSSData.index = GNSSData.index.map(lambda t: t.replace(year=2014, month=4, day=23)) - pd.offsets.Hour(-2)
GNSSData.index

# <codecell>

pd.options.display.max_columns = 50
GNSSData.head(10)

# <headingcell level=1>

# Plots

# <codecell>

nvalues = int(GNSSData.count()[0])
GNSSData.count()

# <codecell>

fw = int(nvalues/6000.0)
if fw < 16:
    fw=16
elif fw > 3000:
    fw=3000

# <headingcell level=2>

# Abtastrate

# <codecell>

GNSSData['tvalue'] = GNSSData.index
GNSSData['delta'] = (GNSSData['tvalue'] - GNSSData['tvalue'].shift()).fillna(0)
dt_s = GNSSData['delta'].values.astype('int')/1e9
GNSSData['fa']=np.divide(1.0,dt_s)

print('Abtastrate der Messung (im Mittel): %.1fHz' % np.divide(1.0,dt_s.mean()))

plt.figure(figsize=(fw, 4))
GNSSData['fa'].plot()
plt.ylabel('$Hz$')
plt.title('Abtastrate')
#plt.axhline(50, color='k', alpha=0.2)
#plt.savefig(outdir+fto[16:-8]+'fa.png', dpi=150, bbox_inches='tight')

# <headingcell level=2>

# Position

# <markdowncell>

# Thanks to [heatmap](http://sethoscope.net/heatmap/) and [OSMViz](http://cbick.github.io/osmviz/html/index.html), this is possible

# <codecell>

gpslogfile = fto[:-4]+'-LatLon.log'
gpsmapfile = fto[:-4]+'-GPSHeatmap.png'

gpsmapwidth= 800    # px
gpsmapmargin=100     # px
gpsmapbase = 'http://b.tile.stamen.com/toner-lite'

# write lat/lon text file to read in to heatmap
GNSSData[['LatDD','LonDD']][::10].to_csv(gpslogfile, sep=' ', index=False, header=False)

# create Heatmap of Lat/Lon
# -M =Value Color in HSV Hex with Direction DHHSSVVAA (=Direction, Hue, Suration, Value, Alpha)
%run heatmap.py {'-p %s -o %s --width %i -M 018FFFFFF --margin %i --osm --osm_base %s' % (gpslogfile, gpsmapfile, gpsmapwidth, gpsmapmargin, gpsmapbase)}

# <codecell>

# Display GPS Heatmap from Disk
gpsheatmap = ImageDisp(filename=gpsmapfile)
gpsheatmap

# <markdowncell>

# Map tiles by [Stamen Design](http://stamen.com/), under [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/). Data by [OpenStreetMap](http://www.openstreetmap.org/), under [CC BY SA](http://creativecommons.org/licenses/by-sa/3.0/).

# <headingcell level=2>

# GNSS Signal Quality Stats

# <codecell>

plt.figure(figsize=(fw, 4))
la=GNSSData['RMS'].plot(alpha=0.6)
la=GNSSData['DGPSage'].plot(alpha=0.6)
plt.legend(loc=2)
ra=GNSSData.NumSats.plot(secondary_y=True, alpha=0.4)

la.set_ylabel('RMS ($m$) und DGPS Age')
#la.set_ylim([-6,6])
ra.right_ax.set_ylabel('Satellites Used')
#ra.set_ylim([0, 8])
plt.legend(loc=1)

plt.savefig(fto[:-4]+'-RMS.png', dpi=150, bbox_inches='tight')

# <headingcell level=2>

# RMS

# <codecell>

whratio = np.cos(np.mean(GNSSData.LatDD*np.pi/180.0))
fh = 14.0
fig = plt.figure(figsize=(fh, fh*whratio))

# Measurements
every = 50 #
plt.scatter(GNSSData.LonDD[::every], GNSSData.LatDD[::every], s=100, label='GNSS measurement (every %sst)' % every,\
            c=GNSSData.RMS[::every], cmap='autumn_r')
cbar=plt.colorbar()
cbar.ax.set_ylabel(u'RMS', rotation=270)
cbar.ax.set_xlabel(u'$m$')

plt.xlabel('Longitude [$^\circ$]')
plt.ylabel('Latitude [$^\circ$]')
plt.legend(loc='best')
plt.axis('equal')
#plt.tight_layout()

# xticks
locs,labels = plt.xticks()
plt.xticks(locs, map(lambda x: "%.3f" % x, locs));

# ytikcs
locs,labels = plt.yticks()
plt.xticks(rotation=35)
plt.yticks(locs, map(lambda x: "%.3f" % x, locs));

plt.savefig(fto[:-4]+'-RMS-LatLon.png', dpi=150, bbox_inches='tight')

# <headingcell level=2>

# Altitude

# <codecell>

plt.figure(figsize=(fw, 4))
la=GNSSData['Alt'].plot(alpha=0.6)
plt.xlabel('Time')
plt.legend(loc=2)
ra=GNSSData.SigmaAlt.plot(secondary_y=True, alpha=0.4)

la.set_ylabel('Altitude ($m$)')
#la.set_ylim([-6,6])
ra.right_ax.set_ylabel('$\sigma_{Altitude}$')
#ra.set_ylim([0, 8])
plt.legend(loc=1)

# <codecell>

print('Done')

