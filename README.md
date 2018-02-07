Sample API script
=================

Sample Python script to automate GNSS data processing through our PaaS

This script is targeted to photgrammetry applications but can be 
adapted to your needs.

In this case, the script takes care of uploading the GNSS logs from 
Rokubun GNSS receiver (Argonaut) alongside with the metadata from the 
drone's camera to Rokubun's PaaS. The script returns 
a ZIP file with the new metadata file, which has more precise geo-tags 
for all the images. The ZIP also contains additional information on 
the GNSS processing that took place

As mentioned, this repository contains samples from Rokubun GNSS receiver
but any other receiver can be used instead. Just provide the corresponding
RINEX file and the PaaS will take care for the rest.
