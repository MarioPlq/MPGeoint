import os
import json
import re
import cv2
import inspect
import numpy as np
import threading

from datetime import datetime
from satImgDowloader import DL_img

def getSatImg(lat, lon, square=2000, zoom=18, plot_center=False):    
    
    src_file_path = inspect.getfile(lambda: None)
    file_dir = os.path.dirname(src_file_path)
    prefs_path = os.path.join(file_dir, 'preferences.json')
    
    R = 6378137
    D = square/2
    
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    if (prefs['tl'] == '') or (prefs['br'] == '') or (prefs['zoom'] == ''):
        
        dLat = D/R
        dLon = D/(R*np.cos(np.pi*lat/180))

        latTL = lat + dLat * 180/np.pi
        lonTL = lon - dLon * 180/np.pi 

        latBR = lat - dLat * 180/np.pi
        lonBR = lon + dLon * 180/np.pi 

        inputs = [f'{latTL}, {lonTL}', f'{latBR}, {lonBR}', f'{zoom}']
        
        prefs['tl'], prefs['br'], prefs['zoom'] = inputs

    lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['tl'])
    lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['br'])

    zoom = int(prefs['zoom'])
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    if prefs['tile_format'].lower() == 'png':
        channels = 4
    else:
        channels = 3

    img = DL_img(lat1, lon1, lat2, lon2, zoom, prefs['url'],
        prefs['headers'], prefs['tile_size'], channels)
    
    if plot_center:
        middle = int(len(img)/2)
        r = int(len(img)/20)

        for ep in range(int(0.005*len(img))):
            for angle in np.arange(0, 2 * np.pi, 1/2/r):
                x = int((r+ep) * np.cos(angle))
                y = int((r+ep) * np.sin(angle))
                img[middle+x,middle+y] = [255]
    
    name = f'{lat}_{lon}.png'   
    
    cv2.imwrite(os.path.join(prefs['dir'], name), img)
    print(f'Saved as {name}')
 