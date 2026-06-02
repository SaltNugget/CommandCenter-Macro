import pydirectinput
import pyautogui
import keyboard
import tkinter as tk
import time
import ctypes
import os
import sys
import json

pydirectinput.PAUSE = 0
pyautogui.PAUSE = 0

running = False
clicker_running = False
f1_pressed = False
f3_pressed = False
start_time = None
clicker_start_time = None
spinner_index = 0
spinner_chars = ['|', '/', '-', '\\']

if getattr(sys, 'frozen', False):
    _base_dir = os.path.dirname(sys.executable)
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))

SETTINGS_FILE = os.path.join(_base_dir, 'cc_settings.json')

def load_settings():
    defaults = {'macro_hotkey': 'f1', 'clicker_hotkey': 'f3', 'failsafe_override': False}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
        defaults.update({k: v for k, v in data.items() if k in defaults})
    except Exception:
        pass
    if not isinstance(defaults['macro_hotkey'], str) or not (1 <= len(defaults['macro_hotkey']) <= 20):
        defaults['macro_hotkey'] = 'f1'
    if not isinstance(defaults['clicker_hotkey'], str) or not (1 <= len(defaults['clicker_hotkey']) <= 20):
        defaults['clicker_hotkey'] = 'f3'
    if not isinstance(defaults['failsafe_override'], bool):
        defaults['failsafe_override'] = False
    return defaults

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({
                'macro_hotkey': macro_hotkey,
                'clicker_hotkey': clicker_hotkey,
                'failsafe_override': failsafe_override,
            }, f)
    except Exception:
        pass

_loaded = load_settings()

macro_hotkey = _loaded['macro_hotkey']
clicker_hotkey = _loaded['clicker_hotkey']
failsafe_override = _loaded['failsafe_override']

rebinding_macro = False
rebinding_clicker = False


def on_macro_hotkey():
    global f1_pressed
    f1_pressed = True

def on_clicker_hotkey():
    global f3_pressed
    f3_pressed = True

def register_hotkeys():
    try:
        keyboard.remove_all_hotkeys()
    except Exception:
        pass
    keyboard.add_hotkey(macro_hotkey, on_macro_hotkey, suppress=True)
    keyboard.add_hotkey(clicker_hotkey, on_clicker_hotkey, suppress=True)

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

def check_hotkeys():
    global f1_pressed, f3_pressed
    if f1_pressed:
        f1_pressed = False
        toggle()
    if f3_pressed:
        f3_pressed = False
        toggle_clicker()
    root.after(50, check_hotkeys)

def toggle():
    global running, start_time

    if not running:
        key = key_entry.get().strip().lower()
        if key == "" or key == "keycode":
            status_label.config(text="Error (Invalid Keycode)", fg="orange")
            return
        try:
            pydirectinput.keyDown(key)
            pydirectinput.keyUp(key)
        except Exception:
            status_label.config(text="Error (Unrecognized Key)", fg="orange")
            return
        delay_val = delay_entry.get()
        if delay_val == "" or delay_val == "DELAY":
            status_label.config(text="Error (Invalid Delay)", fg="orange")
            return
        try:
            d = float(delay_val)
        except ValueError:
            status_label.config(text="Error (Invalid Delay)", fg="orange")
            return
        if d < 0.0001:
            status_label.config(text="Error (Min Delay: 0.0001)", fg="orange")
            return

    running = not running
    if running:
        start_time = time.time()
        status_label.config(text=f"Running ({macro_hotkey.upper()} to stop)", fg="green")
        key_entry.config(state='disabled')
        delay_entry.config(state='disabled')
    else:
        start_time = None
        status_label.config(text=f"Stopped ({macro_hotkey.upper()} to start)", fg="red")
        key_entry.config(state='normal')
        delay_entry.config(state='normal')

def toggle_clicker():
    global clicker_running, clicker_start_time

    if not clicker_running:
        delay_val = clicker_delay_entry.get()
        if delay_val == "" or delay_val == "DELAY":
            clicker_status_label.config(text="Error (Invalid Delay)", fg="orange")
            return
        try:
            d = float(delay_val)
        except ValueError:
            clicker_status_label.config(text="Error (Invalid Delay)", fg="orange")
            return
        if d < 0.0001:
            clicker_status_label.config(text="Error (Min Delay: 0.0001)", fg="orange")
            return

    clicker_running = not clicker_running
    if clicker_running:
        clicker_start_time = time.time()
        clicker_status_label.config(text=f"Running ({clicker_hotkey.upper()} to stop)", fg="green")
        clicker_delay_entry.config(state='disabled')
        clicker_type_menu.config(state='disabled')
    else:
        clicker_start_time = None
        clicker_status_label.config(text=f"Stopped ({clicker_hotkey.upper()} to start)", fg="red")
        clicker_delay_entry.config(state='normal')
        clicker_type_menu.config(state='normal')

def clear_placeholder(entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)

def restore_placeholder(entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)

def get_settings():
    try:
        key = key_entry.get().strip().lower()
        delay = float(delay_entry.get())
        return key, delay
    except ValueError:
        return None, None

def get_clicker_settings():
    try:
        delay = float(clicker_delay_entry.get())
        return delay
    except ValueError:
        return None

def lift_name_canvases():
    root.tk.call('raise', left_name_canvas._w)

def spin():
    global spinner_index
    if running or clicker_running:
        char = spinner_chars[spinner_index % len(spinner_chars)]
        char_reverse = spinner_chars[(-spinner_index) % len(spinner_chars)]
        left_label.config(text=char_reverse)
        right_label.config(text=char)
        spinner_index += 1
    else:
        left_label.config(text='|')
        right_label.config(text='|')
        spinner_index = 0
    root.after(100, spin)

def show_macro():
    clicker_frame.pack_forget()
    settings_frame.pack_forget()
    macro_frame.pack(fill='both', expand=True)
    tab_macro.config(fg='white')
    tab_clicker.config(fg='#888888')
    tab_settings.config(fg='#888888')
    lift_name_canvases()

def show_clicker():
    macro_frame.pack_forget()
    settings_frame.pack_forget()
    clicker_frame.pack(fill='both', expand=True)
    tab_clicker.config(fg='white')
    tab_macro.config(fg='#888888')
    tab_settings.config(fg='#888888')
    lift_name_canvases()

def show_settings():
    macro_frame.pack_forget()
    clicker_frame.pack_forget()
    settings_frame.pack(fill='both', expand=True)
    tab_settings.config(fg='white')
    tab_macro.config(fg='#888888')
    tab_clicker.config(fg='#888888')
    lift_name_canvases()

def make_entry(parent, placeholder):
    frame = tk.Frame(parent, bg='#111111', highlightthickness=0, bd=0)
    entry = tk.Entry(
        frame,
        width=10,
        justify='center',
        bg='#111111',
        fg='white',
        insertbackground='white',
        relief='flat',
        bd=0,
        selectbackground='#111111',
        selectforeground='white',
        highlightthickness=0,
        highlightbackground='#111111',
        highlightcolor='#111111',
        disabledbackground='#111111',
        disabledforeground='#555555'
    )
    entry.insert(0, placeholder)
    entry.pack(padx=1, pady=1)
    entry.bind("<FocusIn>", lambda e: clear_placeholder(entry, placeholder))
    entry.bind("<FocusOut>", lambda e: restore_placeholder(entry, placeholder))
    return frame, entry

def start_rebind_macro():
    global rebinding_macro, rebinding_clicker
    if rebinding_clicker:
        return
    rebinding_macro = True
    macro_bind_btn.config(text="Press a key...", fg='yellow')
    root.bind("<KeyPress>", on_rebind_keypress)

def start_rebind_clicker():
    global rebinding_macro, rebinding_clicker
    if rebinding_macro:
        return
    rebinding_clicker = True
    clicker_bind_btn.config(text="Press a key...", fg='yellow')
    root.bind("<KeyPress>", on_rebind_keypress)

def on_rebind_keypress(event):
    global macro_hotkey, clicker_hotkey, rebinding_macro, rebinding_clicker

    raw = event.keysym.lower()
    key_map = {
        'escape': 'escape', 'return': 'enter', 'space': 'space',
        'tab': 'tab', 'backspace': 'backspace',
    }
    normalized = key_map.get(raw, raw)

    if rebinding_macro:
        if normalized == clicker_hotkey:
            macro_bind_btn.config(text=f"[{macro_hotkey.upper()}]  (click to rebind)", fg='white')
            rebinding_macro = False
            root.unbind("<KeyPress>")
            show_bind_conflict("Macro hotkey can't match Clicker hotkey.")
            return
        macro_hotkey = normalized
        macro_bind_btn.config(text=f"[{macro_hotkey.upper()}]  (click to rebind)", fg='white')
        macro_toggle_btn.config(text=f"Toggle ({macro_hotkey.upper()})")
        rebinding_macro = False
        if not running:
            status_label.config(text=f"Stopped ({macro_hotkey.upper()} to start)", fg="red")
        else:
            status_label.config(text=f"Running ({macro_hotkey.upper()} to stop)", fg="green")

    elif rebinding_clicker:
        if normalized == macro_hotkey:
            clicker_bind_btn.config(text=f"[{clicker_hotkey.upper()}]  (click to rebind)", fg='white')
            rebinding_clicker = False
            root.unbind("<KeyPress>")
            show_bind_conflict("Clicker hotkey can't match Macro hotkey.")
            return
        clicker_hotkey = normalized
        clicker_bind_btn.config(text=f"[{clicker_hotkey.upper()}]  (click to rebind)", fg='white')
        clicker_toggle_btn.config(text=f"Toggle ({clicker_hotkey.upper()})")
        rebinding_clicker = False
        if not clicker_running:
            clicker_status_label.config(text=f"Stopped ({clicker_hotkey.upper()} to start)", fg="red")
        else:
            clicker_status_label.config(text=f"Running ({clicker_hotkey.upper()} to stop)", fg="green")

    root.unbind("<KeyPress>")
    register_hotkeys()
    save_settings()

def show_bind_conflict(msg):
    bind_conflict_label.config(text=msg)
    root.after(2500, lambda: bind_conflict_label.config(text=""))

register_hotkeys()

root = tk.Tk()
root.title("CommandCenter")
root.geometry("250x290")
root.resizable(False, False)
root.config(bg='#111111')

root.update()
HWND = ctypes.windll.user32.GetParent(root.winfo_id())
ctypes.windll.dwmapi.DwmSetWindowAttribute(HWND, 35, ctypes.byref(ctypes.c_int(0x00111111)), 4)

left_label = tk.Label(root, text='|', bg='#111111', fg='white', font=('Courier', 20))
left_label.place(x=5, y=5)

right_label = tk.Label(root, text='|', bg='#111111', fg='white', font=('Courier', 20))
right_label.place(x=224, y=5)

tk.Label(root, text="CommandCenter", bg='#111111', fg='white', font=('Arial', 12, 'bold')).pack(pady=(15, 0))

tab_bar = tk.Frame(root, bg='#111111')
tab_bar.pack(pady=(8, 0))

tab_macro = tk.Label(tab_bar, text="Macro", bg='#111111', fg='white', font=('Arial', 10), cursor='hand2')
tab_macro.pack(side='left', padx=8)
tab_macro.bind("<Button-1>", lambda e: show_macro())

tab_clicker = tk.Label(tab_bar, text="Auto-Clicker", bg='#111111', fg='#888888', font=('Arial', 10), cursor='hand2')
tab_clicker.pack(side='left', padx=8)
tab_clicker.bind("<Button-1>", lambda e: show_clicker())

tab_settings = tk.Label(tab_bar, text="Settings", bg='#111111', fg='#888888', font=('Arial', 10), cursor='hand2')
tab_settings.pack(side='left', padx=8)
tab_settings.bind("<Button-1>", lambda e: show_settings())

tk.Frame(root, bg='#444444', height=1).pack(fill='x', pady=(4, 0), padx=0)

macro_frame = tk.Frame(root, bg='#111111')
macro_frame.pack(fill='both', expand=True)

tk.Label(macro_frame, text="KeyCode:", bg='#111111', fg='white').pack(pady=(10, 0))
key_entry_frame, key_entry = make_entry(macro_frame, "KEYCODE")
key_entry_frame.pack()

tk.Label(macro_frame, text="Delay (Min-0.0001):", bg='#111111', fg='white').pack(pady=(10, 0))
delay_entry_frame, delay_entry = make_entry(macro_frame, "DELAY")
delay_entry_frame.pack()

macro_toggle_btn = tk.Button(macro_frame, text=f"Toggle ({macro_hotkey.upper()})", command=toggle, width=15, bg='#111111', fg='white',
          activebackground='#222222', activeforeground='white', relief='flat')
macro_toggle_btn.pack(pady=10)

status_label = tk.Label(macro_frame, text=f"Stopped ({macro_hotkey.upper()} to start)", fg="red", bg='#111111')
status_label.pack()

clicker_frame = tk.Frame(root, bg='#111111')

tk.Label(clicker_frame, text="MouseButton:", bg='#111111', fg='white').pack(pady=(10, 0))
clicker_type_var = tk.StringVar(value="Left")
clicker_type_menu = tk.OptionMenu(clicker_frame, clicker_type_var, "Left", "Right", "Middle")
clicker_type_menu.config(bg='#111111', fg='white', activebackground='#222222',
                         activeforeground='white', highlightthickness=0, bd=0, relief='flat')
clicker_type_menu["menu"].config(bg='#222222', fg='white', activebackground='#333333', activeforeground='white')
clicker_type_menu.pack()

tk.Label(clicker_frame, text="Delay (Min-0.0001):", bg='#111111', fg='white').pack(pady=(10, 0))
clicker_delay_entry_frame, clicker_delay_entry = make_entry(clicker_frame, "DELAY")
clicker_delay_entry_frame.pack()

clicker_toggle_btn = tk.Button(clicker_frame, text=f"Toggle ({clicker_hotkey.upper()})", command=toggle_clicker, width=15, bg='#111111', fg='white',
          activebackground='#222222', activeforeground='white', relief='flat')
clicker_toggle_btn.pack(pady=10)

clicker_status_label = tk.Label(clicker_frame, text=f"Stopped ({clicker_hotkey.upper()} to start)", fg="red", bg='#111111')
clicker_status_label.pack()

settings_frame = tk.Frame(root, bg='#111111')

tk.Label(settings_frame, text="Macro Hotkey:", bg='#111111', fg='white').pack(pady=(14, 2))
macro_bind_btn = tk.Label(
    settings_frame, text=f"[{macro_hotkey.upper()}]  (click to rebind)",
    bg='#1e1e1e', fg='white', font=('Arial', 9), cursor='hand2',
    relief='flat', padx=8, pady=4
)
macro_bind_btn.pack()
macro_bind_btn.bind("<Button-1>", lambda e: start_rebind_macro())

tk.Label(settings_frame, text="Auto-Clicker Hotkey:", bg='#111111', fg='white').pack(pady=(10, 2))
clicker_bind_btn = tk.Label(
    settings_frame, text=f"[{clicker_hotkey.upper()}]  (click to rebind)",
    bg='#1e1e1e', fg='white', font=('Arial', 9), cursor='hand2',
    relief='flat', padx=8, pady=4
)
clicker_bind_btn.pack()
clicker_bind_btn.bind("<Button-1>", lambda e: start_rebind_clicker())

bind_conflict_label = tk.Label(settings_frame, text="", bg='#111111', fg='orange', font=('Arial', 8))
bind_conflict_label.pack(pady=(4, 0))

tk.Frame(settings_frame, bg='#333333', height=1).pack(fill='x', padx=20, pady=(12, 8))

failsafe_var = tk.BooleanVar(value=failsafe_override)

def on_failsafe_toggle():
    global failsafe_override
    failsafe_override = failsafe_var.get()
    save_settings()

failsafe_check = tk.Checkbutton(
    settings_frame,
    text="Disable 10s failsafe",
    variable=failsafe_var,
    command=on_failsafe_toggle,
    bg='#111111', fg='white',
    activebackground='#111111', activeforeground='white',
    selectcolor='#222222',
    relief='flat'
)
failsafe_check.pack()
tk.Label(settings_frame, text="(allows <0.001s delay indefinitely)", bg='#111111', fg='#666666',
         font=('Arial', 8)).pack()

left_name_canvas = tk.Canvas(root, width=22, height=180, bg='#111111', highlightthickness=0)
left_name_canvas.place(x=2, y=80)
left_name_canvas.create_text(11, 90, text="SaltNugget", fill='#888888', font=('Arial', 11), angle=90)

def loop():
    global running
    if running:
        key, delay = get_settings()
        if key is None or delay is None:
            toggle()
            status_label.config(text="Error (Invalid Settings)", fg="orange")
            root.after(50, loop)
            return
        if not failsafe_override and delay < 0.001 and start_time and (time.time() - start_time) >= 10:
            toggle()
            status_label.config(text="Auto-Stopped (10s limit)", fg="orange")
            root.after(50, loop)
            return
        try:
            pydirectinput.keyDown(key)
            pydirectinput.keyUp(key)
        except Exception:
            toggle()
            status_label.config(text="Error (Key failed)", fg="orange")
            root.after(50, loop)
            return
        root.after(int(delay * 1000), loop)
    else:
        root.after(50, loop)

def clicker_loop():
    global clicker_running
    if clicker_running:
        delay = get_clicker_settings()
        if delay is None:
            toggle_clicker()
            clicker_status_label.config(text="Error (Invalid Settings)", fg="orange")
            root.after(50, clicker_loop)
            return
        if not failsafe_override and delay < 0.001 and clicker_start_time and (time.time() - clicker_start_time) >= 10:
            toggle_clicker()
            clicker_status_label.config(text="Auto-Stopped (10s limit)", fg="orange")
            root.after(50, clicker_loop)
            return
        try:
            btn = clicker_type_var.get().lower()
            pyautogui.click(button=btn)
        except Exception:
            toggle_clicker()
            clicker_status_label.config(text="Error (Click failed)", fg="orange")
            root.after(50, clicker_loop)
            return
        root.after(int(delay * 1000), clicker_loop)
    else:
        root.after(50, clicker_loop)

root.after(50, loop)
root.after(50, check_hotkeys)
root.after(50, clicker_loop)
root.after(100, spin)
try:
    root.iconbitmap(resource_path("Icon-CommandCenter.ico"))
except Exception:
    pass
root.mainloop()





# MADE BY SALTNUGGET