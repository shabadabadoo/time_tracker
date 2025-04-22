import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, colorchooser, ttk
import json
import csv
import os
import time
import threading
from datetime import datetime
from collections import defaultdict

SAVE_FILE = "tracker_data.json"
AUTO_SAVE_INTERVAL = 60  # seconds (15 minutes)
TICK_INTERVAL = 1  # seconds

DEFAULT_COLORS = ["#FF5733", "#33C1FF", "#75FF33", "#F3FF33", "#FF33A8"]
used_colors = set()

class Project:
    def __init__(self, name, color=None, time_data=None, sessions=None):
        self.name = name
        self.color = color or self._assign_color()
        self.total_seconds = time_data or 0
        self.is_active = False
        self.last_start_time = None
        self.sessions = sessions or []  # Each session: (start_ts, stop_ts)

    def _assign_color(self):
        for color in DEFAULT_COLORS:
            if color not in used_colors:
                used_colors.add(color)
                return color
        return "#AAAAAA"

    def start(self):
        if not self.is_active:
            self.last_start_time = time.time()
            self.is_active = True
            self.sessions.append([datetime.now().isoformat(), None])

    def stop(self):
        if self.is_active:
            elapsed = int(time.time() - self.last_start_time)
            self.total_seconds += elapsed
            self.is_active = False
            self.sessions[-1][1] = datetime.now().isoformat()
            self.last_start_time = None

    def tick(self):
        if self.is_active:
            return int(time.time() - self.last_start_time)
        return 0

    def total_minutes(self):
        return (self.total_seconds + self.tick()) // 60

# Update TrackerApp
class TrackerApp:
    def __init__(self, root):
        self.root = root
        self.projects = {}
        self.active_project = None
        self.project_frames = {}
        self.load_data()

        self.root.title("Time Tracker")
        self.ui_frame = tk.Frame(root)
        self.ui_frame.pack()

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        tk.Button(self.control_frame, text="➕ Add Project", command=self.add_project).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="⬇ Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="⬆ Import CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5)

        self.table_frame = tk.Frame(root)
        self.table_frame.pack(pady=10)

        self.render_projects()
        self.build_session_table()
        self.update_ui()
        self.auto_save()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def render_projects(self):
        for widget in self.ui_frame.winfo_children():
            widget.destroy()

        for name, project in self.projects.items():
            self._render_project(project)
            
    def update_project_styles(self):
        for name, (frame, _, _) in self.project_frames.items():
            project = self.projects[name]
            if project.is_active:
                frame.config(highlightbackground="black", highlightthickness=3)
            else:
                frame.config(highlightthickness=0)

    def _render_project(self, project):
        outer_frame = tk.Frame(self.ui_frame, bg="#000000", padx=2, pady=2)
        outer_frame.pack(pady=5, fill="x")
        
        frame = tk.Frame(outer_frame, bd=2, relief=tk.RAISED, padx=20, pady=20,
                         bg=project.color, height=60)
        frame.pack(fill="x")
        
        # Bind clicks
        frame.bind("<Button-1>", lambda e, p=project: self.toggle_timer(p))
        
        name_label = tk.Label(frame, text=project.name, bg=project.color, font=("Arial", 14, "bold"))
        name_label.pack(side=tk.LEFT)
        
        time_label = tk.Label(frame, text="0:00", bg=project.color, font=("Arial", 12))
        time_label.pack(side=tk.LEFT, padx=15)
        
        edit_btn = tk.Button(frame, text="✎", command=lambda p=project: self.rename_project(p))
        edit_btn.pack(side=tk.RIGHT, padx=2)
        
        color_btn = tk.Button(frame, text="🎨", command=lambda p=project: self.change_color(p))
        color_btn.pack(side=tk.RIGHT, padx=2)
        
        del_btn = tk.Button(frame, text="🗑", command=lambda p=project: self.remove_project(p))
        del_btn.pack(side=tk.RIGHT, padx=2)
        
        # Now that everything is initialized, store it properly
        self.project_frames[project.name] = (frame, time_label, outer_frame)


    def toggle_timer(self, project):
        if self.active_project and self.active_project != project:
            self.active_project.stop()
        if project.is_active:
            project.stop()
            self.active_project = None
        else:
            project.start()
            self.active_project = project
        self.update_project_styles() #self.render_projects()
        self.update_session_table()

    def update_ui(self):
        for name, (frame, time_label, outer_frame) in self.project_frames.items():
            project = self.projects.get(name)
            if not project:
                continue
            total = project.total_seconds + project.tick()
            mins, secs = divmod(total, 60)
            if time_label:  # Defensive check
                time_label.config(text=f"{mins}:{secs:02d}")
        
        # Only update styles when a timer is toggled
        # self.update_project_styles()

        self.root.after(TICK_INTERVAL * 1000, self.update_ui)


    def update_session_table(self):
        for row in self.session_table.get_children():
            self.session_table.delete(row)

        rows = []
        for name, proj in self.projects.items():
            for start, stop in reversed(proj.sessions[-3:]):
                rows.append((name, start or "-", stop or "-"))

        for row in sorted(rows, key=lambda r: r[1], reverse=True)[:10]:
            self.session_table.insert("", "end", values=row)

    def build_session_table(self):
        headers = ["Project", "Start Time", "Stop Time"]
        self.session_table = ttk.Treeview(self.table_frame, columns=headers, show="headings")
        for h in headers:
            self.session_table.heading(h, text=h)
            self.session_table.column(h, width=160)
        self.session_table.pack()

    def add_project(self):
        name = simpledialog.askstring("New Project", "Enter project name:")
        if not name or name in self.projects:
            return
        new_project = Project(name)
        self.projects[name] = new_project
        self._render_project(new_project)
        #self.render_projects()

    def rename_project(self, project):
        new_name = simpledialog.askstring("Rename Project", "New name:", initialvalue=project.name)
        if new_name and new_name not in self.projects:
            self.projects[new_name] = self.projects.pop(project.name)
            self.projects[new_name].name = new_name
            self.render_projects()

    def remove_project(self, project):
        project.stop()
        if project.total_minutes() < 10:
            del self.projects[project.name]
        else:
            if messagebox.askyesno("Confirm Delete", f"Remove project '{project.name}'?"):
                del self.projects[project.name]
        self.render_projects()
        self.update_session_table()

    def change_color(self, project):
        color = colorchooser.askcolor(title="Pick a Color")[1]
        if color:
            project.color = color
            self.render_projects()

    def save_data(self):
        data = {
            name: {
                "color": proj.color,
                "time_data": proj.total_seconds,
                "sessions": proj.sessions
            } for name, proj in self.projects.items()
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                for name, details in data.items():
                    self.projects[name] = Project(name, details["color"], details["time_data"], details.get("sessions", []))

    def auto_save(self):
        self.save_data()
        self.root.after(AUTO_SAVE_INTERVAL * 1000, self.auto_save)

    def on_close(self):
        if self.active_project:
            self.active_project.stop()
        self.save_data()
        self.root.destroy()

    def export_csv(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv")
        if not file:
            return
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Project", "Total Minutes", "Color", "Start Time", "Stop Time"])
            for name, proj in self.projects.items():
                for start, stop in proj.sessions:
                    writer.writerow([name, proj.total_minutes(), proj.color, start, stop])

    def import_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file:
            return
        with open(file, newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            idx_map = {col: i for i, col in enumerate(header)}
            self.projects = {}
            for row in reader:
                name = row[idx_map["Project"]]
                color = row[idx_map["Color"]]
                start = row[idx_map.get("Start Time")]
                stop = row[idx_map.get("Stop Time")]
                minutes = int(row[idx_map["Total Minutes"]])
                if name not in self.projects:
                    self.projects[name] = Project(name, color, 0, [])
                self.projects[name].total_seconds += minutes * 60
                self.projects[name].sessions.append([start, stop])
        self.render_projects()
        self.update_session_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrackerApp(root)
    root.mainloop()
