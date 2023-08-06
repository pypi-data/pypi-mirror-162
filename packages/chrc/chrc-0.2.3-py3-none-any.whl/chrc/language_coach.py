# external libraries
import pandas as pd
import langid
from gtts import gTTS
try:
    from chrc.playsound import playsound
except:
    from chrc.playsound import playsound
import pyaudio
from pyaudio import PyAudio,paInt16
import wave
import speech_recognition as sr
from thefuzz import fuzz
from zhon.hanzi import punctuation
from math import *
# internal libratries
import string
import random
import tkinter as tk
from tkinter import simpledialog
from tkinter import *
from tkinter import messagebox
import datetime,os,time
import threading
from tkinter import filedialog
import threading
import ctypes
import time
import multiprocessing
import _thread

print('import chlt.Chinese_learn')
from chrc.Chinese_learn import *
print(text_display_button)
print('import chlt.gif_play')
from chrc.gif_play import *
print('import chlt.QGUI_widget')
from chrc.QGUI_widget import *

def remove_str_punctuation(txt):
    punctuation_str = punctuation
    for i in punctuation_str:
        txt = txt.replace(i, '')
    punctuation_string = string.punctuation
    for i in punctuation_string:
        txt = txt.replace(i, '')
    return txt

def recognize_wav_audio_file(filename = r'L_record\20220504_071122.wav',lang = 'zh'):
    hellow = sr.AudioFile(filename)
    txt = ''
    r = sr.Recognizer()
    with hellow as source:
        audio = r.record(source)
    try:
        txt = r.recognize_google(audio,language = lang)
    except:
        print('Speech recognition fail!')
        return txt
    return txt

def play_wav(filename):
    chunk = 1024
    # filename = repr(filename)
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                    rate=wf.getframerate(), output=True)

    data = wf.readframes(chunk)  # 读取数据
    # print(data)
    while data != b'':  # 播放
        stream.write(data)
        data = wf.readframes(chunk)
        # print('while循环中！')
        # print(data)
    stream.stop_stream()  # 停止数据流
    stream.close()
    p.terminate()  # 关闭 PyAudio

class time_countdown_thread_with_exception(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        # print(gui.font_s)

    def run(self):

        # target function of the thread class
        try:
            ts = int(self.gui.timer_config)
            self.gui.entry_timer.configure(foreground="#afafaf")
            # while ts >= -0:
            while True:
                self.gui.time_val.set(str(ts))
                ts-=1
                # self.Timer.pack()
                time.sleep(1)
                if ts ==0:
                    # self.gui.Timer.config(text='''Time out''')
                    self.gui.entry_timer.configure(foreground="red")
        except:
            print('except')
        finally:
            print('ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class record_prepare_thread_with_exception(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        # print(gui.font_s)

    def run(self):

        # target function of the thread class
        try:
            status = True
            ts = 3
            # self.gui.button_record.configure(disabledforeground="red")
            # self.gui.button_record.configure(foreground="black")
            self.gui.button_record.config(state = 'disabled')
            # while ts >= -0:
            self.gui.delete_privious_buttons()
            for i in range(3):
                self.gui.button_record.config(text = 'Finish')
                self.gui.label_word.configure(text=str(ts))
                self.gui.label_word.configure(foreground="red")
                ts -=1
                # self.Timer.pack()
                time.sleep(0.25)
                if ts ==0:
                    self.gui.button_record.config(state = 'normal')
                    self.gui.label_word.configure(foreground="white")
                    # self.gui.button_record.configure(disabledforeground="#a3a3a3")
                    txt = self.gui.report_dict['problem'][self.gui.problem_index-1]
                    self.gui.label_word.configure(text='')
                    # self.gui.Timer.config(text='''Time out''')
            self.gui.creat_buttons()
            while self.gui.recording_status:
                status = not status
                time.sleep(0.23)
                if status:
                    self.gui.button_record.configure(background="#002c77")
                    self.gui.button_record.configure(foreground="#ffffff")
                else:
                    self.gui.button_record.configure(background="#d9d9d9")
                    self.gui.button_record.configure(foreground="#000000")
            self.gui.button_record.configure(background="#d9d9d9")
            self.gui.button_record.configure(foreground="#000000")

        except:
            print('except')
        finally:
            print('ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class audio_record_thread_with_exception(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        self.framerate=16000
        self.NUM_SAMPLES=2000
        self.channels=1
        self.sampwidth=2
        self.TIME=10
        # print(gui.font_s)
    def save_wave_file(self,filename,data):
        '''save the data to the wavfile'''
        wf=wave.open(filename,'wb')
        # print('saving...')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.framerate)
        wf.writeframes(b"".join(data))
        wf.close()

    def audio_record(out_file, rec_time):
        status = True
        CHUNK = 1024
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率
        p = pyaudio.PyAudio()
        # 创建音频流
        stream = p.open(format=FORMAT,  # 音频流wav格式
                        channels=CHANNELS,  # 单声道
                        rate=RATE,  # 采样率16000
                        input=True,
                        frames_per_buffer=CHUNK)
        print("recoding...")

        frames = []  # 录制的音频流
        # 录制音频数据
        # for i in range(0, int(RATE / CHUNK * rec_time)):
        while self.gui.recording_status:
            data = stream.read(CHUNK)
            frames.append(data)

        # 录制完成

        stream.stop_stream()
        save_wave_file('01.wav',frames)
        stream.close()
        p.terminate()

        print("Finished")

    def run(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率

        # target function of the thread class
        try:
            self.gui.button_start.config(state='disabled')
            p = pyaudio.PyAudio()
            # 创建音频流
            stream = p.open(format=FORMAT,  # 音频流wav格式
                            channels=CHANNELS,  # 单声道
                            rate=RATE,  # 采样率16000
                            input=True,
                            frames_per_buffer=CHUNK)
            print("recoding...")

            frames = []  # 录制的音频流
            # 录制音频数据
            # for i in range(0, int(RATE / CHUNK * rec_time)):
            while self.gui.recording_status:
                data = stream.read(CHUNK)
                frames.append(data)
                # print(self.gui.recording_status)

            # 录制完成
            if not self.gui.recording_status:
                stream.stop_stream()
                self.save_wave_file(self.gui.cur_audio_record_file_path,frames)
                stream.close()
                p.terminate()
                self.gui.button_start.config(state='normal')
                print("Finished")
        except:
            print('except')
        finally:
            print('ended')

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class language_learner:
    def __init__(self,data_file = 'languages_learn_source.csv'):
        '''This class configures and populates the self.toplevel window.
           self.top is the self.toplevel containing window.'''
        # widgets style
        self.font_s = ('calibre',30,'normal')
        self.font_p = ('calibre',80,'normal')
        # Initialzie status parameter
        self.content_priority = ''
        self.timer_config = 20
        self.rounds_config = 20
        self.problem_index = 0
        self.report_dict = {}
        self.recording_status = False
        self.content_random_order = False
        self.input_text = ''
        self.button_object_list = []
        self.path_source = os.path.join(current_path, "source")
        # create directory
        self.report_path = self.generate_new_folder('L_report')
        self.record_path = self.generate_new_folder('L_record')
        self.source_path = self.generate_new_folder('L_source')
        # self.df = pd.read_csv (data_file,sep = '|')
        # self.df_backup = self.df.copy(deep=True)
        # create widgets
        self.create_top()
        self.create_label_word()
        self.create_button_start()
        self.create_button_record()
        self.create_button_read()
        self.create_button_check()
        self.create_button_before()
        self.create_button_report()
        self.create_entry_rounds()
        self.create_entry_timer()
        self.create_menu()
        # self.create_score
        # self.creat_buttons()
        self.retry_times = 0

    def delete_privious_buttons(self):
        if len(self.button_object_list) > 0:
            for i in self.button_object_list:
                i.delete_button()
                del i
            self.button_object_list = []

    def creat_buttons(self):
        n = len(self.input_text)
        # print(input_text)

        cols = 15
        rows =ceil(n/cols)


        # if cols>7:
        #     button_size=ceil(1270 /(cols*2.23))
        # else:
        #     button_size = 20
        # lenghth = ceil(button_size*cols*2.13)
        # width = ceil(button_size*2.34*4)
        # self.top.geometry(str(lenghth)+"x"+str(width)+"+400+100")
        # print(x)
        button_size = 28
        for j in range(rows+1):
            for i in range(cols):
                if n>0:
                    t = text_display_button(root = self.top,
                    input_text=self.input_text[i+j*cols],
                    button_size = button_size,
                    path_name=self.path_source)
                    # t.grid(row=j+1, column=i)
                    t.place(relx=0.05+i*0.06, rely=0.25+j*0.12)
                    self.button_object_list.append(t)
                    n = n-1

    def create_label_word(self):

        self.label_word = tk.Label(self.top,wraplengt=int(self.top_width*0.99),justify=LEFT)
        self.label_word.place(relx=0.015, rely=0.14, relheight=0.7, relwidth=0.97)
        self.label_word.configure(background="#000000")
        self.label_word.configure(disabledforeground="#a3a3a3")
        self.label_word.configure(foreground="#7dcd66")
        self.label_word.configure(text='''Click [File]-->[Open] to load data.''')
        self.label_word.configure(font=self.font_s)
        self.label_word.config(state= "disabled")

    def create_button_start(self):
        self.button_start = tk.Button(self.top)
        self.button_start.place(relx=0.018, rely=0.870, height=48, width=119)
        self.button_start.configure(activebackground="#ececec")
        self.button_start.configure(activeforeground="#000000")
        self.button_start.configure(background="#d9d9d9")
        self.button_start.configure(disabledforeground="#a3a3a3")
        self.button_start.configure(foreground="#000000")
        self.button_start.configure(highlightbackground="#d9d9d9")
        self.button_start.configure(highlightcolor="black")
        self.button_start.configure(pady="0")
        self.button_start.configure(text='''Start''')
        self.button_start.configure(font=self.font_s)
        self.button_start.configure(command=self.button_start_callback)
        self.button_start.config(state= "disabled")

    def create_button_record(self):
        self.button_record = tk.Button(self.top)
        self.button_record.place(relx=0.28, rely=0.870, height=48, width=119)
        self.button_record.configure(activebackground="#ececec")
        self.button_record.configure(activeforeground="#000000")
        self.button_record.configure(background="#d9d9d9")
        self.button_record.configure(disabledforeground="#a3a3a3")
        self.button_record.configure(foreground="#000000")
        self.button_record.configure(highlightbackground="#d9d9d9")
        self.button_record.configure(highlightcolor="black")
        self.button_record.configure(pady="0")
        self.button_record.configure(text='''Record''')
        self.button_record.configure(font=self.font_s)
        self.button_record.configure(command=self.button_record_callback)
        self.button_record.config(state= "disabled")

    def create_button_read(self):
        self.button_read = tk.Button(self.top)
        self.button_read.place(relx=0.56, rely=0.870, height=48, width=119)
        self.button_read.configure(activebackground="#ececec")
        self.button_read.configure(activeforeground="#000000")
        self.button_read.configure(background="#d9d9d9")
        self.button_read.configure(disabledforeground="#a3a3a3")
        self.button_read.configure(foreground="#000000")
        self.button_read.configure(highlightbackground="#d9d9d9")
        self.button_read.configure(highlightcolor="black")
        self.button_read.configure(pady="0")
        self.button_read.configure(text='''Read''')
        self.button_read.configure(font=self.font_s)
        self.button_read.config(command = self.button_read_callback)
        self.button_read.config(state= "disabled")

    def create_button_check(self):
        self.button_check = tk.Button(self.top)
        # self.button_check.place(relx=0.84, rely=0.870, height=48, width=119)
        self.button_check.place(relx=0.227, rely=0.022, height=48, width=119)
        self.button_check.configure(activebackground="#ececec")
        self.button_check.configure(activeforeground="#000000")
        self.button_check.configure(background="#d9d9d9")
        self.button_check.configure(disabledforeground="#a3a3a3")
        self.button_check.configure(foreground="#000000")
        self.button_check.configure(highlightbackground="#d9d9d9")
        self.button_check.configure(highlightcolor="black")
        self.button_check.configure(pady="0")
        self.button_check.configure(text='''Check''')
        self.button_check.configure(font=self.font_s)
        self.button_check.config(command = self.button_check_callback)
        # self.button_check.config(state= "disabled")

    def create_button_before(self):
        self.button_before = tk.Button(self.top)
        self.button_before.place(relx=0.84, rely=0.870, height=48, width=119)
        self.button_before.configure(activebackground="#ececec")
        self.button_before.configure(activeforeground="#000000")
        self.button_before.configure(background="#d9d9d9")
        self.button_before.configure(disabledforeground="#a3a3a3")
        self.button_before.configure(foreground="#000000")
        self.button_before.configure(highlightbackground="#d9d9d9")
        self.button_before.configure(highlightcolor="black")
        self.button_before.configure(pady="0")
        self.button_before.configure(text='''Before''')
        self.button_before.configure(font=self.font_s)
        self.button_before.config(command = self.button_before_callback)
        self.button_before.config(state= "disabled")

    def create_button_report(self):
        self.button_report = tk.Button(self.top)
        self.button_report.place(relx=0.017, rely=0.022, height=48, width=119)
        self.button_report.configure(activebackground="#ececec")
        self.button_report.configure(activeforeground="#000000")
        self.button_report.configure(background="#d9d9d9")
        self.button_report.configure(disabledforeground="#a3a3a3")
        self.button_report.configure(foreground="#000000")
        self.button_report.configure(highlightbackground="#d9d9d9")
        self.button_report.configure(highlightcolor="black")
        self.button_report.configure(pady="0")
        self.button_report.configure(text='''Report''')
        self.button_report.configure(font=self.font_s)
        self.button_report.config(command = self.button_report_callback)
        self.button_report.config(state= "disabled")

    def create_entry_rounds(self):
        self.rounds_val = tk.StringVar()
        self.rounds_val.set('Rounds')
        self.entry_rounds = tk.Entry(self.top)
        self.entry_rounds.configure(textvariable = self.rounds_val)
        self.entry_rounds.place(relx=0.383, rely=0.022, height=47
                , width=130)
        self.entry_rounds.configure(background="black")
        self.entry_rounds.configure(disabledforeground="#a3a3a3")
        self.entry_rounds.configure(disabledbackground='#242424')
        self.entry_rounds.configure(font=self.font_s)
        self.entry_rounds.configure(foreground="#afafaf")
        self.entry_rounds.configure(insertbackground="#afafaf")
        self.entry_rounds.config(state= "disabled")

    def create_entry_timer(self):
        self.time_val = tk.StringVar()
        self.time_val.set('Timer')
        self.entry_timer = tk.Entry(self.top)
        self.entry_timer.configure(textvariable = self.time_val)
        self.entry_timer.place(relx=0.84, rely=0.022,height=47, width=110)
        self.entry_timer.configure(background="black")
        self.entry_timer.configure(disabledforeground="#a3a3a3")
        self.entry_timer.configure(disabledbackground='#242424')
        self.entry_timer.configure(font=self.font_s)
        self.entry_timer.configure(foreground="#afafaf")
        self.entry_timer.configure(insertbackground="#afafaf")
        self.entry_timer.config(state= "disabled")

    def create_top(self):
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.top = Tk()
        self.top_width = 900
        self.top_height = 450
        self.top.geometry(str(self.top_width)+"x"+str(self.top_height)+"+552+252")
        self.top.minsize(120, 1)
        self.top.maxsize(1924, 1061)
        self.top.resizable(1, 1)
        self.top.title("WORD LEARNER")
        self.top.configure(background="#000000")
        self.top.bind( "<Configure>", self.resize)
    def create_menu(self):
        self.menu = Menu(self.top)
        self.top.config(menu=self.menu)
        self.fileMenu = Menu(self.menu)
        self.fileMenu.add_command(label="Open",command=self.menu_open_callback)
        self.fileMenu.add_command(label="Type", command=self.menu_type_callback)
        # self.fileMenu.add_command(label="Order", command=self.menu_order_callback)
        self.fileMenu.add_command(label="Exit", command=self.menu_Exit_callback)
        self.fileMenu.entryconfig(2, state=DISABLED)
        # self.fileMenu.entryconfig(3, state=DISABLED)
        self.menu.add_cascade(label="File", menu=self.fileMenu)

    def button_start_callback(self):
        if self.button_start['text'] == 'Start' or self.button_start['text'] == 'Next':
            # self.button_start.config(state = 'disabled')
            self.countdown()
            print('next problem index:',self.problem_index)
            # i = self.problem_index
            if self.problem_index == 0:
                self.initialize_widgets_for_start()
                self.generate_problem_list_from_database()
                # print(self.report_dict)

            if self.problem_index < self.rounds_config:
                r = int(self.rounds_val.get())-1
                self.rounds_val.set(str(r))
                txt = self.report_dict['problem'][self.problem_index]
                self.input_text = txt

                self.delete_privious_buttons()
                self.creat_buttons()
                self.label_word.configure(text='')
                self.report_dict['time'][self.problem_index-1]=int(self.timer_config)-int(self.time_val.get())
                self.read(self.input_text)

            if self.problem_index == self.rounds_config:
                self.button_start['text'] = 'Submit'
                self.delete_privious_buttons()
                self.label_word.configure(text='Press Submit button to submit')

            self.problem_index+=1
            if self.problem_index > self.rounds_config:
                self.problem_index = self.rounds_config+1


        elif self.button_start['text'] == 'Submit':
            self.button_start['text'] = 'Start'
            self.report_dict['time'][self.problem_index-2]=int(self.timer_config)-int(self.time_val.get())
            self.problem_index = 0
            self.initialize_widgets_for_stop()
            self.generate_report_file_path()
            self.save_report()

        elif self.button_start['text'] == 'OK':
            if self.problem_index <= self.rounds_config and self.problem_index>0:
                self.report_dict['correct'][self.problem_index-1] = 1
                self.button_start.config(background = '#1ecc3f')
                self.button_record.configure(background="#d9d9d9")

        # if self.problem_index>self.rounds_config:


    def button_read_callback(self):
        if self.button_read['text'] == 'Read':
            # txt = self.label_word['text']
            # print(self.input_text)
            txt = self.input_text
            self.read(self.input_text)
            if self.problem_index <= self.rounds_config and self.problem_index>0:
                # txt = self.report_dict['problem'][self.problem_index-1]
                self.report_dict['if_read'][self.problem_index-1] = True
                # self.report_dict['correct'][self.problem_index-1] = 0
        elif self.button_read['text'] == 'Play':
            record_audio_path = self.report_dict['audio_file'][self.problem_index-1]
            if record_audio_path == '':
                print('No record file is found!')
            else:
                try:
                    self.play_wav(record_audio_path)
                except:
                    print('error for playing!')

    def button_record_callback(self):
        if self.button_record['text'] == 'Record' or self.button_record['text'] == 'Finish':
            self.recording_status = not self.recording_status
            print(self.recording_status)
            if self.recording_status:
                audio_record_file_name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.wav'
                self.cur_audio_record_file_path = os.path.join(self.record_path,audio_record_file_name)
                self.cur_audio_record_file_path = self.cur_audio_record_file_path.replace('\\',"/")
                self.record_audio()
                self.prepare_record()
            else: # button is "Finish"
                self.button_record.config(text = 'Record')
                if self.problem_index <= self.rounds_config and self.problem_index>0:
                    self.report_dict['audio_file'][self.problem_index-1] = self.cur_audio_record_file_path
                    self.report_dict['correct'][self.problem_index-1] = 0
                    problem = self.report_dict['problem'][self.problem_index-1]
                    problem = remove_str_punctuation(problem)
                    print(problem)
                    l = self.check_language_type(problem)
                    print(l)
                    while not os.path.isfile(self.cur_audio_record_file_path):
                        time.sleep(0.2)

                    l=self.check_language_type(problem)
                    txt = recognize_wav_audio_file(self.cur_audio_record_file_path,l)

                    similarity = fuzz.token_sort_ratio(problem,txt)
                    self.report_dict['similarity'][self.problem_index-1] = similarity
                    self.report_dict['recognization'][self.problem_index-1] = txt


                    if self.retry_times < 5:
                        if similarity > 90 :
                            messagebox.showinfo('Very GOOD!', "Very GOOD! You got "+str(similarity))
                            self.button_start_callback()
                            self.retry_times =0
                        elif similarity >60:
                            res = messagebox.askquestion("Not bad",
                                           "It is not bad. You get "+str(similarity)+'. Would you make another try?')
                            if res == 'yes':
                                self.retry_times +=1
                                self.button_record_callback()

                            elif res == 'no':
                                self.retry_times =0
                                self.button_start_callback()
                        elif similarity<=60:
                            messagebox.showinfo('Not OK', "Hmm, You only got "+str(similarity)+'. Please try agagin!')
                            self.retry_times +=1
                            self.button_record_callback()
                    else:
                        messagebox.showinfo('Not OK', 'Hmm, You try too many times, let us skip this')
                        self.retry_times =0
                        self.button_start_callback()


        elif self.button_record['text'] == 'NOK':
            if self.problem_index <= self.rounds_config and self.problem_index>0:
                self.report_dict['correct'][self.problem_index-1] = 0
                self.button_record.config(background = '#f60505')
                self.button_start.configure(background="#d9d9d9")

    def button_before_callback(self):
        if self.button_before['text'] == 'Before':
            # self.button_start.config(state = 'disabled')
            # if self.problem_index < 2:
            #     self.problem_index = 2
            self.button_start['text'] = 'Next'
            self.countdown()
            # self.problem_index
            print('problem index:',self.problem_index)
            # i = self.problem_index
            if self.problem_index == 0:
                self.initialize_widgets_for_start()
                self.generate_problem_list_from_database()
                # print(self.report_dict)

            if self.problem_index >1:
                r = int(self.rounds_val.get())+1
                self.rounds_val.set(str(r))
                txt = self.report_dict['problem'][self.problem_index-2]
                self.input_text = txt
                self.delete_privious_buttons()
                self.creat_buttons()
                self.label_word.configure(text='')
                self.report_dict['time'][self.problem_index-2]=int(self.timer_config)-int(self.time_val.get())
                self.problem_index-=1







    def button_check_callback(self):

        # self.report_df = to_csv(self.report_filename,index=False)
        # self.report_dict['audio_file']
        # print(self.problem_index)
        self.button_record.configure(background="#d9d9d9")
        self.button_start.configure(background="#d9d9d9")
        if self.problem_index == 0:
            res = messagebox.askquestion("Ask",
                               "if load previous report file?")
            if res == 'yes':
                self.report_filename = filedialog.askopenfilename(title = "Select file",filetypes = (("CSV Files","*.csv"),))
                self.report_filename_htm = self.report_filename[:-3]+'htm'

                df = pd.read_csv (self.report_filename)

                if list(df.columns)==['problem', 'correct', 'time', 'if_read', 'audio_file','recognization','similarity'] and len(df['problem'])>0:
                    self.report_dict = df.to_dict('list')
                    self.rounds_config = len(self.report_dict['problem'])
                else:
                    pass
            else:
                pass

            self.initialize_widgets_for_check_start()
        if self.problem_index < self.rounds_config:
            self.rounds_val.set(str(self.problem_index))
            txt = self.report_dict['problem'][self.problem_index]
            self.input_text = txt
            self.delete_privious_buttons()
            self.creat_buttons()
            self.label_word.configure(text='')

        if self.problem_index == self.rounds_config:
            self.initialize_widgets_for_check_stop()
            self.save_report()

        self.problem_index+=1
        if self.problem_index > self.rounds_config:
            self.problem_index = 0

    def button_report_callback(self):
        self.save_report()
        self.problem_index = 0
        self.initialize_widgets_for_check_stop()
        os.system('start chrome '+'\"'+self.report_filename_htm+'\"')


    def initialize_widgets_for_check_start(self):
        if self.rounds_val.get()!='Rounds':
            self.rounds_config = int(self.rounds_val.get())
        else:
            self.rounds_val.set(str(0))

        self.button_report.config(state= "normal")

        self.button_start.config(text = 'OK')
        self.button_start.config(state = 'normal')

        self.button_record.config(text = 'NOK')
        self.button_record.config(state = 'normal')

        self.entry_timer.config(state= "disabled")
        self.entry_rounds.config(state= "disabled")

        self.button_read.config(text = 'Play')
        self.button_read.config(state = 'normal')

        self.button_check.config(text = 'Next')
        self.button_check.config(state = 'normal')

    def initialize_widgets_for_check_stop(self):
        self.rounds_val.set('Rounds')
        self.time_val.set('Timer')
        self.button_report.config(state= "normal")
        self.entry_timer.config(state= "normal")
        self.entry_rounds.config(state= "normal")
        self.button_start.config(text = 'Start')
        self.button_start.config(state= "normal")
        self.button_start.configure(background="#d9d9d9")

        self.button_record.config(text = 'Record')
        self.button_record.config(state = 'disabled')

        self.button_read.config(text = 'Read')
        self.button_read.config(state = 'disabled')
        self.button_read.configure(background="#d9d9d9")

        self.button_check.config(text = 'Check')
        self.button_check.config(state = 'normal')

        self.label_word.config(text = '''Click [Start]''')



    def record_audio(self):
        try:
            self.thread_record_audio.raise_exception()
        except:
            print("no record audio thread")
        self.thread_record_audio = audio_record_thread_with_exception(self)
        self.thread_record_audio.start()

    def prepare_record(self):
        try:
            self.thread_record_prepare.raise_exception()
        except:
            print("no prepare record thread")
        self.thread_record_prepare = record_prepare_thread_with_exception(self)
        self.thread_record_prepare.start()

    def menu_type_callback(self):
        self.content_priority = simpledialog.askinteger("Parameter input",
        'Input prority to select the content in database (Integer):',
        initialvalue=1,
        parent=self.top)
        self.initialize_widgets_for_start()
        self.generate_problem_list_from_database()
        self.problem_index = 0
        self.rounds_val.set(len(self.df_f))
        self.button_start.config(text = 'Start')
        self.button_start.config(state = 'normal')
        # print(type(self.content_priority))
    def menu_order_callback(self):
        res = messagebox.askquestion("Order",
                           "Randomly generate problem?")
        # print(res)
        if res == 'yes':
            self.content_random_order = True
        else:
            self.content_random_order = False

    def menu_Exit_callback(self):
        exit()

    def menu_open_callback(self):
        # self.use_database=True
        self.load_csv()
        self.initialize_widgets_for_start()
        self.generate_problem_list_from_database()
        self.problem_index = 0
        self.rounds_val.set(len(self.df_f))
        self.button_start.config(text = 'Start')
        self.button_start.config(state = 'normal')
        self.fileMenu.entryconfig(2, state=NORMAL)

    def initialize_widgets_for_start(self):
        if self.time_val.get() != 'Timer':
            self.timer_config = int(self.time_val.get())
        else:
            self.time_val.set(str(self.timer_config))
        if self.rounds_val.get()!='Rounds':
            self.rounds_config = int(self.rounds_val.get())
        else:
             self.rounds_val.set(str(self.rounds_config))

        self.button_report.config(state= "disabled")
        self.entry_timer.config(state= "disabled")
        self.entry_rounds.config(state= "disabled")
        self.button_start.config(text = 'Next')
        self.button_record.config(text = 'Record')
        self.button_record.config(state = 'normal')
        self.button_read.config(text = 'Read')
        self.button_read.config(state = 'normal')
        self.button_check.config(state = 'disabled')
        self.button_before.config(state = 'normal')

    def initialize_widgets_for_stop(self):
        self.thread_time_countdown.raise_exception()
        self.rounds_val.set('Rounds')
        self.time_val.set('Timer')
        self.button_report.config(state= "normal")
        self.entry_timer.config(state= "normal")
        self.entry_rounds.config(state= "normal")
        self.button_start.config(text = 'Start')
        self.button_before.config(state = 'disabled')
        self.button_record.config(state = 'disabled')
        self.button_read.config(state = 'disabled')
        self.button_check.config(state = 'normal')
        self.button_start.config(state = 'normal')
        self.label_word.config(text='Please press report to see the result!')


    def load_csv(self):
        input_text = []
        # os.getcwd()
        path_txt = filedialog.askopenfilename(title = "Select file",filetypes = (("CSV Files","*.csv"),))
        try:
            self.df = pd.read_csv (path_txt,sep = '|')
        except:
            self.df = pd.read_csv (path_txt,sep = '|', encoding="GBK")
        self.df_backup = self.df.copy(deep=True)

    def generate_new_folder(self,folder_name = "L_report"):
        current_path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isdir(os.path.join(current_path, folder_name)):
            os.mkdir(os.path.join(current_path, folder_name))
        return os.path.join(current_path, folder_name)
        # return os.path.join(save_path,datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.csv')

    def resize(self,event):
        w = self.label_word.winfo_width()
        # print('width:',int(w*0.99))
        self.label_word.config(wraplengt=int(w*0.99))

    def check_language_type(self,read_text):
        language_type = langid.classify(read_text)
        if language_type[0] == 'en':
            language_type = 'en'
        else:
            language_type = 'zh-cn'
        return language_type
    def read(self,read_text):
        language_type = self.check_language_type(read_text)
        var = gTTS(text = read_text,lang = language_type)

        audio_fname = os.path.join(self.source_path,read_text+'.mp3')
        # print(os.path.isfile(fname))

        if not os.path.isfile(audio_fname):
            # soundfile.write(audio_fname, var, 44100)
            var.save(audio_fname)

        try:
            self.mp3_playing_processing.terminate()

        except:
            print('No mp3 playing processing is running.')
        _thread.start_new_thread(playsound, (audio_fname,))
        # self.mp3_playing_processing = multiprocessing.Process(target=playsound, args=(audio_fname,))
        # self.mp3_playing_processing.start()
        # p.terminate()

        # playsound(audio_fname)
        # playsound(fname)
        # os.system('\"'+audio_fname+'\"')
    def countdown(self):
        try:
            self.thread_time_countdown.raise_exception()
        except:
            print("no thread")
        self.thread_time_countdown = time_countdown_thread_with_exception(self)
        self.thread_time_countdown.start()

    def generate_problem_list_from_database(self):
        self.Problem_list = []
        self.problem_index_list = []
        txt_list,correct_list,in_time_list,audio_file_list = [],[],[],[]
        if_read_status,similarity_list,recognization_list = [],[],[]
        if self.content_priority == '':
            self.df_f = self.df
        else:
            self.df_f = self.df.loc[self.df['type']==self.content_priority]
        # print(self.df_f)
        self.df_f = self.df_f['content'].values.tolist()
        # print(self.df['type'])
        # print(self.df_f)
        # print(range(len(self.df_f)))

        if self.content_random_order:
            for i in range(int(self.rounds_val.get())):
                r = random.randint(0,len(self.df_f)-1)
                self.problem_index_list.append(r)
        else:
            if self.rounds_config>=len(self.df_f):
                self.rounds_config = len(self.df_f)
                self.rounds_val.set(len(self.df_f))
            else:
                pass
            self.problem_index_list = [x for x in range(self.rounds_config)]
        print(self.problem_index_list)
        for i in self.problem_index_list:
            txt = str(self.df_f[i])
            txt_list.append(txt)
            correct_list.append(-1)
            in_time_list.append(0)
            audio_file_list.append('')
            if_read_status.append(False)
            similarity_list.append(-1)
            recognization_list.append('')
        self.report_dict['problem'] = txt_list
        self.report_dict['correct'] = correct_list
        self.report_dict['time'] = in_time_list
        self.report_dict['if_read'] = if_read_status
        self.report_dict['audio_file'] = audio_file_list
        self.report_dict['recognization'] =recognization_list
        self.report_dict['similarity'] =similarity_list
    def play_wav(self,audio_fname):
        try:
            self.wav_playing_processing.terminate()
        except:
            print('No .wav file playing processing is running.')
        _thread.start_new_thread(play_wav, (audio_fname,))
        # self.wav_playing_processing = multiprocessing.Process(target=play_wav, args=(audio_fname,))
        # self.wav_playing_processing.start()
    def generate_report_file_path(self):
        self.report_filename = os.path.join(self.report_path,datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.report_filename_htm = self.report_filename+'.htm'
        self.report_filename = self.report_filename+'.csv'
    def save_report(self):
        self.report_df = pd.DataFrame.from_dict(self.report_dict)
        self.report_df.to_csv(self.report_filename,index=False)
        save_report_d = pd.read_csv(self.report_filename)
        save_report_d.to_html(self.report_filename_htm)

    def main(self):
        self.top.mainloop()

def chrc():
    l_learn = language_learner()
    l_learn.main()

if __name__ == '__main__':
    l_learn = language_learner()
    l_learn.main()
    # play_wav('E:/Python project 2020/amy_study/L_record/20220502_211709.wav')
