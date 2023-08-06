# Kalifast main package class
import os
from re import S, X
import shutil

import webbrowser

import validators

import tempfile

import datetime
from tkinter import Y
from tkinter import Tk


import urllib.request
from urllib.parse import urlparse
from urllib.parse import parse_qs

import pyautogui

import numpy as np
import cv2
import pytesseract

import os
import io
import PIL.Image as Image
from PIL import ImageGrab, ImageOps

import pyperclip

import threading
from threading import Event, Thread
import time



class KFT :
    # OutPut #
    LOG_FILE_NAME          = "logs.txt"
    OUTPUT_STATE_FILE_NAME = "KFT_OUTPUT_STATE"
    OUTPUT_PARAMS_DIR_NAME = "output" #output
    IMAGE_DIR_NAME = "screenshots"

    DEBUG = "DEBUG";
    VERBOSE = "VERBOSE";
    INIT = "INIT";
    ERROR = "ERROR";
    incrementLine = 0;

    VERBOSE_MODE = False;


    #Image Detector#

    #REFERENCES#
    CENTER = 10
    LEFT = 11
    RIGHT = 12

    TOP = 13
    TOP_LEFT = 14
    TOP_RIGHT = 15

    BOT = 16
    BOT_LEFT = 17
    BOT_RIGHT = 18


    ENTIRE_SCREEN = 100

    DefaultCorrelation = 0.998
    DefaultTimeout = 5000
    DefaultReference = CENTER
    DefaultParentZone = False

    ERROR_IMG_URL_NOT_FOUND = "image_url_not_found"
    ERROR_IMG_NOT_DEFINED = "image_not_defined"
    ERROR_IMAGE_NOT_VISIBLE ="image_not_visible"
    ERROR_SPECIFY_POSITION ="no_position_specified"
    ERROR_PARAMETERS = "error_parameters"
    ERROR_TIMEOUT ="timeout (image not detected ?)"

    thread_result = False
    
    def __init__(self, base_path=False):

        # OutPut #
        if base_path == False :
            base_path = "./"

        if base_path[-1] != '/' :
            base_path += '/'

        if os.path.isdir(base_path) == False :
            os.mkdir(base_path)

        self.base_path = base_path
        self.clearAll()
        self.initLog()

    #Fonction permettant de mettre à jour les attributs par défaut utilisé par la classe KFT.
    def setDefaultAttributes(self, correlation=DefaultCorrelation, timeout=DefaultTimeout, reference=DefaultReference, parentZone=DefaultParentZone) :
        if correlation != False :
            if isinstance(correlation, int) or isinstance(correlation, float):
                if correlation >= 0  and correlation <= 1 :
                    self.DefaultCorrelation = correlation
                else :
                   self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="correlation must be between 0 and 1 !")
                   raise Exception("correlation must be between 0 and 1 !") 
            else :
                self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="correlation must be an integer !")
                raise Exception("correlation must be an integer !")

            
        if timeout != False :
            if isinstance(timeout, int) :
                if timeout >= 0 :
                    self.DefaultTimeout = timeout
                else :
                    self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="timeout must be >= 0 !")
                    raise Exception("timeout must be >= 0 !")
            else :
                self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="timeout must be an integer !")
                raise Exception("timeout must be an integer !")


        if reference != False :
            if isinstance(reference, int) :
                if reference >= 10 and reference <= 18 :
                    self.DefaultReference = reference
                else :
                    self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="reference must be one of KFT constants ! (between 10 and 18)")
                    raise Exception("reference must be one of KFT constants ! (between 10 and 18)")
            else :
                self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="reference must be an integer ! (between 10 and 18)")
                raise Exception("reference must be an integer ! (between 10 and 18)")

        if parentZone != False :
            if self._checkTypeZone(parentZone) :
                self.DefaultParentZone = parentZone
            else :
                self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment="parentZone is not a zone ! (must be an array of 2 arrays of 2 integers representing top-left corner point and bot-right corner point)")
                raise Exception("parentZone is not a zone ! (must be an array of 2 arrays of 2 integers representing top-left corner point and bot-right corner point)")

    

        if self.VERBOSE_MODE == True :
            self.writeLog(text="setDefaultAttributes(correlation="+str(correlation)+", timeout="+str(timeout)+", reference="+str(reference)+", parentZone="+str(parentZone)+")", type=self.VERBOSE)

    def _checkTypeCorrelation(self, correlation) :
        if isinstance(correlation, int) or isinstance(correlation, float):
            if correlation >= 0  and correlation <= 1 :
                return True
        return False
                
    def _checkTypeReference(self, reference) :
        if isinstance(reference, int) :
            if reference >= 10 and reference <= 18 :
                return True
        return False

    def _checkTypeTimeout(self, timeout) :
        if isinstance(timeout, int) :
            if timeout >= 0 :
                return True
        return False

    def _checkTypeZone(self, zone) :
        if zone == False :
            return True
        if isinstance(zone, list) :
            if len(zone) == 3 :
                if isinstance(zone[0], list) and isinstance(zone[1], list) and (isinstance(zone[2], list) or zone[2] == False) :
                    if len(zone[0]) == 2 and len(zone[1]) == 2 :
                        if (isinstance(zone[0][0], int) or isinstance(zone[0][0], float)) and (isinstance(zone[0][1], int) or isinstance(zone[0][1], float)) and (isinstance(zone[1][0], int) or isinstance(zone[1][0], float)) and (isinstance(zone[1][1], int) or isinstance(zone[1][1], float)):
                            if(zone[0][0] < zone[1][0] and zone[0][1] < zone[1][1]) :
                                return True
        return False
    
    def _checkTypeZones(self, zones) :
        if isinstance(zones, list) :
            for zone in zones:
                if self._checkTypeZone(zone) == False :
                    return False
        else :
            return False

        return True

    def _checkTypePosition(self, position) :

        if isinstance(position, list) :
            if len(position) == 2 :
                if (isinstance(position[0], int) or isinstance(position[0], float)) and (isinstance(position[1], int) or isinstance(position[1], float)) == True :
                    return True
        return False

    def _checkTypePositions(self, positions) :
        if isinstance(positions, list) :
            for position in positions:
                if self._checkTypePosition(position) == False :
                    return False
        else :
            return False

        return True

    def _checkImgType(self, img) :
        if isinstance(img, str) :
            return True
        return False

    def _checkKeyExist(self, key) :
        possibleKeys = ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace', 'browserback', 'browserfavorites', 'browserforward', 'browserhome', 'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear', 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete', 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail', 'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack', 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn', 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn', 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator', 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab', 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen', 'command', 'option', 'optionleft', 'optionright']
        for possibleKey in possibleKeys:
            if key == possibleKey :
                return True
        return False

    def _checkMouseButtonExist(self, mouseButton) :
        possibleKeys = ['left','right','middle']
        for possibleKey in possibleKeys:
            if mouseButton == possibleKey :
                return True
        return False

    #Fonction permettant d'ouvrir le navigateur par défaut avec l'url indiqué en argument.
    def openBrowser(self, url="") :
        try :
            webbrowser.get('windows-default').open_new(url) 
        except Exception as e:
            self.writeLog(text="openBrowser(url=\""+str(url)+"\")", type=self.ERROR, comment=str(e))
            raise Exception("Error opening browser ("+str(e)+")") 

        if self.VERBOSE_MODE == True :
            self.writeLog(text="openBrowser(url=\""+str(url)+"\")", type=self.VERBOSE)

    #Fonction permettant de récupérer un tableau contenant toutes les zones correspondant à l'image entrée en argument.
    def getAllZone(self, img=False, timeout=DefaultTimeout, correlation=DefaultCorrelation, parentZone=DefaultParentZone, onError=False) :
        if parentZone == False :
            parentZone = self.DefaultParentZone

        if self._checkTypeCorrelation(correlation) == False or self._checkTypeZone(parentZone) == False or self._checkTypeTimeout(timeout) == False:
            if onError != False :
                return onError
            self.writeLog(text="getAllZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)

        if self._checkImgType(img) == False:
            if onError != False :
                return onError
            self.writeLog(text="getAllZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.ERROR, comment=self.ERROR_IMG_NOT_DEFINED + "")
            raise Exception(self.ERROR_IMG_NOT_DEFINED)
        
        locationVisible = self._isVisibleBis(img, correlation, parentZone)
        if locationVisible == False:
            waitVisible = self.waitForVisible(img, timeout, correlation, parentZone)
            locationVisible = self._isVisibleBis(img, correlation, parentZone)
        else :
            waitVisible = True

        
        if locationVisible == False :
            if onError != False :
                return onError
            self.writeLog(text="getAllZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.ERROR, comment=self.ERROR_IMAGE_NOT_VISIBLE + "_1")
            raise Exception(self.ERROR_IMAGE_NOT_VISIBLE+"_1")

        if waitVisible == True or locationVisible != False:
            loc = locationVisible
            hh = locationVisible[3]
            ww = locationVisible[2]
            indexes_alpha = locationVisible[4]
            

            if parentZone == False :
                parentZoneTmp = []
                parentZoneTmp.append([])
                parentZoneTmp[0].append(0)
                parentZoneTmp[0].append(0)
            else :
                parentZoneTmp = []
                parentZoneTmp.append([])
                parentZoneTmp[0].append(parentZone[0][0])
                parentZoneTmp[0].append(parentZone[0][1])


            zones = []
            

            if len(loc[0]) > 0 and len(loc[1]) > 0 :
                # print(loc)
                                    
                if indexes_alpha == False :
                    if(len(loc[0]) > 1) :
                        zones = [
                                    [
                                        [
                                            int(loc[1][i]+parentZoneTmp[0][0]),
                                            int(loc[0][i]+parentZoneTmp[0][1])
                                        ], 
                                        [
                                            int(loc[1][i]+ww+parentZoneTmp[0][0]), 
                                            int(loc[0][i]+hh+parentZoneTmp[0][1])
                                        ],
                                        False
                                    ]
                                    for i in range(len(loc[0]))
                                ]
                    else :
                        zones = [
                                    [
                                        [
                                            int(loc[1][0]+parentZoneTmp[0][0]),
                                            int(loc[0][0]+parentZoneTmp[0][1])
                                        ],
                                        [
                                            int(loc[1][0]+ww+parentZoneTmp[0][0]),
                                            int(loc[0][0]+hh+parentZoneTmp[0][1])
                                        ],
                                        False
                                    ]
                                ]
                else :
                    if(len(loc[0]) > 1) :
                        zones = [
                                    [
                                        [
                                            int(loc[1][i]+parentZoneTmp[0][0]),
                                            int(loc[0][i]+parentZoneTmp[0][1])
                                        ], 
                                        [
                                            int(loc[1][i]+ww+parentZoneTmp[0][0]), 
                                            int(loc[0][i]+hh+parentZoneTmp[0][1])
                                        ],
                                        [
                                            [
                                                int(indexes_alpha[0][1]+loc[1][i]+parentZoneTmp[0][0]),
                                                int(indexes_alpha[0][0]+loc[0][i]+parentZoneTmp[0][1])
                                            ],
                                            [
                                                int(indexes_alpha[1][1]+loc[1][i]+parentZoneTmp[0][0]),
                                                int(indexes_alpha[1][0]+loc[0][i]+parentZoneTmp[0][1])
                                            ]
                                        ]
                                    ]
                                    for i in range(len(loc[0]))
                                ]
                    else :
                        zones = [
                                    [
                                        [
                                            int(loc[1][0]+parentZoneTmp[0][0]),
                                            int(loc[0][0]+parentZoneTmp[0][1])
                                        ],
                                        [
                                            int(loc[1][0]+ww+parentZoneTmp[0][0]),
                                            int(loc[0][0]+hh+parentZoneTmp[0][1])
                                        ],
                                        [
                                            [
                                                int(indexes_alpha[0][1]+loc[1][0]+parentZoneTmp[0][0]),
                                                int(indexes_alpha[0][0]+loc[0][0]+parentZoneTmp[0][1])
                                            ],
                                            [
                                                int(indexes_alpha[1][1]+loc[1][0]+parentZoneTmp[0][0]),
                                                int(indexes_alpha[1][0]+loc[0][0]+parentZoneTmp[0][1])
                                            ]
                                        ]
                                    ]
                                ]
                              
            else :
                if onError != False :
                    return onError   
                self.writeLog(text="getAllZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.ERROR, comment=self.ERROR_IMAGE_NOT_VISIBLE)
                raise Exception(self.ERROR_IMAGE_NOT_VISIBLE)


            if self.VERBOSE_MODE == True :
                self.writeLog(text="getAllZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.VERBOSE, comment= "zones : "+ str(len(zones)) )
            return zones
        else :
            if onError != False :
                    return onError   
            self.writeLog(text="getAllZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.ERROR, comment=self.ERROR_TIMEOUT)
            raise Exception(self.ERROR_TIMEOUT)

    #Fonction permettant de récupérer la première zone trouvée correspondant à l'image entrée en argument.
    def getFirstZone(self, img=False, timeout=DefaultTimeout, correlation=DefaultCorrelation, parentZone=DefaultParentZone, onError=False) :
    
        try :
            zones = self.getAllZone(img,timeout,correlation,parentZone,onError)
            return zones[0]

        except Exception as e:
            if onError != False :
                return onError
            self.writeLog(text="getFirstZone("+str(img)+", "+str(timeout)+", "+str(correlation)+", "+str(parentZone)+", "+str(onError)+")", type=self.ERROR, comment=str(e))
            raise Exception(str(e))

    #Fonction mettant en pause le programme le temps inscrit dans l'argument duration en millisecondes
    def pause(self, duration=DefaultTimeout) :
        time.sleep(duration/1000)
        
        if self.VERBOSE_MODE == True :
             self.writeLog(text="pause("+str(duration)+")", type=self.VERBOSE)

    #Fonction permettant de vérifier sur l'image est présente ou non  à l'écran (Renvoie False ou True)
    def isVisible(self, img=False, correlation=DefaultCorrelation, parentZone=DefaultParentZone) :
        if img == False:
            self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=self.ERROR_IMG_NOT_DEFINED + "")
            raise Exception(self.ERROR_IMG_NOT_DEFINED)
        
        
        if parentZone == False:
                screenshot = pyautogui.screenshot(tempfile.gettempdir() + '/m_screen.png')
                # print("noparent")
        else :
            screenshot = ImageGrab.grab(bbox=(parentZone[0][0],parentZone[0][1],parentZone[1][0],parentZone[1][1]))
            screenshot.save(tempfile.gettempdir() + '/m_screen.png')

        try :
            if validators.url(img) : 
                arr = np.asarray(bytearray(urllib.request.urlopen(img).read()), dtype=np.uint8)
                template = cv2.imdecode(arr,-1) # 'load it as it is'    
            else :
                if os.path.exists(img) :
                    template = cv2.imread(img, cv2.IMREAD_UNCHANGED)
                else :
                    self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=self.ERROR_IMG_URL_NOT_FOUND + "")
                    raise Exception(self.ERROR_IMG_URL_NOT_FOUND)


            arr_parent_zone_img = cv2.imread(tempfile.gettempdir()+'/m_screen.png', cv2.IMREAD_UNCHANGED)
  
        except Exception as inst:         
            self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=self.ERROR_IMG_URL_NOT_FOUND + "")
            raise Exception(self.ERROR_IMG_URL_NOT_FOUND)

        # hh, ww = template.shape[:2]
        base = template[:,:,0:3]
        alpha = template[:,:,3]
        alpha = cv2.merge([alpha,alpha,alpha])
        correlation_real = cv2.matchTemplate(arr_parent_zone_img, base, cv2.TM_CCORR_NORMED, mask=alpha)
        
        loc = np.where(correlation_real >= correlation)
        
        # print(len(loc[0]))
        if self.VERBOSE_MODE == True :
            self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.VERBOSE, comment ="visible : "+ str(len(loc[0]) > 0 and len(loc[1]) > 0))

        if len(loc[0]) > 0 and len(loc[1]) > 0 :
            return True

        return False
        
    #Fonction permettant de vérifier sur l'image est présente ou non  à l'écran (Renvoie False ou une Zone)
    def _isVisibleBis(self, img=False, correlation=DefaultCorrelation, parentZone=DefaultParentZone) :
        if img == False:
            self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=self.ERROR_IMG_NOT_DEFINED + "")
            raise Exception(self.ERROR_IMG_NOT_DEFINED)
        
        if parentZone == False:
            screenshot = pyautogui.screenshot(tempfile.gettempdir() + '/m_screen.png')
        else :
            screenshot = ImageGrab.grab(bbox=(parentZone[0][0],parentZone[0][1],parentZone[1][0],parentZone[1][1]))
            screenshot.save(tempfile.gettempdir() + '/m_screen.png')

        try :
            if validators.url(img) : 
                arr = np.asarray(bytearray(urllib.request.urlopen(img).read()), dtype=np.uint8)
                template = cv2.imdecode(arr,-1) # 'load it as it is'    
            else :
                if os.path.exists(img) :
                    template = cv2.imread(img, cv2.IMREAD_UNCHANGED)
                else :
                    self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=self.ERROR_IMG_URL_NOT_FOUND + "")
                    raise Exception(self.ERROR_IMG_URL_NOT_FOUND)


            arr_parent_zone_img = cv2.imread(tempfile.gettempdir()+'/m_screen.png', cv2.IMREAD_UNCHANGED)
  
        except Exception as inst:         
            self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=self.ERROR_IMG_URL_NOT_FOUND + "")
            raise Exception(self.ERROR_IMG_URL_NOT_FOUND)

        hh, ww = template.shape[:2]
        base = template[:,:,0:3]
        alpha = template[:,:,3]

        trans_indexes = np.argwhere(alpha == 0)
        if trans_indexes.size != 0 :
            first_index_alpha = trans_indexes[0]
            last_index_alpha = trans_indexes[-1]
        else :
            first_index_alpha = False
            last_index_alpha = False

        alpha = cv2.merge([alpha,alpha,alpha])
        correlation_real = cv2.matchTemplate(arr_parent_zone_img, base, cv2.TM_CCORR_NORMED, mask=alpha)

        loc = np.where(correlation_real >= correlation)



        if self.VERBOSE_MODE == True :
            self.writeLog(text="isVisible(img=\""+str(img)+"\", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.VERBOSE, comment ="visible : "+ str(len(loc[0]) > 0 and len(loc[1]) > 0))
        
        if len(loc[0]) > 0 and len(loc[1]) > 0 :
            #loc[3] = ww
            #loc[4] = hh
            #loc.append([first_index_alpha, last_index_alpha])
            #print(type(loc))
            #loc += [first_index_alpha, last_index_alpha]
            if trans_indexes.size != 0 :
                loc = [loc[0], loc[1], ww, hh, [first_index_alpha, last_index_alpha]]
            else :
                loc = [loc[0], loc[1], ww, hh, False]

            #print(loc)

            return loc

        return False

    #Fonction bloquante attendant que l'image spécifiée en argument soit visible à l'écran
    def waitForVisible(self, img=False, timeout=DefaultTimeout, correlation=DefaultCorrelation, parentZone=DefaultParentZone) :
        eventOnVisible = Event()

        listenerThread = threading.Thread(target=self.waitForImgThread, args=(eventOnVisible,img,timeout,correlation,parentZone,True,))
        listenerThread.start()

        eventOnVisible.wait()

        if self.VERBOSE_MODE == True :
            self.writeLog(text="waitForVisible(img=\""+str(img)+"\", timeout="+str(timeout)+", correlation="+str(correlation)+",parentZone="+str(parentZone)+")", type=self.VERBOSE, comment="thread timeout : " + str(self.thread_result != self.thread_result))
        return self.thread_result

    #Fonction bloquante attendant que l'image spécifiée en argument ne soit plus visible à l'écran
    def waitForNotVisible(self, img=False, timeout=DefaultTimeout, correlation=DefaultCorrelation,parentZone=DefaultParentZone) :
        eventOnVisible = Event()

        listenerThread = threading.Thread(target=self.waitForImgThread, args=(eventOnVisible,img,timeout,correlation,parentZone,False,))
        listenerThread.start()

        eventOnVisible.wait()


        if self.VERBOSE_MODE == True :
            self.writeLog(text="waitForNotVisible(img=\""+str(img)+"\", timeout="+str(timeout)+", correlation="+str(correlation)+",parentZone="+str(parentZone)+")", type=self.VERBOSE, comment="thread timeout : " + str(self.thread_result != self.thread_result))

        return self.thread_result

    def waitForImgThread(self, eventOnVisible, img=False, timeout=DefaultTimeout, correlation=DefaultCorrelation, parentZone=DefaultParentZone, visible=True) :

        start_ms = int(round(time.time() * 1000))

        thread_out = False
        while thread_out == False :
            now_ms = int(round(time.time() * 1000))
            if now_ms-start_ms >= timeout :
                thread_out = True
                self.thread_result = False

            if self.isVisible(img, correlation, parentZone) == visible:
                thread_out = True
                self.thread_result = True
        
        eventOnVisible.set()

    #Fonction permettant de récupérer  un tableau de position correspondant à la position de toutes les corrrespondances sur l'écran de l'image spécifiée en argument
    def getAllPosition(self, img=False, timeout=DefaultTimeout, onError=False, ref=CENTER, at=[0,0], correlation=DefaultCorrelation, parentZone=DefaultParentZone, searchInTransp=True) :
        
        if self._checkTypeReference(ref) == False or self._checkTypePosition(at) == False :
            if onError != False :
                return onError
            self.writeLog(text="img="+str(img)+", timeout="+str(timeout)+", onError="+str(onError)+", ref="+str(ref)+", at="+str(at)+", correlation="+str(correlation)+", parentZone="+str(parentZone)+"", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)

        try :
            zones = self.getAllZone(img=img, timeout=timeout, correlation=correlation, parentZone=parentZone)
            # width = (zones[1][0] - zone[0][0])
            # height = (zones[1][1] - zone[0][1])
                # print(loc)
            
            # positions = [[ zones[i][0][0], zones[i][0][1] ] for i in range(len(zones[0]))
            if(parentZone != False) :
                at = [at[0] + parentZone[0][0], at[1] + parentZone[0][1]]


            if len(zones) > 1 :
                if ref == self.TOP_LEFT :
                    if searchInTransp == False :
                        positions = [[ zones[i][0][0]+at[0], zones[i][0][1]+at[1] ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ zones[i][2][0][0]+at[0], zones[i][2][0][1]+at[1] ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ zones[i][0][0]+at[0], zones[i][0][1]+at[1] ] for i in range(len(zones[0])-1)]


                    # position_x = zone[0][0]
                    # position_y = zone[0][1]
                if ref == self.TOP :
                    if searchInTransp == False :
                        positions = [[ zones[i][0][0]+((zones[i][1][0] - zones[i][0][0])/2)+at[0], zones[i][0][1]+at[1] ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ zones[i][2][0][0]+((zones[i][2][1][0] - zones[i][2][0][0])/2)+at[0], zones[i][2][0][1]+at[1] ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ zones[i][0][0]+((zones[i][1][0] - zones[i][0][0])/2)+at[0], zones[i][0][1]+at[1] ] for i in range(len(zones[0])-1)]

                #      position_x = zone[0][0]+(width/2)
                #      position_y = zone[0][1]
                if ref == self.TOP_RIGHT :
                    if searchInTransp == False :
                       positions = [[ zones[i][0][0]+(zones[i][1][0] - zones[i][0][0])+at[0], zones[i][0][1]+at[1] ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ zones[i][2][0][0]+(zones[i][2][1][0] - zones[i][2][0][0])+at[0], zones[i][2][0][1]+at[1] ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ zones[i][0][0]+(zones[i][1][0] - zones[i][0][0])+at[0], zones[i][0][1]+at[1] ] for i in range(len(zones[0])-1)]


                if ref == self.LEFT :
                    if searchInTransp == False :
                        positions = [[ int(zones[i][0][0]+at[0]), int(zones[i][0][1]+ ((zones[i][1][1] - zones[i][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ int(zones[i][2][0][0]+at[0]), int(zones[i][2][0][1]+ ((zones[i][2][1][1] - zones[i][2][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ int(zones[i][0][0]+at[0]), int(zones[i][0][1]+ ((zones[i][1][1] - zones[i][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]




                #      position_x = zone[0][0]
                #      position_y = zone[0][1]+(height/2)
                if ref == self.CENTER :
                    #for i in range(len(zones[0])) :
                    if searchInTransp == False :
                        positions = [[ int(zones[i][0][0]+((zones[i][1][0] - zones[i][0][0])/2)+at[0]), int(zones[i][0][1]+ ((zones[i][1][1] - zones[i][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ int(zones[i][2][0][0]+((zones[i][2][1][0] - zones[i][2][0][0])/2)+at[0]), int(zones[i][2][0][1]+ ((zones[i][2][1][1] - zones[i][2][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ int(zones[i][0][0]+((zones[i][1][0] - zones[i][0][0])/2)+at[0]), int(zones[i][0][1]+ ((zones[i][1][1] - zones[i][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]


                #      position_x = zone[0][0]+(width/2)
                #      position_y = zone[0][1]+(height/2)
                
                if ref == self.RIGHT :
                    if searchInTransp == False :
                        positions = [[ int(zones[i][0][0]+(zones[i][1][0] - zones[i][0][0])+at[0]), int(zones[i][0][1]+ ((zones[i][1][1] - zones[i][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ int(zones[i][2][0][0]+(zones[i][2][1][0] - zones[i][2][0][0])+at[0]), int(zones[i][2][0][1]+ ((zones[i][2][1][1] - zones[i][2][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ int(zones[i][0][0]+(zones[i][1][0] - zones[i][0][0])+at[0]), int(zones[i][0][1]+ ((zones[i][1][1] - zones[i][0][1])/2)+at[1]) ] for i in range(len(zones[0])-1)]


                #      position_x = zone[0][0]+width
                #      position_y = zone[0][1]+(height/2)
                if ref == self.BOT_LEFT :
                    if searchInTransp == False :
                        positions = [[ int(zones[i][0][0]+at[0]), int(zones[i][0][1]+ (zones[i][1][1] - zones[i][0][1])+at[1]) ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ int(zones[i][2][0][0]+at[0]), int(zones[i][2][0][1]+ (zones[i][2][1][1] - zones[i][2][0][1])+at[1]) ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ int(zones[i][0][0]+at[0]), int(zones[i][0][1]+ (zones[i][1][1] - zones[i][0][1])+at[1]) ] for i in range(len(zones[0])-1)]

                #     position_x = zone[0][0]
                #     position_y = zone[0][1]+height
                if ref == self.BOT_RIGHT :
                    if searchInTransp == False :
                        positions = [[ int(zones[i][1][0]+at[0]), int(zones[i][1][1]+at[1]) ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ int(zones[i][2][1][0]+at[0]), int(zones[i][2][1][1]+at[1]) ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ int(zones[i][1][0]+at[0]), int(zones[i][1][1]+at[1]) ] for i in range(len(zones[0])-1)]


                #     position_x = zone[1][0]
                #     position_y = zone[1][1]
                if ref == self.BOT :
                    if searchInTransp == False :
                        positions = [[ zones[i][0][0]+((int(zones[i][1][0] - zones[i][0][0])/2)+at[0]), int(zones[i][0][1]+ (zones[i][1][1] - zones[i][0][1])+at[1]) ] for i in range(len(zones[0])-1)]
                    else :
                        try :
                            positions = [[ zones[i][2][0][0]+((int(zones[i][2][1][0] - zones[i][2][0][0])/2)+at[0]), int(zones[i][2][0][1]+ (zones[i][2][1][1] - zones[i][2][0][1])+at[1]) ] for i in range(len(zones[0])-1)]
                        except Exception :
                            positions = [[ zones[i][0][0]+((int(zones[i][1][0] - zones[i][0][0])/2)+at[0]), int(zones[i][0][1]+ (zones[i][1][1] - zones[i][0][1])+at[1]) ] for i in range(len(zones[0])-1)]


                #     position_x = zone[0][0]+(width/2)
                #     position_y = zone[0][1]+height

                # position_x += at[0]
                # position_y += at[1]
                
                # pyautogui.moveTo(x =position_x, y =position_y)
            else :
                
                width = (zones[0][1][0] - zones[0][0][0])
                height = (zones[0][1][1] - zones[0][0][1])
                position_x = 0;
                position_y = 0;

                if ref == self.TOP_LEFT :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][0][0]
                       position_y = zones[0][0][1]
                    else :
                       position_x = zones[2][0][0]
                       position_y = zones[2][0][1]

                if ref == self.TOP :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][0][0]+(width/2)
                       position_y = zones[0][0][1]
                    else :
                       position_x = zones[2][0][0]+(width/2)
                       position_y = zones[2][0][1]

                if ref == self.TOP_RIGHT :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][0][0]+width
                       position_y = zones[0][0][1]
                    else :
                       position_x = zones[2][0][0]+width
                       position_y = zones[2][0][1]

                if ref == self.LEFT :
                    if searchInTransp == False or zones[0][2] == False:
                       position_x = zones[0][0][0]
                       position_y = zones[0][0][1]+(height/2)
                    else :
                       position_x = zones[2][0][0]
                       position_y = zones[2][0][1]+(height/2)
                if ref == self.CENTER :
                    if searchInTransp == False or zones[0][2] == False:
                       position_x = zones[0][0][0]+(width/2)
                       position_y = zones[0][0][1]+(height/2)
                    else : 
                       position_x = zones[2][0][0]+(width/2)
                       position_y = zones[2][0][1]+(height/2)

                if ref == self.RIGHT :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][0][0]+width
                       position_y = zones[0][0][1]+(height/2)
                    else :
                       position_x = zones[2][0][0]+width
                       position_y = zones[2][0][1]+(height/2)                        


                if ref == self.BOT_LEFT :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][0][0]
                       position_y = zones[0][0][1]+height
                    else :
                       position_x = zones[2][0][0]
                       position_y = zones[2][0][1]+height


                if ref == self.BOT_RIGHT :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][1][0]
                       position_y = zones[0][1][1]
                    else :
                       position_x = zones[2][1][0]
                       position_y = zones[2][1][1]                        

                if ref == self.BOT :
                    if searchInTransp == False or zones[2] == False:
                       position_x = zones[0][0][0]+(width/2)
                       position_y = zones[0][1]+height
                    else :
                       position_x = zones[2][0][0]+(width/2)
                       position_y = zones[2][1]+height                        

                positions = [[int(position_x+at[0]),int(position_y+at[1])]]

            i = 0
            for pos in positions :
                j = 0
                for cord in pos :
                    #if isinstance(positions[i][j], float) == False and isinstance(positions[i][j], int) == False :
                        #positions[i][j] = positions[i][j].item()
                    j = j+1
                i = i+1

            if self.VERBOSE_MODE == True :
                self.writeLog(text="getAllPosition(img=\""+str(img)+"\", timeout="+str(timeout)+", onError="+str(onError)+", ref="+str(ref)+", at="+str(at)+", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.VERBOSE, comment="Positions : " + str(len(zones[0])))



            return positions

        except Exception as e :
            if onError != False :
                return onError
            self.writeLog(text="getAllPosition(img=\""+str(img)+"\", timeout="+str(timeout)+", onError="+str(onError)+", ref="+str(ref)+", at="+str(at)+", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=str(e))
            raise Exception(str(e))

    def getFirstPosition(self, img=False, timeout=DefaultTimeout, onError=False, ref=CENTER, at=[0,0], correlation=DefaultCorrelation, parentZone=DefaultParentZone, searchInTransp=True) :
        try :
            all_zones = self.getAllPosition(img=img,timeout=timeout,onError=onError,ref=ref,at=at,correlation=correlation,parentZone=parentZone, searchInTransp=searchInTransp)
            # pyautogui.moveTo(x =position_x, y =position_y)
            if self.VERBOSE_MODE == True :
                self.writeLog(text="getFirstPosition(img=\""+str(img)+"\", timeout="+str(timeout)+", onError="+str(onError)+", ref="+str(ref)+", at="+str(at)+", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.VERBOSE)

            return all_zones[0]

        except Exception as e :
            if onError != False :
                return onError
            self.writeLog(text="getFirstPosition(img=\""+str(img)+"\", timeout="+str(timeout)+", onError="+str(onError)+", ref="+str(ref)+", at="+str(at)+", correlation="+str(correlation)+", parentZone="+str(parentZone)+")", type=self.ERROR, comment=str(e))
            raise Exception(str(e))

    def move(self, pos=False, fromTo=0):
        
        if self._checkTypePosition(pos) == False :
            self.writeLog(text="move(pos="+str(pos)+", fromTo="+str(fromTo)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)


        if pos == False :
            self.writeLog(text="move(pos="+str(pos)+", fromTo="+str(fromTo)+")", type=self.ERROR, comment=self.ERROR_SPECIFY_POSITION)
            raise Exception(self.ERROR_SPECIFY_POSITION)

        time.sleep(fromTo/1000)

        pyautogui.moveTo(x = pos[0], y = pos[1])

        if self.VERBOSE_MODE == True :
            self.writeLog(text="move(pos="+str(pos)+", fromTo="+str(fromTo)+")", type=self.VERBOSE)

    def moveOn(self, img=False, timeout=DefaultTimeout, onError=False, ref=CENTER, at=[0,0], correlation=DefaultCorrelation, parentZone=DefaultParentZone, fromTo=0) :
        positions = self.getAllPosition(img, timeout, onError, ref, at, correlation, parentZone)

        for pos in positions:
            self.move(pos)

    def pressKey(self, key) :
        if self._checkKeyExist(key) == False :
            self.writeLog(text="pressKey(key="+str(key)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)

        pyautogui.press(key)

        if self.VERBOSE_MODE == True :
            self.writeLog(text="press(key=\""+key+"\")", type=self.VERBOSE)

    def click(self, pos=False, mouse_btn='left', clicks=1, interval=0) :
        interval = interval/1000

        if (self._checkTypePosition(pos) == False and self._checkTypePositions(pos) == False) and self._checkMouseButtonExist(mouse_btn) == False:
            self.writeLog(text="click(pos="+str(pos)+", mouse_btn="+str(mouse_btn)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)
            
        if pos == False :
            self.writeLog(text="click(pos="+str(pos)+")", type=self.ERROR, comment=self.ERROR_SPECIFY_POSITION)
            raise Exception(self.ERROR_SPECIFY_POSITION)
        
        if self._checkTypePositions(pos) :
            for pos_i in pos:
                pyautogui.moveTo(x = pos_i[0], y = pos_i[1])
                pyautogui.click(x = pos_i[0], y = pos_i[1], button=mouse_btn, clicks=clicks, interval=interval)
        elif self._checkTypePosition(pos) :
            pyautogui.moveTo(x = pos[0], y = pos[1])
            pyautogui.click(x = pos[0], y = pos[1], button=mouse_btn, clicks=clicks, interval=interval)

        if self.VERBOSE_MODE == True :
            self.writeLog(text="click(pos="+str(pos)+", mouse_bnt=\""+mouse_btn+"\")", type=self.VERBOSE)

    def clickOn(self, img=False, timeout=DefaultTimeout, onError=False, ref=CENTER, at=[0,0], correlation=DefaultCorrelation, parentZone=DefaultParentZone, mouse_btn='left', clicks=1, interval=0) :
        interval = interval/1000
        positions = self.getAllPosition(img, timeout, onError, ref, at, correlation, parentZone)
        for pos in positions:
            self.click(pos=pos, mouse_btn=mouse_btn, clicks=1, interval=0)

    def getTextAt(self, pos=False, onError=False) :

        if self._checkTypePosition(pos) == False:
            if onError != False :
                return onError

            self.writeLog(text="getTextAt(pos="+str(pos)+", onError="+str(False)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)
            
        self.click(pos)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        self.click(pos)
        copied = Tk().clipboard_get()

        #print(copied)

        if self.VERBOSE_MODE == True :
            self.writeLog(text="getTextAt(pos="+str(pos)+", onError="+str(onError)+")", type=self.VERBOSE)

        return copied
    

    def getOCRTextFromTemplate(self, template, subZone) :
        print()



    def getOCRText(self, zone=False, img=False, onError=False, tesseract_exe='C:\\Program Files\\Tesseract-OCR\\tesseract.exe', readOnlyTransp=True, border_size=20, tesseract_config=False) :
        #print(self._checkTypeZone(zone))

        if os.path.exists(tesseract_exe) == False :
            if onError != False :
                return onError
            self.writeLog(text="getOCRText(pos="+str(zone)+", onError=\""+str(onError)+"\", tesseract_exe=\""+str(tesseract_exe)+"\")", type=self.ERROR, comment="tesseract.exe not found !")
            raise Exception(str("tesseract.exe not found"))
        


        if (self._checkTypeZone(zone) == False and self._checkTypeZones(zone) == False and zone != self.ENTIRE_SCREEN and zone != False) and (img != False):
             if onError != False :
                 return onError
             self.writeLog(text="getOCRText(zone="+str(zone)+", onError="+str(False)+", tesseract_exe=\""+str(tesseract_exe)+"\")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
             raise Exception(self.ERROR_PARAMETERS)
            

        result = []
        #print(tempfile.gettempdir() + '/m_screen_ocr.png')

        if zone == False and img != False :
            zone = self.getAllZone(img=img)

        if self._checkTypeZones(zone) == True :
            for z in zone :
                if readOnlyTransp == True and z[2] != False:
                    screenshot = ImageGrab.grab(bbox=(z[2][0][0],z[2][0][1],z[2][1][0],z[2][1][1]))
                else :
                    screenshot = ImageGrab.grab(bbox=(z[0][0],z[0][1],z[1][0],z[1][1]))
                    
                screenshot.save(tempfile.gettempdir() + '/m_screen_ocr.png')

                img = Image.open(tempfile.gettempdir() + '/m_screen_ocr.png')
                #print(img.quantize(colors=1,method=2).getpalette()[:6])
                rgb_first_pixel = img.quantize(colors=1,method=2).getpalette()[:6]

                colorHex = "#"
                if(rgb_first_pixel[0] < 10) :
                    colorHex = colorHex + "0"                
                colorHex = colorHex + hex(rgb_first_pixel[0])[2:]

                if(rgb_first_pixel[1] < 10) :
                    colorHex = colorHex + "0"                
                colorHex = colorHex + hex(rgb_first_pixel[1])[2:]

                if(rgb_first_pixel[2] < 10) :
                    colorHex = colorHex + "0"                
                colorHex = colorHex + hex(rgb_first_pixel[2])[2:]


                img = ImageOps.expand(img, border=border_size, fill=colorHex)
                img.save(tempfile.gettempdir() + '/m_screen_ocr.png')



                try :
                    pytesseract.pytesseract.tesseract_cmd = r''+tesseract_exe+''

                    if tesseract_config == False :
                        result.append(pytesseract.image_to_string(Image.open(tempfile.gettempdir() + '/m_screen_ocr.png'))[:-2])
                    else :
                        result.append(pytesseract.image_to_string(Image.open(tempfile.gettempdir() + '/m_screen_ocr.png'),config=tesseract_config)[:-2])

                except Exception as e :
                    if onError != False :
                        return onError
                    self.writeLog(text="getOCRText(pos="+str(zone)+", onError=\""+str(onError)+"\", tesseract_exe=\""+str(tesseract_exe)+"\")", type=self.ERROR, comment=str(e))
                    raise Exception(str(e))

        elif self._checkTypeZone(zone) == True :

            if readOnlyTransp == True and zone[2] != False:
                screenshot = ImageGrab.grab(bbox=(zone[2][0][0],zone[2][0][1],zone[2][1][0],zone[2][1][1]))
            else :
                screenshot = ImageGrab.grab(bbox=(zone[0][0],zone[0][1],zone[1][0],zone[1][1]))

            screenshot.save(tempfile.gettempdir() + '/m_screen_ocr.png')

            img = Image.open(tempfile.gettempdir() + '/m_screen_ocr.png')
            rgb_first_pixel = img.quantize(colors=1,method=2).getpalette()[:6]
            colorHex = "#"
            if(rgb_first_pixel[0] < 10) :
                colorHex = colorHex + "0"                
            colorHex = colorHex + hex(rgb_first_pixel[0])[2:]

            if(rgb_first_pixel[1] < 10) :
                colorHex = colorHex + "0"                
            colorHex = colorHex + hex(rgb_first_pixel[1])[2:]

            if(rgb_first_pixel[2] < 10) :
                colorHex = colorHex + "0"                
            colorHex = colorHex + hex(rgb_first_pixel[2])[2:]
                
            img = ImageOps.expand(img, border=border_size, fill=colorHex)
            img.save(tempfile.gettempdir() + '/m_screen_ocr.png')


            #screenshot.save(tempfile.gettempdir() + '/m_screen_ocr.png')
            try :
                pytesseract.pytesseract.tesseract_cmd = r''+tesseract_exe+''
                result = pytesseract.image_to_string(Image.open(tempfile.gettempdir() + '/m_screen_ocr.png'))[:-2]

            except Exception as e :
                if onError != False :
                    return onError
                self.writeLog(text="getOCRText(zone="+str(zone)+", onError=\""+str(onError)+"\", tesseract_exe=\""+str(tesseract_exe)+"\")", type=self.ERROR, comment=str(e))
                raise Exception(str(e))
        
        elif zone == self.ENTIRE_SCREEN :
            screenshot = pyautogui.screenshot(tempfile.gettempdir() + '/m_screen_ocr.png')
            try :
                pytesseract.pytesseract.tesseract_cmd = r''+tesseract_exe+''
                if tesseract_config == False :
                    result = pytesseract.image_to_string(Image.open(tempfile.gettempdir() + '/m_screen_ocr.png'))[:-2]
                else : 
                    result = pytesseract.image_to_string(Image.open(tempfile.gettempdir() + '/m_screen_ocr.png'), config=tesseract_config)[:-2]
            except Exception as e :
                if onError != False :
                    return onError
                self.writeLog(text="getOCRText(zone="+str(zone)+", onError=\""+str(onError)+"\", tesseract_exe=\""+str(tesseract_exe)+"\")", type=self.ERROR, comment="tesseract.exe not found")
                raise Exception(str(e))


        if self.VERBOSE_MODE == True :
            self.writeLog(text="getOCRText(zone="+str(zone)+", onError=\""+str(onError)+"\", tesseract_exe=\""+str(tesseract_exe)+"\")", type=self.VERBOSE)

        return result



    def mouseUp(self, pos=False) :
        if self._checkTypePosition(pos) == True :
            self.move(pos)

        pyautogui.mouseUp();

        
        if self.VERBOSE_MODE == True :
            self.writeLog(text="mouseUp(pos="+str(pos)+")", type=self.VERBOSE)

    def mouseDown(self, pos) :
        if self._checkTypePosition(pos) == True :
            self.move(pos)
        pyautogui.mouseDown();

        if self.VERBOSE_MODE == True :
            self.writeLog(text="mouseDown(pos="+str(pos)+")", type=self.VERBOSE)

    def pressHotKey(self, key1, key2) :
        if self._checkKeyExist(key1) == False or self._checkKeyExist(key2) == False:
            self.writeLog(text="pressHotKey(key1="+str(key1)+", key2=\""+str(key1)+"\")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)


        pyautogui.hotkey(key1, key2)


        if self.VERBOSE_MODE == True :
            self.writeLog(text="hotKey(key1=\""+str(key1)+"\", text=\""+str(key2)+"\")", type=self.VERBOSE)

    def replaceText(self, pos, text=False, interval=0) :
        if (self._checkTypePosition(pos) == False and self._checkTypePositions(pos) == False) and interval < 0 and text == False:
            self.writeLog(text="replaceText(pos="+str(pos)+", text=\""+str(text)+"\", interval="+str(interval)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)


        if (self._checkTypePosition(pos)) :
            self.click(pos)
            pyautogui.hotkey("ctrl", "a")

            if interval != 0 :
                for char in text :
                    time.sleep(interval/1000)
                    pyperclip.copy(char)
                    pyautogui.hotkey("ctrl", "v")

            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            pyperclip.copy('')
            #pyautogui.write(text, interval=interval)    

        if self.VERBOSE_MODE == True :
            self.writeLog(text="replaceText(pos="+str(pos)+", text="+str(text)+", interval="+str(interval)+")", type=self.VERBOSE)



    def typeText(self, text=False, interval=0) :

        if text == False:
            self.writeLog(text="typeText(text="+str(text)+", interval="+str(interval)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)

        if interval != 0 :
            for char in text :
                time.sleep(interval/1000)
                pyperclip.copy(char)
                pyautogui.hotkey("ctrl", "v")
        elif interval == 0 :
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            #pyautogui.write(text, interval=interval)    
            pyperclip.copy('')

        if self.VERBOSE_MODE == True :
            self.writeLog(text="typeText(text="+str(text)+", interval="+str(interval)+")", type=self.VERBOSE)


    def typeAt(self, pos=False, text=False, interval=0) :
        if (self._checkTypePosition(pos) == False and self._checkTypePositions(pos) == False) and interval < 0 and text == False:
            self.writeLog(text="typeAt(pos="+str(pos)+", text=\""+str(text)+"\", interval="+str(interval)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)
            
        if pos == False :
            self.writeLog(text="click(pos="+str(pos)+")", type=self.ERROR, comment=self.ERROR_SPECIFY_POSITION)
            raise Exception(self.ERROR_SPECIFY_POSITION)

        #print(pos)
        #print (type(pos[0][0]))

        if self._checkTypePositions(pos) :
            for pos_i in pos:
                self.click(pos_i)
                if interval != 0 :
                    for char in text :
                        time.sleep(interval/1000)
                        pyperclip.copy(char)
                        pyautogui.hotkey("ctrl", "v")
                else :
                    pyperclip.copy(text)
                    pyautogui.hotkey('ctrl', 'v')
                    #pyautogui.write(text, interval=interval)    
                pyperclip.copy('')

        elif self._checkTypePosition(pos) :
            self.click(pos)

            if interval != 0 :
                for char in text :
                    time.sleep(interval/1000)
                    pyperclip.copy(char)
                    pyautogui.hotkey("ctrl", "v")
            else :
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                #pyautogui.write(text, interval=interval)    
            pyperclip.copy('')





        if self.VERBOSE_MODE == True :
            self.writeLog(text="typeAt(pos="+str(pos)+", text="+str(text)+", interval="+str(interval)+")", type=self.VERBOSE)

    def scroll(self, pos, distance=0) :
        self.click(pos)
        pyautogui.scroll(distance)
        if self.VERBOSE_MODE == True :
            self.writeLog(text="scroll(pos="+str(pos)+", distance="+str(distance)+")", type=self.VERBOSE)

    def doubleClick(self, pos) :
        if (self._checkTypePosition(pos) == False and self._checkTypePositions(pos) == False):
            self.writeLog(text="doubleClick(pos="+str(pos)+")", type=self.ERROR, comment=self.ERROR_PARAMETERS + "")
            raise Exception(self.ERROR_PARAMETERS)
            
        if self._checkTypePositions(pos) :
            for pos_i in pos:
                pyautogui.doubleClick(x = pos_i[0], y = pos_i[1])
        elif self._checkTypePosition(pos) :
            pyautogui.doubleClick(x = pos[0], y = pos[1])


        if self.VERBOSE_MODE == True :
            self.writeLog(text="doubleClick(pos="+str(pos)+")", type=self.VERBOSE)

    def doubleClickOn(self, img=False, timeout=DefaultTimeout, onError=False, ref=CENTER, at=[0,0], correlation=DefaultCorrelation, parentZone=DefaultParentZone, interval=0) :
        positions = self.getAllPosition(img, timeout, onError, ref, at, correlation, parentZone)

        for pos in positions:
            self.doubleClick(pos=pos, interval=interval)

    def initLog(self):
        # if self.VERBOSE_MODE == True :
            # self.writeLog(text="INIT SCRIPT", type=self.INIT)

        self.incrementLine = 0;

        f = open(self.base_path + self.LOG_FILE_NAME, "a")
        e = datetime.datetime.now()
        dateString = "%s:%s:%s - %s:%s:%s" % (e.day, e.month, e.year, e.hour, e.minute, e.second)
        f.write("===== NEW EXECUTION : " + dateString + " =====\n")
        f.close()

    def setVerbose(self, bool) :
        if self.VERBOSE_MODE == True :
            self.writeLog(text="Verbose disables", type=self.VERBOSE)

        self.VERBOSE_MODE = bool

    def writeLog(self, text=False, type="writeLog", comment=False):
        
        f = open(self.base_path + self.LOG_FILE_NAME, "a")
        
        if type == False :
            type = self.DEBUG

        if text != False :
            self.incrementLine = self.incrementLine + 1

            hour_str = ""
            minute_str = ""
            second_str = ""
            month_str = ""
            day_str = ""

            e = datetime.datetime.now()
            if len(str(e.minute)) != 2 :
                minute_str = "0"+str(e.minute)
            else :
                minute_str =str(e.minute)

            if len(str(e.second)) != 2 :
                second_str = "0"+str(e.second)
            else :
                second_str =str(e.second)

            if len(str(e.hour)) != 2 :
                hour_str = "0"+str(e.hour)
            else :
                hour_str =str(e.hour)

            if len(str(e.month)) != 2 :
                month_str = "0"+str(e.month)
            else :
                month_str =str(e.month)

            if len(str(e.day)) != 2 :
                day_str = "0"+str(e.day)
            else :
                day_str =str(e.day)

            dateString = "%s:%s:%s - %s:%s:%s" % (day_str, month_str, e.year, hour_str, minute_str, second_str)
            if comment != False :
                f.write(str(self.incrementLine) + " | " + dateString + " : (" + type + ") "+ text + " - (information : " + comment + ")\n")
            else :
                f.write(str(self.incrementLine) + " | " + dateString + " : (" + type + ") "+ text +"\n")

        f.close()
    
    def setOutPutState(self, output_state):
        if os.path.isdir(self.base_path + self.OUTPUT_PARAMS_DIR_NAME) == False :
            os.mkdir(self.base_path + self.OUTPUT_PARAMS_DIR_NAME)

            if os.path.exists(self.base_path + self.OUTPUT_PARAMS_DIR_NAME + "/" + self.OUTPUT_STATE_FILE_NAME)  == True :
                if self.VERBOSE_MODE == True :
                    self.writeLog(text="setOutPutState(\""+output_state+"\")", type=self.VERBOSE)
            else :
                if self.VERBOSE_MODE == True :
                    self.writeLog(text="setOutPutState(\""+output_state+"\")", type=self.VERBOSE, comment="New OutPutState")


        f = open(self.base_path + self.OUTPUT_PARAMS_DIR_NAME + "/" + self.OUTPUT_STATE_FILE_NAME, "w")
        f.write(output_state)
        f.close()

    def addOutPutParam(self, param, value):
        if os.path.isdir(self.base_path + self.OUTPUT_PARAMS_DIR_NAME) == False :
            os.mkdir(self.base_path + self.OUTPUT_PARAMS_DIR_NAME)


        f = open(self.base_path + self.OUTPUT_PARAMS_DIR_NAME + "/" + param, "w")
        f.write(value)
        f.close()

        if self.VERBOSE_MODE == True :
            self.writeLog(text="addOutPutParam(\""+param+"\",\""+value+"\")", type=self.VERBOSE)

    def addOutPutImage(self, img=ENTIRE_SCREEN, name="img"):
        if os.path.isdir(self.base_path + self.IMAGE_DIR_NAME) == False :
            os.mkdir(self.base_path + self.IMAGE_DIR_NAME)
        
        if self._checkTypeZone(img) :
            screenshot = ImageGrab.grab(bbox=(img[0][0],img[0][1],img[1][0],img[1][1]))
            screenshot.save(self.base_path + self.IMAGE_DIR_NAME + "/" + name +".png")
        elif img == self.ENTIRE_SCREEN :
            screenshot = pyautogui.screenshot(self.base_path + self.IMAGE_DIR_NAME + "/" + name +".png")
        elif validators.url(img) :
            arr = np.asarray(bytearray(urllib.request.urlopen(img).read()), dtype=np.uint8)
            template = cv2.imdecode(arr,-1)
            cv2.imwrite(self.base_path + self.IMAGE_DIR_NAME + "/" + name +".png", template)

        elif os.path.exists(img) :
            shutil.copy(img, self.base_path + self.IMAGE_DIR_NAME)
        else :
            self.writeLog(text="addOutPutImage(img=\""+str(img)+"\")", type=self.ERROR_PARAMETERS, comment="addOutPutImage need zone, url or path to add an outputImage")
            raise Exception(self.ERROR_PARAMETERS)


            

        if self.VERBOSE_MODE == True :
            self.writeLog(text="addOutPutImage(img=\""+str(img)+"\")", type=self.VERBOSE)

    def clearAll(self):
        #remove log file

        if os.path.exists(self.base_path + self.LOG_FILE_NAME) :
            os.remove(self.base_path + self.LOG_FILE_NAME)

        #output state file
        if os.path.exists(self.base_path + self.OUTPUT_STATE_FILE_NAME) :
            os.remove(self.base_path + self.OUTPUT_STATE_FILE_NAME)

        #output param dir
        if os.path.isdir(self.base_path + self.OUTPUT_PARAMS_DIR_NAME) == True :
            shutil.rmtree(self.base_path + self.OUTPUT_PARAMS_DIR_NAME)

        #images dir
        if os.path.isdir(self.base_path + self.IMAGE_DIR_NAME) == True :
            shutil.rmtree(self.base_path + self.IMAGE_DIR_NAME)

        if os.path.isdir("./tmp") == True :
            shutil.rmtree("./tmp")

    def getKalifastVar(self, var_name) :
        if os.path.isdir("./input") == True :
            if os.path.exists("./input/"+var_name) :
                f = open("./input/"+var_name, "r")
                var_value = f.read()
                f.close()
                return var_value

        return False
    
    def getImageFromURL(self, image_url) :
        image = False
        if os.path.isdir("./tmp") == False :
            os.mkdir("./tmp")

        parsed_url = urlparse(image_url)
        captured_value = parse_qs(parsed_url.query)['id'][0]

        path_img = "./tmp/"+captured_value+".png"
        try :
            urllib.request.urlretrieve(image_url, path_img)
        except Exception as e:
            print(e)

        return path_img





class KFT_Zone() :
    def __init__(self,x=False,y=False,width=False,height=False, top_left_x = False,  top_left_y = False, bot_right_x = False, bot_right_y = False) :
        self.x = x;
        self.y = y;
        self.width = width;
        self.height = height;


        self.top_left_x = top_left_x
        self.top_left_y = top_left_y

        self.bot_right_x = bot_right_x
        self.bot_right_y = bot_right_y
    
