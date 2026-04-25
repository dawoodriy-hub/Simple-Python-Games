import customtkinter as ctk
from tkinter import messagebox
import time
import threading

ctk.set_appearance_mode("dark")

class ModernToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cool Python Timer Tools")
        self.geometry("400x500")
        
        # Color Palette
        self.bg_purple = "#2D1B4D"
        self.frame_purple = "#3D2B5D"
        self.configure(fg_color=self.bg_purple)

        self.label = ctk.CTkLabel(self, text="COOL PYTHON TIMER TOOLS", font=("Roboto", 24, "bold"), text_color="#E0B0FF")
        self.label.pack(pady=30)

        # Main Buttons
        ctk.CTkButton(self, text="Countdown Timer", fg_color="#6A5ACD", hover_color="#483D8B", corner_radius=20, height=50, width=250, command=lambda: self.open_tool("countdown")).pack(pady=10)
        ctk.CTkButton(self, text="Alarm Clock", fg_color="#2ecc71", hover_color="#27ae60", corner_radius=20, height=50, width=250, command=lambda: self.open_tool("alarm")).pack(pady=10)
        ctk.CTkButton(self, text="Stopwatch", fg_color="#e67e22", hover_color="#d35400", corner_radius=20, height=50, width=250, command=lambda: self.open_tool("stopwatch")).pack(pady=10)

    def open_tool(self, tool_type):
        window = ctk.CTkToplevel(self)
        window.geometry("350x380")
        window.configure(fg_color=self.bg_purple)
        window.attributes("-topmost", True)

        if tool_type == "countdown":
            window.title("Timer")
            self.timer_running = False
            input_frame = ctk.CTkFrame(window, fg_color=self.frame_purple)
            input_frame.pack(pady=20, padx=20)
            h_entry = ctk.CTkEntry(input_frame, width=60, placeholder_text="Hrs", fg_color="#1A0F2E"); h_entry.grid(row=0, column=0, padx=5, pady=10)
            m_entry = ctk.CTkEntry(input_frame, width=60, placeholder_text="Min", fg_color="#1A0F2E"); m_entry.grid(row=0, column=1, padx=5, pady=10)
            s_entry = ctk.CTkEntry(input_frame, width=60, placeholder_text="Sec", fg_color="#1A0F2E"); s_entry.grid(row=0, column=2, padx=5, pady=10)
            display = ctk.CTkLabel(window, text="00:00:00", font=("Roboto", 40, "bold"), text_color="#F0E6FF"); display.pack(pady=20)
            
            def run():
                try:
                    self.timer_running = True
                    total = int(h_entry.get() or 0)*3600 + int(m_entry.get() or 0)*60 + int(s_entry.get() or 0)
                    while total >= 0 and self.timer_running:
                        h_left, rem = divmod(total, 3600); m_left, s_left = divmod(rem, 60)
                        display.configure(text=f"{h_left:02d}:{m_left:02d}:{s_left:02d}")
                        time.sleep(1); total -= 1
                    if total < 0 and self.timer_running:
                        for _ in range(3): print('\a'); time.sleep(0.4)
                        messagebox.showinfo("Done", "Time is up! 🔔")
                except: messagebox.showerror("Error", "Numbers only!")

            btn_f = ctk.CTkFrame(window, fg_color="transparent"); btn_f.pack(pady=10)
            ctk.CTkButton(btn_f, text="Start", width=100, command=lambda: threading.Thread(target=run, daemon=True).start()).grid(row=0, column=0, padx=5)
            ctk.CTkButton(btn_f, text="Reset", width=100, fg_color="#c0392b", command=lambda: [setattr(self, 'timer_running', False), display.configure(text="00:00:00")]).grid(row=0, column=1, padx=5)

        elif tool_type == "stopwatch":
            window.title("Stopwatch")
            self.sw_running = False
            self.sw_elapsed = 0
            sw_display = ctk.CTkLabel(window, text="00:00:00", font=("Roboto", 40, "bold"), text_color="#F0E6FF")
            sw_display.pack(pady=40)
            
            def update():
                if self.sw_running:
                    self.sw_elapsed = int(time.time() - self.start_t)
                    h, rem = divmod(self.sw_elapsed, 3600)
                    m, s = divmod(rem, 60)
                    sw_display.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
                    window.after(1000, update)
            
            def toggle():
                if not self.sw_running:
                    self.sw_running = True
                    self.start_t = time.time() - self.sw_elapsed
                    update()
                else: self.sw_running = False

            def reset_sw():
                self.sw_running = False
                self.sw_elapsed = 0
                sw_display.configure(text="00:00:00")

            btn_f = ctk.CTkFrame(window, fg_color="transparent"); btn_f.pack()
            ctk.CTkButton(btn_f, text="Start/Stop", width=100, fg_color="#e67e22", command=toggle).grid(row=0, column=0, padx=5)
            ctk.CTkButton(btn_f, text="Reset", width=100, fg_color="#c0392b", command=reset_sw).grid(row=0, column=1, padx=5)

        elif tool_type == "alarm":
            window.title("Alarm")
            entry = ctk.CTkEntry(window, placeholder_text="HH:MM", fg_color="#1A0F2E"); entry.insert(0, time.strftime("%H:%M")); entry.pack(pady=40)
            def run_alarm():
                target = entry.get()
                messagebox.showinfo("Alarm", f"Set for {target}")
                while True:
                    if time.strftime("%H:%M") == target:
                        messagebox.showinfo("Alarm", "WAKE UP! ⏰"); break
                    time.sleep(10)
            ctk.CTkButton(window, text="Set Alarm", fg_color="#2ecc71", command=lambda: threading.Thread(target=run_alarm, daemon=True).start()).pack()

if __name__ == "__main__":
    app = ModernToolApp()
    app.mainloop()
