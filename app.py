import os
import re
import sys
import shutil
import zipfile
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "HTML to APK Offline Converter"
ROOT = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "android-template")
VERSIONS = {
    "Android 4.0 (API 14)": 14, "Android 4.1 (API 16)": 16,
    "Android 4.4 (API 19)": 19, "Android 5.0 (API 21)": 21,
    "Android 6.0 (API 23)": 23, "Android 7.0 (API 24)": 24,
    "Android 8.0 (API 26)": 26, "Android 9.0 (API 28)": 28,
    "Android 10 (API 29)": 29, "Android 11 (API 30)": 30,
    "Android 12 (API 31)": 31, "Android 13 (API 33)": 33,
    "Android 14 (API 34)": 34, "Android 15 (API 35)": 35,
}

def safe_extract(zip_path, destination):
    root = os.path.realpath(destination)
    with zipfile.ZipFile(zip_path, "r") as zf:
        for item in zf.infolist():
            target = os.path.realpath(os.path.join(destination, item.filename))
            if target != root and not target.startswith(root + os.sep):
                raise ValueError("ZIP contains an unsafe path: " + item.filename)
        zf.extractall(destination)

def find_html(folder):
    preferred = ["index.html", "index.htm", "main.html", "main.htm"]
    files = []
    for base, dirs, names in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for name in names:
            if name.lower().endswith((".html", ".htm")):
                full = os.path.join(base, name)
                rel = os.path.relpath(full, folder)
                files.append(rel)
    if not files:
        raise ValueError("No .html or .htm file found.")
    files.sort(key=lambda p: (os.path.basename(p).lower() not in preferred, p.lower()))
    return files[0]

def package_name_valid(value):
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*){1,}$", value))

class Converter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x610")
        self.minsize(680, 560)
        self.configure(padx=18, pady=16)
        self.source = tk.StringVar()
        self.app_name = tk.StringVar(value="My HTML App")
        self.package_id = tk.StringVar(value="com.example.htmlapp")
        self.version = tk.StringVar(value="Android 4.0 (API 14)")
        self.output = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "HTML-to-APK-Projects"))
        self.entry = tk.StringVar()
        self.status = tk.StringVar(value="Ready. Select an HTML file, website folder, or ZIP.")
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="HTML to APK", font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(self, text="Offline website packager • Windows desktop", foreground="#64748b").pack(anchor="w", pady=(0, 14))
        src = ttk.LabelFrame(self, text="1. Website source", padding=12)
        src.pack(fill="x", pady=6)
        ttk.Entry(src, textvariable=self.source).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(src, text="HTML file", command=self.pick_html).pack(side="left", padx=3)
        ttk.Button(src, text="Folder", command=self.pick_folder).pack(side="left", padx=3)
        ttk.Button(src, text="ZIP", command=self.pick_zip).pack(side="left", padx=3)
        meta = ttk.LabelFrame(self, text="2. Android application settings", padding=12)
        meta.pack(fill="x", pady=6)
        self._field(meta, "Application name", self.app_name)
        self._field(meta, "Package ID", self.package_id)
        row = ttk.Frame(meta); row.pack(fill="x", pady=5)
        ttk.Label(row, text="Minimum Android", width=20).pack(side="left")
        ttk.Combobox(row, textvariable=self.version, values=list(VERSIONS.keys()), state="readonly").pack(side="left", fill="x", expand=True)
        out = ttk.LabelFrame(self, text="3. Output", padding=12)
        out.pack(fill="x", pady=6)
        ttk.Entry(out, textvariable=self.output).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(out, text="Browse", command=self.pick_output).pack(side="left")
        actions = ttk.Frame(self); actions.pack(fill="x", pady=12)
        self.create_btn = ttk.Button(actions, text="Create Android project", command=self.create_project)
        self.create_btn.pack(side="left")
        self.build_btn = ttk.Button(actions, text="Build APK", command=self.build_apk)
        self.build_btn.pack(side="left", padx=8)
        ttk.Button(actions, text="Open output folder", command=self.open_output).pack(side="right")
        logbox = ttk.LabelFrame(self, text="Status", padding=10); logbox.pack(fill="both", expand=True)
        ttk.Label(logbox, textvariable=self.status, wraplength=690, justify="left").pack(anchor="w")
        ttk.Label(logbox, text="Note: APK compilation needs JDK 17, Android SDK Platform 35 and Gradle 8.7. The converter UI and website packaging work offline.", foreground="#64748b", wraplength=690).pack(anchor="w", pady=(12, 0))

    def _field(self, parent, label, variable):
        row = ttk.Frame(parent); row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, width=20).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)

    def pick_html(self):
        p = filedialog.askopenfilename(filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")])
        if p: self.source.set(p)

    def pick_folder(self):
        p = filedialog.askdirectory()
        if p: self.source.set(p)

    def pick_zip(self):
        p = filedialog.askopenfilename(filetypes=[("ZIP archives", "*.zip")])
        if p: self.source.set(p)

    def pick_output(self):
        p = filedialog.askdirectory()
        if p: self.output.set(p)

    def open_output(self):
        p = self.output.get()
        os.makedirs(p, exist_ok=True)
        if sys.platform == "win32": os.startfile(p)
        elif sys.platform == "darwin": subprocess.Popen(["open", p])
        else: subprocess.Popen(["xdg-open", p])

    def create_project(self):
        source = self.source.get().strip()
        name = self.app_name.get().strip()
        package_id = self.package_id.get().strip()
        output = self.output.get().strip()
        if not source or not os.path.exists(source):
            messagebox.showerror("Missing source", "Choose an HTML file, folder, or ZIP archive."); return
        if not name or not package_name_valid(package_id):
            messagebox.showerror("Invalid settings", "Enter an app name and package ID like com.example.myapp."); return
        if not os.path.isdir(TEMPLATE):
            messagebox.showerror("Template missing", "The android-template folder is missing. Re-download the complete project."); return
        try:
            os.makedirs(output, exist_ok=True)
            safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-") or "HtmlApp"
            project = os.path.join(output, safe_name)
            if os.path.exists(project):
                project = project + "-project"
            shutil.copytree(TEMPLATE, project)
            site = os.path.join(project, "app", "src", "main", "assets", "site")
            os.makedirs(site, exist_ok=True)
            if os.path.isfile(source) and source.lower().endswith(".zip"):
                safe_extract(source, site)
            elif os.path.isdir(source):
                shutil.copytree(source, site, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            elif os.path.isfile(source) and source.lower().endswith((".html", ".htm")):
                shutil.copytree(os.path.dirname(source), site, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
            else:
                raise ValueError("Source must be an HTML file, a website folder, or a ZIP file.")
            entry = find_html(site)
            self._replace(os.path.join(project, "app", "build.gradle"), {
                "%%APP_ID%%": package_id, "%%MIN_SDK%%": str(VERSIONS[self.version.get()])
            })
            self._replace(os.path.join(project, "app", "src", "main", "res", "values", "strings.xml"), {
                "%%APP_NAME%%": self._xml_escape(name)
            })
            self._replace(os.path.join(project, "app", "src", "main", "java", "com", "example", "htmlapp", "MainActivity.java"), {
                "%%ENTRY_FILE%%": entry.replace("\\", "/").replace('"', "")
            })
            self.entry.set(project)
            self.status.set("Project created: " + project + "\nStart page: " + entry + "\nThe website files are bundled locally in the APK.")
            messagebox.showinfo("Project created", "Android project created successfully.\n\n" + project + "\n\nYou can now press Build APK if Gradle and Android SDK are installed.")
        except Exception as exc:
            messagebox.showerror("Creation failed", str(exc))
            self.status.set("Error: " + str(exc))

    def _replace(self, path, replacements):
        with open(path, "r", encoding="utf-8") as f: data = f.read()
        for old, new in replacements.items(): data = data.replace(old, new)
        with open(path, "w", encoding="utf-8") as f: f.write(data)

    def _xml_escape(self, text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "\\'")

    def build_apk(self):
        project = self.entry.get().strip()
        if not project or not os.path.isdir(project):
            messagebox.showwarning("No project", "Create an Android project first."); return
        gradle = shutil.which("gradle")
        if not gradle:
            messagebox.showerror("Gradle not found", "Install Gradle 8.7 and add it to PATH. Also install JDK 17 and Android SDK Platform 35.")
            return
        self.build_btn.configure(state="disabled")
        self.status.set("Building APK... This can take several minutes.")
        def worker():
            try:
                cmd = [gradle, "assembleDebug", "--no-daemon"]
                proc = subprocess.run(cmd, cwd=project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                apk = os.path.join(project, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
                if proc.returncode == 0 and os.path.isfile(apk):
                    self.after(0, lambda: self.status.set("Build successful!\nAPK: " + apk))
                    self.after(0, lambda: messagebox.showinfo("APK ready", "APK created:\n" + apk))
                else:
                    tail = (proc.stdout or "")[-3500:]
                    self.after(0, lambda: self.status.set("Build failed:\n" + tail))
                    self.after(0, lambda: messagebox.showerror("Build failed", tail))
            except Exception as exc:
                self.after(0, lambda: self.status.set("Build error: " + str(exc)))
            finally:
                self.after(0, lambda: self.build_btn.configure(state="normal"))
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    Converter().mainloop()
