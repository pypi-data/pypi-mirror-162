'''创建一个弹窗，并且隐藏多余的Tk主窗口'''

import tkinter as tk
from tkinter import messagebox


def createMessagebox(messagebox_info):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo('提醒', messagebox_info)

if __name__=="__main__":
    createMessagebox('我是提醒的内容')


