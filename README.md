# Origanise photos and videos
## Description
Python tool to organise photos and videos
## Features
* Identifies duplicate photos/videos and copies only the original file
* If the file is already in destination then it is not copied
* Copies all meta data information along with the files
* Files in the source path is not deleted or modified
* Neatly organises files based on year/month
* Renames files in destination in the type_YYYYMMDD_HHMMSS format
* Creates a photos.csv file with the information on the files copied
* Supports almost all video and image formats
## Parameters
**Source**: directory where photos and vidoes are stored  
**Destination**: directory where they are to be copied
## Requirements
future==0.18.2
numpy==1.20.1
pandas==1.2.2
Pillow==8.1.0
python-dateutil==2.8.1
pytz==2021.1
six==1.15.0
