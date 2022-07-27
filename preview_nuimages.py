import tkinter as tk
from tkinter import ttk

import sys
import os
import shutil
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
        self.img_width = 550
        self.img_height = int(self.img_width/1.79)

        self.create_widgets()



    def create_widgets(self):
        # ann_token input area
        self.ann_token_input = ttk.LabelFrame(self)
        self.ann_token_input.configure(text='Instance token')
        self.ann_token_input.grid(column=0, row=0)
        self.ann_token_input.grid(padx=20, pady=35)
        # ann_token input textbox
        self.ann_token = ttk.Entry(self.ann_token_input, width=50)
        self.ann_token.grid(column=0, row=0)
        #File open and Load Image
        self.button_open = ttk.Button(self.ann_token_input)
        self.button_open.configure(text = 'Load')
        self.button_open.grid(column=0, row=1)
        self.button_open.configure(command=self.loadInstance)

        # Canvas annoteted info
        self.ori_img_canvas = tk.Canvas(self)
        self.ori_img_canvas.configure(width=550, height=150, bg='gray')
        self.ori_img_canvas.grid(column=1, row=0)
        self.ori_img_canvas.grid(padx=35, pady=10)

        # Canvas original image
        self.ori_img_frame = ttk.LabelFrame(self)
        self.ori_img_frame.configure(text='Original Image')
        self.ori_img_frame.grid(column=0, row=1)
        self.ori_img_frame.grid(padx=20)
        # Image
        self.ori_img_canvas = tk.Canvas(self.ori_img_frame)
        self.ori_img_canvas.configure(width=self.img_width, height=self.img_height)
        self.ori_img_canvas.grid(column=0, row=0)
        self.ori_img_canvas.grid(padx=0, pady=10)
        # Save Button
        self.ori_save = ttk.Button(self.ori_img_frame)
        self.ori_save.configure(text = 'Save')
        self.ori_save.grid(column=0, row=1)
        self.ori_save.grid(pady=0)
        self.ori_save.configure(command=self.oriSave)

        # Canvas annoteted image
        self.ann_img_frame = ttk.LabelFrame(self)
        self.ann_img_frame.configure(text='Annoteted Image')
        self.ann_img_frame.grid(column=1, row=1)
        self.ann_img_frame.grid(padx=20)
        # Image
        self.ann_img_canvas = tk.Canvas(self.ann_img_frame)
        self.ann_img_canvas.configure(width=self.img_width, height=self.img_height)
        self.ann_img_canvas.grid(column=0, row=0)
        self.ann_img_canvas.grid(padx=0, pady=10)
        # Save Button
        self.ann_save = ttk.Button(self.ann_img_frame)
        self.ann_save.configure(text = 'Save')
        self.ann_save.grid(column=0, row=1)
        self.ann_save.grid(pady=0)
        self.ann_save.configure(command=self.annSave)

    # Event Call Back
    def loadInstance(self):

        #self.folder_name = filedialog.askdirectory()
        self.ann_token = self.ann_token.get()
        #print(self.folder_name)
        # print(self.ann_token)

        try:
            self.ori_img_filepath = ann_datas[self.ann_token]['ori_img']
            self.ori_img_filepath = ori_img_root + self.ori_img_filepath
            print("ori : ", self.ori_img_filepath)

            self.ann_img_filepath = ann_datas[self.ann_token]['ann_img']
            self.ann_img_filepath = ann_img_root + self.ann_img_filepath[2:]
            print("ann : ", self.ann_img_filepath)
        except KeyError:
            print(f"The token ({self.ann_token}) is not defined.")
        except Exception as e:
            print(self.ann_token, e)

        # ori_img
        self.ori_img_bgr = cv2.imread(self.ori_img_filepath)
        self.ori_img_height, self.ori_img_width = self.ori_img_bgr.shape[:2]
        self.ori_img_bgr_resize = cv2.resize(self.ori_img_bgr, (self.img_width, self.img_height), interpolation=cv2.INTER_AREA)
        self.ori_img_rgb = cv2.cvtColor( self.ori_img_bgr_resize, cv2.COLOR_BGR2RGB )  # imreadはBGRなのでRGBに変換
        self.ori_img_PIL = Image.fromarray(self.ori_img_rgb) # RGBからPILフォーマットへ変換
        self.ori_img_tk = ImageTk.PhotoImage(self.ori_img_PIL) # ImageTkフォーマットへ変換
        self.ori_img_canvas.create_image(self.img_width/2, self.img_height/2, image=self.ori_img_tk)

        # ann_img
        self.ann_img_bgr = cv2.imread(self.ann_img_filepath)
        self.ann_img_height, self.ann_img_width = self.ann_img_bgr.shape[:2]
        self.ann_img_bgr_resize = cv2.resize(self.ann_img_bgr, (self.img_width, self.img_height), interpolation=cv2.INTER_AREA)
        self.ann_img_rgb = cv2.cvtColor( self.ann_img_bgr_resize, cv2.COLOR_BGR2RGB )  # imreadはBGRなのでRGBに変換
        self.ann_img_PIL = Image.fromarray(self.ann_img_rgb) # RGBからPILフォーマットへ変換
        self.ann_img_tk = ImageTk.PhotoImage(self.ann_img_PIL) # ImageTkフォーマットへ変換
        self.ann_img_canvas.create_image(self.img_width/2, self.img_height/2, image=self.ann_img_tk)

    def oriSave(self):
        savePath = tk.filedialog.asksaveasfilename(
            initialfile=self.ann_token + "_ori", 
            defaultextension="jpg"
        )
        # self.ori_img_PIL.save(savePath + ".jpg")  # 縮小後の画像が保存される
        try:
            shutil.copy2(self.ori_img_filepath, savePath)
        except PermissionError as e:
            print(f"Permission Error\n保存に失敗した可能性があります．\n{savePath}.jpgを確認してください\n{e}")
        except FileNotFoundError:
            print("Canceled")
        except Exception as e:
            print(f"Undefined Error : {e}\n{self.ori_img_filepath} -> {savePath}")

    def annSave(self):
        savePath = tk.filedialog.asksaveasfilename(
            initialfile=self.ann_token + "_ann", 
            defaultextension="jpg"
        )
        # self.ori_img_PIL.save(savePath + ".jpg")  # 縮小後の画像が保存される
        try:
            shutil.copy2(self.ann_img_filepath, savePath)
        except PermissionError as e:
            print(f"Permission Error\n保存に失敗した可能性があります．\n{savePath}.jpgを確認してください\n{e}")
        except FileNotFoundError:
            print("Canceled")
        except Exception as e:
            print(f"Undefined Error : {e}\n{self.ann_img_filepath} -> {savePath}")


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
