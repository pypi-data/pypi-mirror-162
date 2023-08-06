
import tkinter as tk
import re
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import (
#     FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.figure import Figure
# import numpy as np

class QGUI_widget(object):
    def __init__(self,root):
        self.place_info = {'relwidth':0,'relheight':0,'relx':0,'rely':0}

        self.root = root
        self.frame = tk.Frame(root, width=10, height=10)
        # self.frame.config(borderwidth = 3,highlightbackground="black",highlightthickness=1)
        self.widgets = []

        self.create_widgets_inside_frame()
        self.creat_menu()
        self.bind_event()
        self.style()
        self.layout()

    def create_widgets_inside_frame(self):
        pass
        self.widgets = []

    def bind_event(self):
        pass

    def style(self):
        pass

    def layout(self):
        pass

    def bind(self,*arg,**kwargs):
        self.frame.bind(*arg,**kwargs)
    def grid(self,*arg,**kwargs):
        self.frame.grid(*arg,**kwargs)
    def pack(self,*arg,**kwargs):
        self.frame.pack(*arg,**kwargs)
    def place(self,*arg,**kwargs):
        self.frame.place(*arg,**kwargs)

    def creat_menu(self):
        self.m = tk.Menu(self.root, tearoff=0)
        # self.m.add_command(label="Drag and drop",command=self.drag_and_drop)
        self.m.add_command(label="Drag & Zoom on",command = self.zoom_out)
        self.m.add_command(label="Drag & Zoom off",command = self.zoom_off)
        self.m.add_command(label="Disable",command=self.disable_widget)
        self.m.add_command(label="Enable",command=self.enable_widget)
        for widget in self.widgets:
            widget.bind("<Button-3>", self.do_popup)
    def zoom_out(self):
        self.drag_and_drop()
        self.frame.config(borderwidth = 1,highlightbackground="black",highlightthickness=1)
        self.frame.bind("<Button-1>", self.zoom_out_start)
        self.frame.bind("<ButtonRelease-1>", self.release_stop_movement_zoom)


    def zoom_out_start(self,event):
        widget = event.widget
        widget._widget_start_x = widget.winfo_x()
        widget._widget_start_width = widget.winfo_width()
        widget._widget_start_height = widget.winfo_height()
        widget._widget_start_y = widget.winfo_y()
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

        border_judge = self.if_on_border_or_corner_or_corner(event)
        # print(widget._drag_start_y)

            # widget.config(borderwidth = 3,highlightbackground="black",highlightthickness=1)
        if border_judge == 'L':
            self.frame.config(cursor="left_side")
            widget.bind("<B1-Motion>", self.zoom_out_L_motion)
        elif border_judge == 'R':
            self.frame.config(cursor="right_side")
            widget.bind("<B1-Motion>", self.zoom_out_R_motion)
        elif border_judge == 'T':
            self.frame.config(cursor="top_side")
            widget.bind("<B1-Motion>", self.zoom_out_T_motion)
        elif border_judge == 'B':
            self.frame.config(cursor="bottom_side")
            widget.bind("<B1-Motion>", self.zoom_out_B_motion)
        elif border_judge =='TL':
            self.frame.config(cursor="top_left_corner")
            widget.bind("<B1-Motion>", self.zoom_out_TL_motion)
        elif border_judge =='TR':
            self.frame.config(cursor="top_right_corner")
            widget.bind("<B1-Motion>", self.zoom_out_TR_motion)
        elif border_judge =='BL':
            self.frame.config(cursor="bottom_left_corner")
            widget.bind("<B1-Motion>", self.zoom_out_BL_motion)
        elif border_judge =='BR':
            self.frame.config(cursor="bottom_right_corner")
            widget.bind("<B1-Motion>", self.zoom_out_BR_motion)
        elif border_judge==None:
            self.frame.config(cursor="fleur")
            self.drag_and_drop()
            print('work')

    def zoom_out_TL_motion(self,event):
        widget = event.widget
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        zoom_out_x = widget._widget_start_x - x
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        zoom_out_y = widget._widget_start_y - y
        if x<5 or widget._widget_start_width+zoom_out_x<5or y<5 or widget._widget_start_height+zoom_out_y<5:
            pass
        else:
            widget.place(x=x,width = widget._widget_start_width+zoom_out_x,relwidth=0,
            y=y,height = widget._widget_start_height+zoom_out_y,relheight=0,relx=0.0, rely=0.0)

    def zoom_out_TR_motion(self,event):
        widget = event.widget
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        zoom_out_y = widget._widget_start_y - y
        zoom_out_x = x-widget._widget_start_x -widget._widget_start_width
        if widget._widget_start_width + zoom_out_x<4 or x>self.root.winfo_width()-4:
            pass
        elif x<4 or widget._widget_start_width+zoom_out_x<4:
            pass
        else:
            widget.place(x = widget._widget_start_x,width = widget._widget_start_width+zoom_out_x,relwidth=0,
            y=y,height = widget._widget_start_height+zoom_out_y,relheight=0,
            relx=0.0, rely=0.0)

    def zoom_out_BL_motion(self,event):
        widget = event.widget
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        zoom_out_x = widget._widget_start_x - x
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        zoom_out_y = y-widget._widget_start_y -widget._widget_start_height
        if widget._widget_start_height + zoom_out_y<4 or y>self.root.winfo_height()-4:
            pass
        elif x<4 or widget._widget_start_width+zoom_out_x<4:
            pass
        else:
            widget.place(x=x,
            width = widget._widget_start_width+zoom_out_x,
            relwidth=0,
            y = widget._widget_start_y,
            height = widget._widget_start_height+zoom_out_y,
            relheight=0,
            relx=0.0, rely=0.0)

    def zoom_out_BR_motion(self,event):
        widget = event.widget
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        zoom_out_x = x-widget._widget_start_x -widget._widget_start_width
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        zoom_out_y = y-widget._widget_start_y -widget._widget_start_height
        if widget._widget_start_height + zoom_out_y<4 or y>self.root.winfo_height()-4:
            pass
        elif widget._widget_start_width + zoom_out_x<4 or x>self.root.winfo_width()-4:
            pass
        else:
            widget.place(x = widget._widget_start_x,
            width = widget._widget_start_width+zoom_out_x,
            y = widget._widget_start_y,
            height = widget._widget_start_height+zoom_out_y,
            relx=0.0, rely=0.0,
            relwidth=0,relheight=0,
            )

    # def zoom_out_motion(self,event):
    #     pass
    def get_place_info(self):
        print('coodinate of frame')
        print(self.frame.winfo_x())
        print(self.frame.winfo_y())
        print(self.frame.winfo_width())
        print(self.frame.winfo_height())
        self.place_info['x'] = self.frame.winfo_x()
        self.place_info['y'] = self.frame.winfo_y()
        self.place_info['width'] = self.frame.winfo_width()
        self.place_info['height'] = self.frame.winfo_height()

    def zoom_off(self):
        self.get_place_info()
        self.ubind_event()
        self.frame.config(borderwidth = 3,highlightbackground="black",highlightthickness=0)
        self.frame.config(cursor="arrow")
        self.frame.unbind("<B1-Motion>")
        self.frame.unbind("<B1-Motion>")

    def release_stop_movement_zoom(self,event):
        widget = event.widget
        widget.config(borderwidth = 3,highlightbackground="black",highlightthickness=1)
        self.frame.config(cursor="fleur")

    def zoom_out_L_motion(self,event):
        widget = event.widget
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        zoom_out_x = widget._widget_start_x - x
        if x<4 or widget._widget_start_width+zoom_out_x<4:
            pass
        else:
            widget.place(x=x,
            width = widget._widget_start_width+zoom_out_x,
            height= widget._widget_start_height,relwidth=0,relheight=0,
            relx=0.0, rely=0.0)

    def zoom_out_R_motion(self,event):
        widget = event.widget
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        zoom_out_x = x-widget._widget_start_x -widget._widget_start_width
        if widget._widget_start_width + zoom_out_x<4 or x>self.root.winfo_width()-4:
            pass
        else:
            widget.place(x = widget._widget_start_x,
            width = widget._widget_start_width+zoom_out_x,
            height= widget._widget_start_height,relx=0.0, rely=0.0,
            relwidth=0,relheight=0,
            )

    def zoom_out_T_motion(self,event):
        widget = event.widget
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        x = self.root.winfo_pointerx()-self.root.winfo_rootx()
        zoom_out_y = widget._widget_start_y - y
        if y<4 or widget._widget_start_height+zoom_out_y<4:
            pass
        else:
            widget.place(y=y,
            height = widget._widget_start_height+zoom_out_y,
            width = widget._widget_start_width,relx=0.0, rely=0.0,
            relwidth=0,relheight=0,)

    def zoom_out_B_motion(self,event):
        widget = event.widget
        y = self.root.winfo_pointery()-self.root.winfo_rooty()
        zoom_out_y = y-widget._widget_start_y -widget._widget_start_height
        if widget._widget_start_height + zoom_out_y<4 or y>self.root.winfo_height()-4:
            pass
        else:
            widget.place(y = widget._widget_start_y,
            height = widget._widget_start_height+zoom_out_y,
            width = widget._widget_start_width,relx=0.0, rely=0.0,
            relwidth=0,relheight=0)


    def if_on_border_or_corner_or_corner(self,event):
        widget = event.widget
        x = event.x
        y = event.y
        range =10
        x0,y0 = 0,0
        w,h = widget.winfo_width(),widget.winfo_height()

        if_on_left_border = x<x0+range and y>y0+range and y<h-range
        if_on_top_border =  y<y0+range and x>x0+range and x<w-range
        if_on_right_border = x>w-range and y>y0+range and y<h-range
        if_on_bottom_border = y>h-range and x>x0+range and x<w-range
        if_on_tl_corner = y < range and x<range
        if_on_tr_corner = y < range and x>w-range
        if_on_bl_corner = y>h-range and x<range
        if_on_br_corner = y>h-range and x>w-range
        if if_on_left_border:
            print('L')
            widget.config(borderwidth = 3,highlightbackground="black",highlightthickness=1.5)
            return 'L'
        elif if_on_top_border:
            print('T')
            widget.config(borderwidth = 3,highlightbackground="black",highlightthickness=1.5)
            return 'T'
        elif if_on_right_border:
            print('R')
            return 'R'
        elif if_on_bottom_border:
            print('B')
            return 'B'
        elif if_on_tl_corner:
            print('TL')
            return('TL')
        elif if_on_tr_corner:
            print('TR')
            return('TR')
        elif if_on_bl_corner:
            print('BL')
            return('BL')
        elif if_on_br_corner:
            print('BR')
            return('BR')

        return None

    def do_popup(self,event):
        try:
            self.m.tk_popup(event.x_root, event.y_root)
        finally:
            self.m.grab_release()

    def disable_widget(self):
        for widget in self.widgets:
            try:
                widget.configure(state=tk.DISABLED)
            except:
                print(widget)

    def enable_widget(self):
        for widget in self.widgets:
            try:
                widget.configure(state=tk.NORMAL)
            except:
                print(widget)

    def drag_and_drop(self):
        self.frame.focus()
        self.make_draggable(self.widgets)


    def make_draggable(self,widgets):
        for widget in widgets:
            self.frame.config(cursor="fleur")
            widget.bind("<Button-1>", lambda event: self.on_drag_start(event))
            widget.bind("<B1-Motion>", self.on_drag_motion)
            widget.bind("<ButtonRelease-1>", self.release_stop_movement)


    def on_drag_start(self,event):
        # widget = event.widget
        widget = self.frame
        widget._drag_start_x = event.x
        widget._drag_start_y = event.y

    def on_drag_motion(self,event):
        # widget = event.widget
        self.frame.config(borderwidth = 3,highlightbackground="black",highlightthickness=1)
        widget = self.frame
        x = widget.winfo_x() - widget._drag_start_x + event.x
        y = widget.winfo_y() - widget._drag_start_y + event.y
        # print(widget._drag_start_y,event.y)
        if x<0: x=0
        if y<0: y=0
        if x>self.root.winfo_width()-widget.winfo_width():x = self.root.winfo_width()-widget.winfo_width()
        if y>self.root.winfo_height()-widget.winfo_height():y = self.root.winfo_height()-widget.winfo_height()
        widget.place(x=x, y=y,relx=0.0, rely=0.0)

    def ubind_event(self):
        # self.frame.config(cursor="arrow")
        for widget in self.widgets:
            self.frame.config(cursor="arrow")
            widget.unbind("<Button-1>")
            widget.unbind("<B1-Motion>")
            widget.unbind("<ButtonRelease-1>")

    def release_stop_movement(self,event):
        widget=self.frame
        widget._widget_start_x = widget.winfo_x()
        widget._widget_start_width = widget.winfo_width()
        widget._widget_start_height = widget.winfo_height()
        widget._widget_start_y = widget.winfo_y()
        # self.frame.config(borderwidth = 3,highlightbackground="black",highlightthickness=0)
        # self.ubind_event()

    def isfloat(self,s):
        try:
            return float(s)<float('inf')
        except:
            return False

    def isInt(self,s):
        try:
            return int(s)<float('inf')
        except:
            return False
