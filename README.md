Sample API script
=================

Sample Python script to automate GNSS data processing through our PaaS's API.
This is equivalent to using the GUI from [Rokubun Paas](https://paas.rokubun.cat), or running it via
command line CURLs.

Description
-----------

The script takes care of uploading the GNSS logs from
Rokubun GNSS receiver (Argonaut) alongside with (optional) the metadata* from the
drone's camera to Rokubun's PaaS. The script returns
a ZIP file with the new metadata file, which has more precise geo-tags
for all the images. The ZIP also contains additional information on
the GNSS processing that took place

As mentioned, this repository contains samples from Rokubun GNSS receiver
in our proprietary format, but any other receiver can be used instead.
Simply provide the corresponding RINEX v2 file and the PaaS will take care for the rest.

Another additional input is the GNSS file (Rokubun or Rinex formats accepted) corresponding
to the base station. If this is not provided, the nearest station in our database will
be used instead.

The program needs your user's token. You can get it from your personal area in paas.rokubun.cat --> click on
user's email --> Account —> Software —> Secret Token (if you haven't set up an account yet, now it's time
to do so!).

Finally, the destination folder workspace (working directory) must be provided.


\* _Metadata format is based on Pix4D's (https://support.pix4d.com/hc/en-us/articles/202558539-Input-Files), which is a CSV file with the following fields:_
    
1. `imagename`
2. `latitude` [decimal degrees]
3. `longitude` [decimal degrees]
4. `altitude` [meter]
5. `omega` [degrees]
6. `phi` [degrees]
7. `kappa` [degrees]
8. `Accuracy Easting` [meter]
9. `Accuracy Northing` [meters]
10. `Accuracy Vert` [meter]
11. `GPS Week`
12. `GPS Second of the week`



Execution
---------

The program can be run as follows with the example data in this repo.
```
apiScript.py -c config.yaml
```

Check the tags in the configuration file, and edit it to process your data

```
# This is the template for Rokubun's PaaS API configuration file
# to be provided to the program apiScript.py. Paths must be either absolute,
# or relative with respect to the script's execution directory

# Argonaut LOG file (.rok extension) with the GNSS data to process
argonaut-log: 20171016_1.rok   

# (Optional) GNSS file for the reference station. If not provided, a station
# from the neighbouring networks will be used. The expected file format is Rinex v2.11
base-station:   

# CSV file containing the metadata for every image acquired by the sensor flown alongside
# with Argonaut
images-metadata: original_metadata.csv

# User's secret token. Can be found in the Account section of User's tab in paas.rokubun.cat
# It consists of 30 alphanumeric characters in uppercase following the structure:
# XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX
secret-token: XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX

# Workspace where result will be saved. If it doesn't exist, will be created
workspace: /path/to/the/workspace
```


Requirements
------------

The following components are required to run the script:

* Python 2 or 3
* [`requests`](http://docs.python-requests.org/)
* [`wget`](https://pypi.python.org/pypi/wget)
* [`PyYAML`](https://pypi.python.org/pypi/PyYAML)
