import os
import time
import shutil
import hashlib
import argparse
import concurrent.futures
import pandas as pd

from PIL import Image
from PIL.ExifTags import TAGS
from collections import defaultdict
from datetime import datetime

VIDEO = ('.m1v', '.mpeg', '.mov', '.qt', '.mpa', '.mpg', '.mpe', '.avi', '.movie', '.mp4', '.3gp')
IMAGE = ('.ras', '.xwd', '.bmp', '.jpe', '.jpg', '.jpeg', '.xpm', '.ief', '.pbm', '.tif', '.gif', '.ppm', '.xbm', '.tiff', '.rgb', '.pgm', '.png', '.pnm')

def GetFileHash(myfile):
   
    CHUNK_SIZE = 1024 * 1024

    with open(myfile, "rb") as f:
        file_hash = hashlib.md5()
        #file_hash = hashlib.sha1()
        #file_hash = hashlib.sha256()
        #file_hash = hashlib.sha512()
        chunk = f.read(CHUNK_SIZE)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(CHUNK_SIZE)
    
    return file_hash.hexdigest()

def GetNewName(fullPath, dateStr, isVideo):
    fstr = dateStr.replace(':', '')
    fstr = fstr.replace(' ', '_')
    fname = os.path.basename(fullPath)
    split = os.path.splitext(fname)
    if(isVideo == False):
        newName = 'img_' + fstr + split[1].lower()
    else:
        newName = 'mov_' + fstr + split[1].lower()
   
    try:
        d = datetime.strptime(dateStr, "%Y:%m:%d %H:%M:%S")
        y = str(d.year)
        m = d.strftime("%b")
    except Exception as e:
        print(e)

    return os.path.join(y, os.path.join(m,newName))

class MetaInfo:

    def __init__(self, orig):
        self.origf = os.path.normpath(orig)
        if orig.lower().endswith(VIDEO):
            self.is_video = True
        else:
            self.is_video = False

    def GetImageTags(self):

        try:
            # read the image data using PIL
            image = Image.open(self.origf)

            # extract EXIF data
            exifdata = image.getexif()

            """
            The problem with exifdata variable now is that the field names are just IDs, not a 
            human readable field name, thats why we gonna need the TAGS dictionary from PIL.ExifTags 
            module which maps each tag ID into a human readable text 
            """

            print('\n'+self.origf+'\n')

            # iterating over all EXIF data fields
            for tag_id in exifdata:
                # get the tag name, instead of human unreadable tag id
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                # decode bytes 
                if isinstance(data, bytes):
                    data = data.decode(encoding='UTF-8',errors='strict')

                print(f"{tag_id}:{tag:25}: {data}")
        except:
            pass


    def GetFileDate(self):
        t = os.path.getmtime(self.origf)
        return time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(t))

    def GetImageDate(self):
       
        try:
            # read the image data using PIL
            image = Image.open(self.origf)
            
            # extract EXIF data
            exifdata = image.getexif()
            cdate = exifdata.get(36867)
            if(str(cdate) == 'None'):
                raise Exception("Meta info not found")
        except:
            # faill back to file date
            cdate = self.GetFileDate()

        return cdate
   
    def GetVideoDate(self):
#        try:
#            print(self.origf)
#            vid = ffmpeg.probe(self.origf)
#            print(vid['streams'])
#        except Exception as e:
#            print(e)

        cdate = self.GetFileDate()

        return cdate

    def GetMetaInfo(self):
        if self.is_video == True:
            date = self.GetVideoDate()
        else:
            date = self.GetImageDate()

        hash = GetFileHash(self.origf)
        name = GetNewName(self.origf, date, self.is_video)

        info = [ self.origf, date, hash, name ]
       
        return info

def GetMetaDataFrame(path, statuscb):
    data = defaultdict(list)
    total = 0
    for dirpath, dirs, files in os.walk(path):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for filename in files: 
                #print(filename)
                if filename.lower().endswith(IMAGE) or filename.lower().endswith(VIDEO): 
                    total += 1
                    mi = MetaInfo(os.path.join(dirpath,filename))
                    f = executor.submit(mi.GetMetaInfo)
                    futures.append(f)

            for future in concurrent.futures.as_completed(futures):
                try:
                    info = future.result()
                    data['origfile'].append(info[0])
                    data['date'].append(info[1])
                    data['hash'].append(info[2])
                    data['newpath'].append(info[3])
                    statuscb(f"Processed {info[0]}")
                except:
                    pass
    
    return pd.DataFrame(data)

def copy_files(df, dest, statuscb):
    futures = {}
    for idx, row in df.iterrows():
        dirname = os.path.dirname(row["newpath"])
        filename = os.path.basename(row["newpath"])
        absdir = os.path.join(dest, dirname)
        os.makedirs(absdir, exist_ok=True)
        fullpath = os.path.join(absdir, filename)
        #shutil.copy2(row["origfile"], fullpath)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f = { executor.submit(shutil.copy2, row["origfile"], fullpath) : fullpath }
            futures.update(f)

    for f in concurrent.futures.as_completed(futures):
        try:
            print(f"Copied:{futures[f]}")
            statuscb(f"Copied {futures[f]}")
        except Exception as e:
            print(e)

def do_organise(src, dest, statuscb):
    # get meta information from the source path
    dfSrc = GetMetaDataFrame(src, statuscb)
    
    # sort data frame by date
    dfSrc.sort_values(by=["date"], inplace=True)

    # get meta information from the destination path
    dfDest = GetMetaDataFrame(dest, statuscb)
    
    # get duplicated list of hash values
    dfSrc.drop_duplicates(subset=["hash"], keep="first", inplace=True)
    #filt = dfSrc.duplicated(subset="hash", keep="first")
    # remove duplicates from data
    #dfSrc = dfSrc[~filt]
    
    filt = dfSrc.duplicated(subset="newpath", keep=False)
    #print(dfSrc.loc[ filt, "newpath" ].apply(lambda x:x))
    seDups = dfSrc.loc[filt, "newpath"].sort_values()
    prevVal = ""
    for idx, val in seDups.iteritems():
        if prevVal == dfSrc.at[idx, "newpath"]:
            count += 1
            split =  os.path.splitext(dfSrc.at[idx, "newpath"])
            newName = "{0}_{1}{2}".format(split[0], str(count), split[1])
            dfSrc.at[idx, "newpath"] = newName
        else:
            count = 0

        prevVal = val

    dfMerge = pd.concat([dfSrc, dfDest], keys=["src", "dest"])
    dfMerge.drop_duplicates(subset=["hash"], keep=False, inplace=True)
    copy_files(dfMerge.loc["src"], dest, statuscb)
    dfMerge.loc["src"].reset_index(drop=True).to_csv(os.path.join(dest, "photos.csv"), mode="a")

