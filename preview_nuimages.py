import tkinter as tk
from tkinter import ttk

import sys
import os
from tkinter import *
from tkinter import messagebox,filedialog
import numpy as np
from PIL import Image, ImageTk
import cv2
import json
import ndjson

j_file = '/Volumes/murakamih/work/nuScenes/im_ped/v1.0-mini/ped.ndjson'
ann_datas = {}
ori_img_root = '/Volumes/work/murakamih/nuimages/'
ann_img_root = '/Volumes/murakamih/work/nuScenes/'

class Application(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        self.pack()

        self.master.geometry("1200x600")
        self.master.title("nuImages Preview")
        self.img_height = 308
        self.img_width = 550

        self.create_widgets()



    def create_widgets(self):
        self.filepath_input = ttk.LabelFrame(self)
        self.filepath_input.configure(text='Instance token')
        self.filepath_input.grid(column=1, row=0)
        self.filepath_input.grid(padx=35, pady=35)

        self.filepath_box = ttk.Entry(self.filepath_input, width=50)
        self.filepath_box.grid(column=0, row=0)

        #File open and Load Image
        self.button_open = ttk.Button(self.filepath_input)
        self.button_open.configure(text = 'Load')
        self.button_open.grid(column=0, row=1)
        self.button_open.configure(command=self.loadImage)

        # Canvas original image
        self.ori_img_canvas = tk.Canvas(self)
        self.ori_img_canvas.configure(width=self.img_width, height=self.img_height)
        self.ori_img_canvas.grid(column=1, row=1)
        self.ori_img_canvas.grid(padx=20, pady=50)

        # Canvas annoteted image
        self.ann_img_canvas = tk.Canvas(self)
        self.ann_img_canvas.configure(width=self.img_width, height=self.img_height)
        self.ann_img_canvas.grid(column=2, row=1)
        self.ann_img_canvas.grid(padx=20, pady=50)

    # Event Call Back
    def loadImage(self):

        #self.folder_name = filedialog.askdirectory()
        self.ann_token = self.filepath_box.get()
        #print(self.folder_name)
        # print(self.ann_token)

        ori_img_filepath = ann_datas[self.ann_token]['ori_img']
        ori_img_filepath = ori_img_root + ori_img_filepath
        print("ori : ", ori_img_filepath)

        ann_img_filepath = ann_datas[self.ann_token]['ann_img']
        ann_img_filepath = ann_img_root + ann_img_filepath[2:]
        print("ann : ", ann_img_filepath)

        # ori_img
        self.ori_img_bgr = cv2.imread(ori_img_filepath)
        self.ori_img_height, self.ori_img_width = self.ori_img_bgr.shape[:2]
        print(self.ori_img_height, self.ori_img_width)
        if self.ori_img_width > self.ori_img_height:
            self.ori_new_size = (self.img_width, self.img_height)
        else:
            self.ori_new_size = (280,500)

        self.ori_img_bgr_resize = cv2.resize(self.ori_img_bgr, self.ori_new_size, interpolation=cv2.INTER_AREA)
        self.ori_img_rgb = cv2.cvtColor( self.ori_img_bgr_resize, cv2.COLOR_BGR2RGB )  # imreadはBGRなのでRGBに変換

       # self.ori_img_rgb = cv2.cvtColor(self.ori_img_bgr, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
        self.ori_img_PIL = Image.fromarray(self.ori_img_rgb) # RGBからPILフォーマットへ変換
        self.ori_img_tk = ImageTk.PhotoImage(self.ori_img_PIL) # ImageTkフォーマットへ変換
        self.ori_img_canvas.create_image(self.img_width/2, self.img_height/2, image=self.ori_img_tk)

        # ann_img
        self.ann_img_bgr = cv2.imread(ann_img_filepath)
        self.ann_img_height, self.ann_img_width = self.ann_img_bgr.shape[:2]
        print(self.ann_img_height, self.ann_img_width)
        if self.ann_img_width > self.ann_img_height:
            self.ann_new_size = (self.img_width, self.img_height)
        else:
            self.ann_new_size = (280,500)

        self.ann_img_bgr_resize = cv2.resize(self.ann_img_bgr, self.ann_new_size, interpolation=cv2.INTER_AREA)
        self.ann_img_rgb = cv2.cvtColor( self.ann_img_bgr_resize, cv2.COLOR_BGR2RGB )  # imreadはBGRなのでRGBに変換
        
        # self.ann_img_rgb = cv2.cvtColor(self.ann_img_bgr, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
        self.ann_img_PIL = Image.fromarray(self.ann_img_rgb) # RGBからPILフォーマットへ変換
        self.ann_img_tk = ImageTk.PhotoImage(self.ann_img_PIL) # ImageTkフォーマットへ変換
        self.ann_img_canvas.create_image(self.img_width/2, self.img_height/2, image=self.ann_img_tk)
        self.ann_img_canvas.create_image(self.img_width/2, self.img_height/2, image=self.ann_img_tk)

def read_json(j_file):
    with open(j_file, 'r') as f:
        ndj = ndjson.load(f)
        tmp = json.dumps(ndj)
        data = json.loads(tmp)
    
    for d in data:
        token = d['token']
        ann_datas[token] = {
            'ori_img'       : d['ori_img'], 
            'ann_img'       : d['new_img'],
            'mask_area'     : d['mask_area'],
            'bbox_height'   : d['bbox_size'][3] - d['bbox_size'][1]  # ymax - ymin
        }

def main():
    read_json(j_file)
    root = tk.Tk()
    app = Application(master=root)  # Inherit
    app.mainloop()

if __name__ == "__main__":
    main()
