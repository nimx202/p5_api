import tkinter as tk
from tkinter import Scrollbar
import os

def update_text(new_text):
    text_widget.insert(tk.END, new_text)
    text_widget.see(tk.END)  # Scroll to the end of the text

def read_text_from_file():
    try:
        with open("text_data.txt", "r") as file:
            text = file.read()
            update_text(text)
    except FileNotFoundError:
        pass

def clean_text_file():
    try:
        os.remove("text_data.txt")
        text_widget.delete("1.0", tk.END)  # Clear the text widget
    except FileNotFoundError:
        pass

def update_text_periodically():
    # Read text from the file every 40 milliseconds
    read_text_from_file()
    root.after(40, update_text_periodically)

def clean_file_periodically():
    # Clean the text file every 10 seconds
    clean_text_file()
    root.after(10000, clean_file_periodically)

root = tk.Tk()
root.title("Text Receiver")
root.geometry("800x400")

scrollbar = Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_widget = tk.Text(root, wrap=tk.WORD, yscrollcommand=scrollbar.set)
text_widget.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=text_widget.yview)

# Read text from the file when the GUI starts
read_text_from_file()

# Start updating text periodically
update_text_periodically()

# Start cleaning the text file periodically
clean_file_periodically()

root.mainloop()
