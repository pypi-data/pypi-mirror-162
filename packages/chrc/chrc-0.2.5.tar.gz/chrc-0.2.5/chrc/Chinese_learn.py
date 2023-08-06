# coding=utf8
from pathlib import Path
# from QGUI_widget import *
import _thread
from gtts import gTTS
from chrc.playsound import playsound
from chrc.gif_play import *
import re
from tkinter import filedialog
from tkinter import *
import requests
import sys,os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
# import pyglet
#
current_path = os.path.dirname(os.path.abspath(__file__))
pwd = os.getcwd()
print(os.path.join(current_path, "source"))
if not os.path.isdir(os.path.join(current_path, "source")):
    os.mkdir(os.path.join(current_path, "source"))
# sys.path.append(os.path.join(current_path, "source"))

gif_display_window = None

class download_chinese_gif_file_from_web:
    def __init__(self,url_head = 'http://bishun.strokeorder.info/mandarin.php?q=',path = 'E:\\Python project 2020\\amy_study\\source' ):
        # self.ch_c = ch_c
        self.url_head =url_head
        self.path = path
    def is_valid(self,url):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def get_all_images(self,url):
        """
        Returns all image URLs on a single `url`
        """
        soup = bs(requests.get(url).content, "html.parser")
        urls = []
        for img in tqdm(soup.find_all("img"), "Extracting images"):
            img_url = img.attrs.get("src")
            if not img_url:
                # if img does not contain src attribute, just skip
                continue
                # make the URL absolute by joining domain with the URL that is just extracted
            img_url = urljoin(url, img_url)
            try:
                pos = img_url.index("?")
                img_url = img_url[:pos]
            except ValueError:
                pass
                    # finally, if the url is valid
            if self.is_valid(img_url):
                urls.append(img_url)
        return urls

    def download(self,url, pathname,filename=''):
        """
        Downloads a file given an URL and puts it in the folder `pathname`
        """
        # if path doesn't exist, make that path dir
        if not os.path.isdir(pathname):
            os.makedirs(pathname)
        # download the body of response by chunk, not immediately
        response = requests.get(url, stream=True)
        # get the total file size
        file_size = int(response.headers.get("Content-Length", 0))
        # get the file name
        if filename=='':
            filename = os.path.join(pathname, url.split("/")[-1])
        else:
            filename = os.path.join(pathname, filename)
        # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
        progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            for data in progress.iterable:
                # write data read to the file
                f.write(data)
                # update the progress bar manually
                progress.update(len(data))
    def main(self,ch_c):
        # get all images
        url = self.url_head+ch_c
        filename = ch_c+'.gif'
        # print('this +96'+filename)
        # print('this +96'+self.path)
        imgs = self.get_all_images(url)
        path = self.path
        for img in imgs:
            # for each image, download it
            if '.gif' in img:
                print(img)
                self.download(img, self.path,filename)

class text_display_button():
    def __init__(self,root,input_text = 'hao',path_name = '',button_size = 85):
        self.input_text = input_text
        s =str(input_text[0].encode('utf-8'))
        x = s.replace('\\','')
        x = x.replace('\'','')
        self.audio_file_coding = x
        self.path_name = path_name
        self.button_size = button_size
        self.root = root
        # QGUI_widget.__init__(self, root)
        self.create_widgets_inside_frame()
        self.download_gif = download_chinese_gif_file_from_web(path=path_name)


        # print(self.widgets)
        # editMenu = tk.Menu(menu)
        # editMenu.add_command(label="Undo")
        # editMenu.add_command(label="Redo")
        # menu.add_cascade(label="Edit", menu=editMenu)

    def load_file(self):
        with open(path_txt, 'r',encoding='UTF-8', errors='ignore') as reader:
            input_text = reader.read()
        # print(input_text)
        input_text=re.findall(r'[\u4e00-\u9fa5]', input_text)
        # input_text = input_text.split('\n')
        # print(input_text)
        input_text_l = []
        for i in input_text:
            if i != '':
                input_text_l.append(i)
        self.input_text_list = input_text_l

    def create_widgets_inside_frame(self):
        # self.w = tk.Text(self.frame, wrap='word',font=("Helvetica", 100))
        # self.w.config(width=2,height=1)
        # self.sb1=tk.Scrollbar(self.frame, orient='horizontal' )
        # self.w.config( yscrollcommand=self.sb1.set )
        # self.sb1.config( command=self.w.xview )
        #
        # self.sb=tk.Scrollbar(self.frame, orient='vertical' )
        # self.w.config( yscrollcommand=self.sb.set )
        # self.sb.config( command=self.w.yview )
        # # self.w.insert(font='Arial 12 italic')
        # self.w.insert(1.0, self.input_text )
        # self.w.config(state=tk.DISABLED)
        self.widgets = []

        self.Button = tk.Button(self.root,text =self.input_text[0],command=self.call_back,font=("SimSun", self.button_size))
        self.Button.config(width=3,height=1)
        self.Button.config(bg = 'black',fg = '#7dcd66',borderwidth = 0)

        # self.w.config(state=tk.DISABLED)

        # self.l = tk.Label(self.frame,text = self.input_text)
        self.widgets.append(self.Button)
    def place(self,*arg,**kwargs):
        self.Button.place(*arg,**kwargs)
    def layout(self):
        self.Button.pack(side=tk.BOTTOM,fill=tk.X)

    def call_back(self):
        _thread.start_new_thread(self.read_and_display,())
    # def read(self):
    #     msg = self.input_text
    #     engine = pyttsx3.init()
    #     newVoiceRate = 230
    #     engine.setProperty('rate',newVoiceRate)
    #     engine.setProperty('Languages','zh')
    #     voices = engine.getProperty('voices')
    #     print(voices[-2])
    #     engine.setProperty('voice', voices[-2].id)
    #     engine.say(msg)
    #     engine.runAndWait()
    #     engine.stop()
    def read(self):
        var = gTTS(text = self.input_text,lang = 'zh-cn')
        import os.path

        audio_fname = os.path.join(self.path_name,self.audio_file_coding+'.mp3')
        # print(os.path.isfile(fname))

        if not os.path.isfile(audio_fname):
            var.save(audio_fname)
        playsound(audio_fname)
        # os.system('\"'+audio_fname+'\"')

    def display_gif_file(self,display_pro = 'system'):
        # ch_gif_fname = self.path_name+self.input_text[0]+'.gif'
        ch_gif_fname = os.path.join(self.path_name,self.input_text[0]+'.gif')
        if not os.path.isfile(ch_gif_fname):
            # print(self.input_text[0]+'.gif')
            # print(type(self.input_text[0]))

            self.download_gif.main(self.input_text[0])
        # display_gif(ch_gif_fname)
        if display_pro == 'system':
            os.system('TASKKILL /F /IM Microsoft.Photos.exe')
            os.system('\"'+ch_gif_fname+'\"')
        else:
            # try:
            #     gif_display_loop.stop_update()
            # except:
            #     print('no after loop!')
            # self.gif_window.destroy()
            # self.gif_window = tk.Toplevel()
            # self.gif_window.geometry('300x300+50+50')

            try:
                global gif_display_window
                gif_display_window.destroy()
            except:
                print('no such window')

            self.gif_window = tk.Toplevel()
            gif_display_window = self.gif_window
            self.gif_window.geometry('300x300+50+50')

            lbl = ImageLabel(self.gif_window)
            lbl.pack()
            # print(ch_gif_fname)
            lbl.load(ch_gif_fname)
            gif_display_loop = lbl
            # return self.gif_window
            print(self.gif_window)
    # def display_gif(self):


    def read_and_display(self):
        self.read()
        self.display_gif_file('o')

    def delete_button(self):
        self.Button.destroy()

from math import *
class main_frame():
    def __init__(self,root):
        self.root = root
        self.root.geometry("796x796+400+100")
        # self.gif_window = tk.Toplevel()
        # self.gif_window.geometry('300x300+50+50')
        # global gif_display_window
        # gif_display_window = self.gif_window
        self.path_source = os.path.join(current_path, "source")
        self.button_object_list = []
        menu = Menu(self.root)
        self.root.config(menu=menu)
        fileMenu = Menu(menu)
        fileMenu.add_command(label="Open",command=self.load)
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="File", menu=fileMenu)
    def exitProgram(self):
        exit()
    def load(self):
        self.load_txt()
        self.delete_privious_buttons()
        self.creat_buttons()
    def delete_privious_buttons(self):
        if len(self.button_object_list) > 0:
            for i in self.button_object_list:
                i.delete_button()
                del i


    def load_txt(self):
        input_text = []
        # os.getcwd()
        path_txt = 'E:\\Python project 2020\\amy_study\\TXTs\\'
        path_txt = filedialog.askopenfilename()
        with open(path_txt, 'r',encoding='UTF-8', errors='ignore') as reader:
            input_text = reader.read()
        # print(input_text)
        input_text=re.findall(r'[\u4e00-\u9fa5]', input_text)
        # input_text = input_text.split('\n')
        # print(input_text)
        input_text_l = []
        for i in input_text:
            if i != '':
                input_text_l.append(i)
        self.input_text = input_text_l

    def creat_buttons(self):
        n = len(self.input_text)
        # print(input_text)

        cols = ceil(n/4.0)
        rows = 4
        if cols>7:
            button_size=ceil(1270 /(cols*2.23))
        else:
            button_size = 85
        lenghth = ceil(button_size*cols*2.13)
        width = ceil(button_size*2.34*4)
        self.root.geometry(str(lenghth)+"x"+str(width)+"+400+100")
        # print(x)

        for j in range(rows+1):
            for i in range(cols):
                if n>0:
                    t = text_display_button(root = self.root,
                    input_text=self.input_text[j*cols+i],
                    button_size = button_size,
                    path_name=self.path_source)
                    t.grid(row=j, column=i)
                    self.button_object_list.append(t)
                    n = n-1

if __name__ == '__main__':
    root=tk.Tk()
    main_frame(root)
    root.mainloop()
