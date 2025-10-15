import numpy as np
import cv2
import board_recognition as br
import pyperclip
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

class OthelloRecognizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Othello Board Recognizer")
        self.root.geometry("400x200")
        
        self.image = None
        self.label = tk.Label(root, text="Press Ctrl+V to paste image")
        self.label.pack(pady=10)
        
        self.result_label = tk.Label(root, text="", wraplength=350)
        self.result_label.pack(pady=10)
        
        self.root.bind('<Control-v>', self.paste_and_process)
        
    def paste_and_process(self, event):
        try:
            img = ImageGrab.grabclipboard()
            if img is None:
                messagebox.showerror("Error", "No image found in clipboard.")
                return
            self.image = np.array(img)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
            self.label.config(text="Processing image...")
            self.process_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste image: {e}")
    
    def process_image(self):
        if self.image is None:
            messagebox.showerror("Error", "No image available.")
            return
        
        hint = br.Hint()
        hint.mode = br.Mode.PHOTO
        recognizer = br.AutomaticRecognizer()
        ret, result = recognizer.analyzeBoard(self.image, hint)
        
        if not ret:
            messagebox.showerror("Error", "Board recognition failed.")
            self.label.config(text="Press Ctrl+V to paste image")
            return
        
        CELL = 40
        SIZE = CELL * 8
        board = recognizer.extractBoard(self.image, result.vertex, (SIZE, SIZE))
        bd = np.ones((8, 8), dtype=np.int8) * -1
        bd[result.isUnknown == True] = -2
        
        for d in result.disc:
            if d.color == br.DiscColor.BLACK:
                color = (0, 0, 0)
                line = (255, 255, 255)
            else:
                color = (255, 255, 255)
                line = (0, 0, 0)
            bd[d.cell[0], d.cell[1]] = int(d.color)
            x = int(d.position[1] * SIZE)
            y = int(d.position[0] * SIZE)
            cv2.circle(board, (x, y), 8, line, -1)
            cv2.circle(board, (x, y), 7, color, -1)
        
        for j in range(8):
            for i in range(8):
                x = int((i + 0.5) * CELL)
                y = int((j + 0.5) * CELL)
                if bd[j, i] == -1:
                    cv2.rectangle(board, (x - 4, y - 4), (x + 4, y + 4), (0, 255, 0), -1)
                elif bd[j, i] == -2:
                    cv2.rectangle(board, (x - 4, y - 4), (x + 4, y + 4), (128, 128, 128), -1)
        
        board_str = ''.join(['-' if x == -1 else 'X' if x == 0 else 'O' if x == 1 else '?' for x in bd.flatten()])
        total_discs = np.sum(bd != -1)
        board_str += ' X' if total_discs % 2 == 1 else ' O'
        
        self.result_label.config(text=f"Transcript: {board_str}")
        pyperclip.copy(board_str)
        self.label.config(text="Press Ctrl+V to paste another image")
        messagebox.showinfo("Success", "Transcript copied to clipboard.")

if __name__ == "__main__":
    from PIL import ImageGrab
    root = tk.Tk()
    app = OthelloRecognizerApp(root)
    root.mainloop()