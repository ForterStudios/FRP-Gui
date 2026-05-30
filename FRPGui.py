# Fast-Reverse-Proxy GUI
# A simple and efficient GUI for managing your FRP proxies, designed to be as lightweight and user-friendly as possible.
# Author: Asanov Denis (ForterGames)
# Version: 1.2

# Requirements:
# - Python 3.x
# - Tkinter (usually included with Python)
# - pystray (optional, for system tray support)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, re, subprocess, threading, sys, json
import urllib.request
import io 

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = ImageDraw = None

if os.name == 'nt':
    import winreg
else:
    winreg = None

SETTINGS_FILE = "frp_gui_config.json"
TRAY_ICON_FILE = "frp_gui_icon.ico"

# A cute cat gif to make the about tab more enjoyable while checking for updates. You can replace this URL with any other gif you like, just make sure it's not too large to load quickly. The current one is a small, looping cat gif from Giphy.
GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExenV3eHZrMGpzYmIyNWRkYXR4M24xa3YwM2kxcmlhNWJzaDlldXAwciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/G6TgcESZt8FFk8XV7K/giphy.gif"

class FrpcUltimateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fast-Reverse-Proxy GUI v1.2")
        self.root.geometry("600x650")
        self.set_window_icon()
        
        self.filepath = tk.StringVar()
        self.frpc_exe = tk.StringVar()
        self.server_addr = tk.StringVar()
        self.autostart_frp = tk.BooleanVar(value=False)
        self.windows_run = tk.BooleanVar(value=False)
        self.frpc_process = None
        self.tray_icon = None
        
        self.load_settings()
        self.create_widgets()
        self.setup_tray_icon()
        self.load_existing_proxies()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        if self.autostart_frp.get():
            self.root.after(1000, self.start_frpc)

    def set_window_icon(self):
        if not os.path.exists(TRAY_ICON_FILE):
            return
        try:
            if os.name == 'nt':
                self.root.iconbitmap(TRAY_ICON_FILE)
            else:
                icon = tk.PhotoImage(file=TRAY_ICON_FILE)
                self.root.iconphoto(True, icon)
                self._icon_image = icon
        except Exception:
            pass

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.filepath.set(data.get("toml_path", "frpc.toml"))
                    self.frpc_exe.set(data.get("exe_path", "frpc.exe"))
                    self.server_addr.set(data.get("server_addr", "127.0.0.1:7000"))
                    self.autostart_frp.set(data.get("autostart_frp", False))
                    self.windows_run.set(data.get("windows_run", False))
            except: pass
        else:
            self.filepath.set("frpc.toml")
            self.frpc_exe.set("frpc.exe" if os.name == 'nt' else "./frpc")
            self.server_addr.set("127.0.0.1:7000")
            self.autostart_frp.set(False)
            self.windows_run.set(False)

    def save_settings(self, *args):
        data = {
            "toml_path": self.filepath.get(),
            "exe_path": self.frpc_exe.get(),
            "server_addr": self.server_addr.get(),
            "autostart_frp": self.autostart_frp.get(),
            "windows_run": self.windows_run.get()
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
        if winreg: self.toggle_windows_autostart()

    def toggle_windows_autostart(self):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "FRP_GUI"
        path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if self.windows_run.get(): winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{path}"')
            else:
                try: winreg.DeleteValue(key, app_name)
                except: pass
            winreg.CloseKey(key)
        except: pass

    def create_widgets(self):
        path_frame = tk.LabelFrame(self.root, text=" Settings ", padx=10, pady=5)
        path_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(path_frame, text="Config:").grid(row=0, column=0, sticky="w")
        tk.Entry(path_frame, textvariable=self.filepath).grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(path_frame, text="📁", command=self.browse_toml).grid(row=0, column=2)

        tk.Label(path_frame, text="FRPC EXE:").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(path_frame, textvariable=self.frpc_exe).grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(path_frame, text="📁", command=self.browse_exe).grid(row=1, column=2)

        tk.Label(path_frame, text="Server:").grid(row=2, column=0, sticky="w", pady=5)
        server_entry = tk.Entry(path_frame, textvariable=self.server_addr)
        server_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)
        server_entry.bind("<FocusOut>", lambda e: self.save_settings())
        
        check_frame = tk.Frame(path_frame)
        check_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=5)
        tk.Checkbutton(check_frame, text="Run at Windows Startup (Install executable from the Release tab I guess)", variable=self.windows_run, command=self.save_settings).pack(side="left", padx=5)
        tk.Checkbutton(check_frame, text="Autostart FRP", variable=self.autostart_frp, command=self.save_settings).pack(side="left", padx=20)
        path_frame.columnconfigure(1, weight=1)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=5)
        self.tab_manage = ttk.Frame(self.nb); self.tab_logs = ttk.Frame(self.nb); self.tab_about = ttk.Frame(self.nb)
        self.nb.add(self.tab_manage, text=" Ports Manager "); self.nb.add(self.tab_logs, text=" FRP Logs "); self.nb.add(self.tab_about, text=" About ")
        self.setup_manage_tab(); self.setup_logs_tab(); self.setup_about_tab()

    def setup_manage_tab(self):
        add_f = tk.LabelFrame(self.tab_manage, text=" New Proxy ", padx=10, pady=10)
        add_f.pack(fill="x", padx=5, pady=5)
        self.name_v = tk.StringVar(); self.type_v = tk.StringVar(value="tcp"); self.lp_v = tk.StringVar(); self.rp_v = tk.StringVar()
        tk.Label(add_f, text="Name:").grid(row=0, column=0); tk.Entry(add_f, textvariable=self.name_v, width=12).grid(row=0, column=1, padx=2)
        tk.Label(add_f, text="Type:").grid(row=0, column=2); ttk.Combobox(add_f, textvariable=self.type_v, values=["tcp", "udp"], width=5, state="readonly").grid(row=0, column=3, padx=2)
        tk.Label(add_f, text="Local Port:").grid(row=0, column=4); tk.Entry(add_f, textvariable=self.lp_v, width=7).grid(row=0, column=5, padx=2)
        tk.Label(add_f, text="Remote Port:").grid(row=0, column=6); tk.Entry(add_f, textvariable=self.rp_v, width=7).grid(row=0, column=7, padx=2)
        self.lp_v.trace_add("write", lambda *a: self.rp_v.set(self.lp_v.get()))
        tk.Button(add_f, text="➕ ADD", bg="#009F05", fg="white", command=self.add_proxy).grid(row=0, column=8, padx=10)

        list_f = tk.LabelFrame(self.tab_manage, text=" Proxy List ")
        list_f.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree = ttk.Treeview(list_f, columns=("n","t","lp","rp"), show="headings")
        for c, h in zip(("n","t","lp","rp"), ("Name", "Type", "L.Port", "R.Port")): self.tree.heading(c, text=h); self.tree.column(c, width=80)
        self.tree.pack(fill="both", expand=True, side="left")
        sc = ttk.Scrollbar(list_f, command=self.tree.yview); sc.pack(side="right", fill="y"); self.tree.configure(yscrollcommand=sc.set)
        tk.Button(self.tab_manage, text="🗑 Delete Selected", bg="#ff1100", fg="white", command=self.delete_proxy).pack(pady=5)

    def setup_logs_tab(self):
        ctrl = tk.Frame(self.tab_logs, pady=5)
        ctrl.pack(fill="x")
        self.btn_start = tk.Button(ctrl, text="> START FRP <", bg="#2196F3", fg="white", width=15, command=self.start_frpc)
        self.btn_start.pack(side="left", padx=10)
        self.btn_stop = tk.Button(ctrl, text="> ■ STOP <", bg="#9E9E9E", state="disabled", width=10, command=self.stop_frpc)
        self.btn_stop.pack(side="left")
        self.log_area = tk.Text(self.tab_logs, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10), state="disabled")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_about_tab(self):
        tk.Label(self.tab_about, text="| Fast-Reverse-Proxy GUI |\nDesigned for speed and simplicity.\n\nMade with love by ForterGames\n(Asanov Denis)", font=("Arial", 12)).pack(pady=10)
        
        self.version_label = tk.Label(self.tab_about, text="Latest FRP Version: Checking GitHub...", font=("Arial", 10, "bold"), fg="#2196F3")
        self.version_label.pack(pady=5)
        
        self.gif_label = tk.Label(
            self.tab_about, 
            text="Loading cat gif...", 
            compound="top",
            font=("Arial", 10, "italic"), 
            fg="gray"
        )
        self.gif_label.pack(pady=15)
        
        threading.Thread(target=self.fetch_about_data, daemon=True).start()

    def fetch_about_data(self):
        
        try:
            req = urllib.request.Request("https://api.github.com/repos/fatedier/frp/releases/latest", headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=5).read()
            data = json.loads(resp)
            version = data.get("tag_name", "Unknown")
            self.root.after(0, lambda: self.version_label.config(text=f"Latest FRP Version: {version}", fg="#009F05"))
        except Exception:
            self.root.after(0, lambda: self.version_label.config(text="Latest FRP Version: Unavailable (Network error)", fg="#ff1100"))

        try:
            req = urllib.request.Request(GIF_URL, headers={'User-Agent': 'Mozilla/5.0'})
            raw_data = urllib.request.urlopen(req, timeout=10).read()
            
            
            gif_file = io.BytesIO(raw_data)
            
            frames = []
            idx = 0
            while True:
                try:
                    
                    frame = tk.PhotoImage(data=gif_file.getvalue(), format=f"gif -index {idx}")
                    frames.append(frame)
                    idx += 1
                except tk.TclError:
                    
                    break
            
            if frames:
                self.gif_frames = frames
                self.current_frame = 0
                self.root.after(0, self.start_gif_animation)
            else:
                self.root.after(0, lambda: self.gif_label.config(text="No frames in GIF"))
        except Exception as e:
            
            print(f"Error loading GIF: {e}")
            self.root.after(0, lambda: self.gif_label.config(text="Could not load GIF from internet"))

    def start_gif_animation(self):
        self.gif_label.config(text="Doing something cute with FRP...")
        self.animate_gif()

    def animate_gif(self):
        if hasattr(self, 'gif_frames') and self.gif_frames:
            self.gif_label.config(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.root.after(100, self.animate_gif)

    def browse_toml(self):
        f = filedialog.askopenfilename(filetypes=[("TOML", "*.toml")]);
        if f: self.filepath.set(f); self.save_settings(); self.load_existing_proxies()

    def browse_exe(self):
        f = filedialog.askopenfilename(filetypes=[("EXE", "*.exe"), ("All", "*.*")])
        if f: self.frpc_exe.set(f); self.save_settings()

    def load_existing_proxies(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        if not os.path.exists(self.filepath.get()): return
        try:
            with open(self.filepath.get(), "r", encoding="utf-8") as f: content = f.read()
            s_addr_match = re.search(r'serverAddr\s*=\s*"([^"]+)"', content)
            s_port_match = re.search(r'serverPort\s*=\s*(\d+)', content)
            
            if s_addr_match:
                addr = s_addr_match.group(1)
                port = s_port_match.group(1) if s_port_match else "7000"
                self.server_addr.set(f"{addr}:{port}")
                self.save_settings()
            blocks = content.split("[[proxies]]")[1:]
            for b in blocks:
                n = re.search(r'name\s*=\s*"([^"]+)"', b)
                t = re.search(r'type\s*=\s*"([^"]+)"', b)
                lp = re.search(r'localPort\s*=\s*(\d+)', b)
                rp = re.search(r'remotePort\s*=\s*(\d+)', b)
                if n: self.tree.insert("", "end", values=(n.group(1), t.group(1) if t else "tcp", lp.group(1) if lp else "", rp.group(1) if rp else ""))
        except: pass

    def add_proxy(self):
        name, lp, rp = self.name_v.get().strip(), self.lp_v.get().strip(), self.rp_v.get().strip()
        if not name or not lp.isdigit(): return
        
        full_addr = self.server_addr.get().strip()
        if ":" in full_addr:
            s_host, s_port = full_addr.split(":", 1)
            if not s_port.isdigit(): s_port = "7000"
        else:
            s_host, s_port = full_addr, "7000"

        toml_file = self.filepath.get()
        
        existing_proxies = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            existing_proxies.append({
                "name": values[0],
                "type": values[1],
                "lp": values[2],
                "rp": values[3]
            })
            
        existing_proxies.append({
            "name": name,
            "type": self.type_v.get(),
            "lp": lp,
            "rp": rp
        })
        
        new_content = f'serverAddr = "{s_host}"\nserverPort = {s_port}\n'
        for p in existing_proxies:
            new_content += f'\n[[proxies]]\nname = "{p["name"]}"\ntype = "{p["type"]}"\nlocalIP = "127.0.0.1"\nlocalPort = {p["lp"]}\nremotePort = {p["rp"]}\n'
            
        with open(toml_file, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        self.name_v.set(""); self.lp_v.set(""); self.load_existing_proxies()

    def delete_proxy(self):
        sel = self.tree.selection()
        if not sel: return
        target_name = self.tree.item(sel[0])['values'][0]
        if not messagebox.askyesno("?", f"Delete {target_name}?"): return
        
        full_addr = self.server_addr.get().strip()
        if ":" in full_addr:
            s_host, s_port = full_addr.split(":", 1)
            if not s_port.isdigit(): s_port = "7000"
        else:
            s_host, s_port = full_addr, "7000"
            
        toml_file = self.filepath.get()
        
        new_content = f'serverAddr = "{s_host}"\nserverPort = {s_port}\n'
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if str(values[0]) == str(target_name):
                continue
            new_content += f'\n[[proxies]]\nname = "{values[0]}"\ntype = "{values[1]}"\nlocalIP = "127.0.0.1"\nlocalPort = {values[2]}\nremotePort = {values[3]}\n'
            
        with open(toml_file, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        self.load_existing_proxies()

    def start_frpc(self):
        c_flags = 0x08000000 if os.name == 'nt' else 0
        try:
            self.frpc_process = subprocess.Popen([self.frpc_exe.get(), "-c", self.filepath.get()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, creationflags=c_flags)
            self.btn_start.config(state="disabled", bg="#9E9E9E"); self.btn_stop.config(state="normal", bg="#f44336")
            threading.Thread(target=self.stream_logs, daemon=True).start()
        except Exception as e: messagebox.showerror("Error", str(e))

    def stream_logs(self):
        for line in iter(self.frpc_process.stdout.readline, ''): self.root.after(0, self.update_log, line)
        self.root.after(0, self.on_frpc_exit)

    def update_log(self, text):
        self.log_area.config(state="normal"); self.log_area.insert("end", text); self.log_area.see("end"); self.log_area.config(state="disabled")

    def create_tray_image(self):
        if Image is None:
            return None
        try:
            if os.path.exists(TRAY_ICON_FILE):
                return Image.open(TRAY_ICON_FILE)
        except Exception as e:
            print(f"Tray icon load failed: {e}")

        image = Image.new('RGB', (64, 64), color='#2196F3')
        draw = ImageDraw.Draw(image)
        draw.rectangle((14, 10, 50, 22), fill='white')
        draw.rectangle((14, 22, 26, 54), fill='white')
        draw.rectangle((14, 38, 46, 50), fill='white')
        return image

    def setup_tray_icon(self):
        if pystray is None or Image is None:
            return
        menu = pystray.Menu(
            pystray.MenuItem('Restore', self.on_tray_restore),
            pystray.MenuItem('Exit', self.on_tray_exit)
        )
        self.tray_icon = pystray.Icon('FRP GUI', icon=self.create_tray_image(), title='FRP GUI', menu=menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(0, lambda: self.root.attributes('-topmost', False))
        except Exception:
            pass

    def on_tray_restore(self, icon, item):
        self.root.after(0, self.show_window)

    def cleanup_and_exit(self):
        if self.frpc_process:
            self.frpc_process.terminate()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()

    def on_tray_exit(self, icon, item):
        self.root.after(0, self.cleanup_and_exit)

    def on_closing(self):
        if self.tray_icon:
            self.root.withdraw()
            return
        self.root.iconify()

    def stop_frpc(self):
        if self.frpc_process: self.frpc_process.terminate()

    def on_frpc_exit(self):
        self.btn_start.config(state="normal", bg="#2196F3"); self.btn_stop.config(state="disabled", bg="#9E9E9E"); self.frpc_process = None

if __name__ == "__main__":
    root = tk.Tk()
    app = FrpcUltimateGUI(root)
    root.mainloop()
