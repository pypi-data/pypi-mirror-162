import tkinter as tk
from PIL import Image, ImageTk
from itertools import count

class ImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 10

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self._job = self.after(self.delay, self.next_frame)
    def stop_update(self):
        if self._job:
            self.after_cancel(self._job)
            self._job = None

def display_gif(path = './source/尽.gif'):
    root = tk.Toplevel()
    root.geometry('300x300+50+50')
    lbl = ImageLabel(root)
    lbl.pack()
    lbl.load(path)
    return root
    # root.mainloop()

if __name__ == "__main__":
    display_gif()
