import customtkinter as ctk
from tkinter import messagebox
import time
import threading

ctk.set_appearance_mode("dark")

class ModernToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Neon Digital Suite")
        self.geometry("400x500")
        
        # Neon Purple Theme
        self.bg_purple = "#0F081A"      
        self.frame_purple = "#1A0F2E"   
        self.glow_color = "#D1B3FF"     
        self.configure(fg_color=self.bg_purple)

        self.digit_font = ("Consolas", 44, "bold") 
        self.blink = True # Controls the colon visibility

        self.label = ctk.CTkLabel(self, text="PYTHON TOOLS", font=("Roboto", 26, "bold"), text_color=self.glow_color)
        self.label.pack(pady=30)

        # Main Buttons
        ctk.CTkButton(self, text="Countdown Timer", fg_color="#6A5ACD", corner_radius=20, height=50, width=250, command=lambda: self.open_tool("countdown")).pack(pady=10)
        ctk.CTkButton(self, text="Alarm Clock", fg_color="#2ecc71", corner_radius=20, height=50, width=250, command=lambda: self.open_tool("alarm")).pack(pady=10)
        ctk.CTkButton(self, text="Stopwatch", fg_color="#e67e22", corner_radius=20, height=50, width=250, command=lambda: self.open_tool("stopwatch")).pack(pady=10)

    def open_tool(self, tool_type):
        window = ctk.CTkToplevel(self)
        window.geometry("360x400")
        window.configure(fg_color=self.bg_purple)
        window.attributes("-topmost", True)

        if tool_type == "countdown":
            window.title("Blinking Timer")
            self.timer_running = False
            
            input_frame = ctk.CTkFrame(window, fg_color=self.frame_purple)
            input_frame.pack(pady=20, padx=20)
            
            h_e = ctk.CTkEntry(input_frame, width=65, placeholder_text="Hrs", fg_color=self.bg_purple, border_color=self.glow_color)
            h_e.grid(row=0, column=0, padx=5, pady=10)
            m_e = ctk.CTkEntry(input_frame, width=65, placeholder_text="Min", fg_color=self.bg_purple, border_color=self.glow_color)
            m_e.grid(row=0, column=1, padx=5, pady=10)
            s_e = ctk.CTkEntry(input_frame, width=65, placeholder_text="Sec", fg_color=self.bg_purple, border_color=self.glow_color)
            s_e.grid(row=0, column=2, padx=5, pady=10)

            display = ctk.CTkLabel(window, text="00:00:00", font=self.digit_font, text_color=self.glow_color)
            display.pack(pady=20)
            
            def run():
                try:
                    self.timer_running = True
                    total = int(h_e.get() or 0)*3600 + int(m_e.get() or 0)*60 + int(s_e.get() or 0)
                    while total >= 0 and self.timer_running:
                        h, rem = divmod(total, 3600); m, s = divmod(rem, 60)
                        # Blinking logic
                        sep = ":" if self.blink else " "
                        self.blink = not self.blink
                        display.configure(text=f"{h:02d}{sep}{m:02d}{sep}{s:02d}")
                        time.sleep(0.5) # Update faster for blink effect
                        if self.blink: total -= 1 # Only subtract second every two blinks
                    if total < 0 and self.timer_running:
                        for _ in range(3): print('\a'); time.sleep(0.4)
                        messagebox.showinfo("Done", "Time is up! 🔔")
                except: messagebox.showerror("Error", "Numbers only!")

            btn_f = ctk.CTkFrame(window, fg_color="transparent"); btn_f.pack(pady=10)
            ctk.CTkButton(btn_f, text="Start", width=110, command=lambda: threading.Thread(target=run, daemon=True).start()).grid(row=0, column=0, padx=5)
            ctk.CTkButton(btn_f, text="Reset", fg_color="#c0392b", width=110, command=lambda: [setattr(self, 'timer_running', False), display.configure(text="00:00:00")]).grid(row=0, column=1, padx=5)

        elif tool_type == "stopwatch":
            window.title("Blinking Stopwatch")
            self.sw_running = False
            self.sw_elapsed = 0
            sw_display = ctk.CTkLabel(window, text="00:00:00", font=self.digit_font, text_color=self.glow_color)
            sw_display.pack(pady=40)
            
            def update():
                if self.sw_running:
                    now_el = int(time.time() - self.start_t)
                    h, rem = divmod(now_el, 3600); m, s = divmod(rem, 60)
                    sep = ":" if (int(time.time() * 2) % 2 == 0) else " " # Fast blink logic
                    sw_display.configure(text=f"{h:02d}{sep}{m:02d}{sep}{s:02d}")
                    window.after(250, update) # Refresh 4 times a second

            def toggle():
                if not self.sw_running:
                    self.sw_running = True
                    self.start_t = time.time() - self.sw_elapsed
                    update()
                else:
                    self.sw_running = False
                    self.sw_elapsed = int(time.time() - self.start_t)

            btn_f = ctk.CTkFrame(window, fg_color="transparent"); btn_f.pack()
            ctk.CTkButton(btn_f, text="Start / Stop", width=110, fg_color="#e67e22", command=toggle).grid(row=0, column=0, padx=5)
            ctk.CTkButton(btn_f, text="Reset", fg_color="#c0392b", width=110, command=lambda: [setattr(self, 'sw_running', False), setattr(self, 'sw_elapsed', 0), sw_display.configure(text="00:00:00")]).grid(row=0, column=1, padx=5)

        elif tool_type == "alarm":
            window.title("Digital Alarm")
            e = ctk.CTkEntry(window, placeholder_text="HH:MM", fg_color=self.bg_purple, border_color=self.glow_color, font=("Consolas", 20))
            e.insert(0, time.strftime("%H:%M")); e.pack(pady=50)
            def run_alarm():
                target = e.get()
                messagebox.showinfo("Alarm", f"Set for {target}")
                while True:
                    if time.strftime("%H:%M") == target:
                        messagebox.showinfo("Alarm", "WAKE UP! ⏰"); break
                    time.sleep(5)
            ctk.CTkButton(window, text="Set Alarm", fg_color="#2ecc71", command=lambda: threading.Thread(target=run_alarm, daemon=True).start()).pack()

if __name__ == "__main__":
    app = ModernToolApp()
    app.mainloop()
