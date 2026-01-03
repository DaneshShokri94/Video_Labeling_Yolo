"""
AnnotateX - Professional Video Annotation Suite
A modern, minimal design for efficient dataset creation
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import copy


class Colors:
    """Modern minimal color palette"""
    # Backgrounds
    BG_PRIMARY = "#0D0D0D"
    BG_SECONDARY = "#161616"
    BG_TERTIARY = "#1E1E1E"
    BG_ELEVATED = "#262626"
    BG_HOVER = "#2D2D2D"
    
    # Borders
    BORDER = "#333333"
    BORDER_LIGHT = "#404040"
    
    # Text
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B3B3B3"
    TEXT_TERTIARY = "#737373"
    TEXT_DISABLED = "#525252"
    
    # Accents
    ACCENT_BLUE = "#3B82F6"
    ACCENT_BLUE_HOVER = "#60A5FA"
    ACCENT_GREEN = "#22C55E"
    ACCENT_YELLOW = "#EAB308"
    ACCENT_RED = "#EF4444"
    ACCENT_PURPLE = "#A855F7"
    
    # Semantic
    SUCCESS = "#22C55E"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#3B82F6"


class Icons:
    """Unicode icons for UI"""
    FOLDER = "📁"
    SAVE = "💾"
    PLAY = "▶"
    PAUSE = "⏸"
    PREV = "◂"
    NEXT = "▸"
    FIRST = "⏮"
    LAST = "⏭"
    SKIP_BACK = "⏪"
    SKIP_FWD = "⏩"
    ZOOM_IN = "+"
    ZOOM_OUT = "−"
    RESET = "⟲"
    DELETE = "✕"
    UNDO = "↶"
    COPY = "⧉"
    CLEAR = "⌧"
    HELP = "?"
    SETTINGS = "⚙"
    CHECK = "✓"
    SEARCH = "⌕"


class AnnotateX:
    def __init__(self, root):
        self.root = root
        self.root.title("AnnotateX")
        self.root.geometry("1500x900")
        self.root.minsize(1200, 700)
        self.root.configure(bg=Colors.BG_PRIMARY)
        
        # Remove window decorations for custom title bar (optional)
        # self.root.overrideredirect(True)
        
        self.init_variables()
        self.create_ui()
        self.bind_events()
        
    def init_variables(self):
        """Initialize all application variables"""
        # Video state
        self.video_path = None
        self.cap = None
        self.current_frame = None
        self.frame_number = 0
        self.total_frames = 0
        self.fps = 30
        self.playing = False
        
        # Display
        self.scale_factor = 1.0
        self.zoom_level = 1.0
        self.pan_offset = [0, 0]
        
        # Annotations
        self.annotations = {}
        self.selected_idx = None
        self.is_drawing = False
        self.is_editing = False
        self.edit_mode = None
        self.drag_start = None
        self.temp_box = None
        
        # Classes
        self.classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
        self.custom_classes = []
        self.current_class = tk.StringVar(value="")
        
        # Class colors (vibrant palette)
        self.class_colors = {}
        palette = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD",
            "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9", "#F8B500", "#FF4757",
            "#2ED573", "#1E90FF", "#FF6348", "#7BED9F", "#70A1FF", "#FFA502",
            "#FF4757", "#2F3542", "#57606F", "#747D8C", "#A4B0BD", "#DFE4EA"
        ]
        for i, cls in enumerate(self.classes):
            self.class_colors[cls] = palette[i % len(palette)]
        
        # UI state
        self.show_labels = tk.BooleanVar(value=True)
        self.show_boxes = tk.BooleanVar(value=True)
        self.export_format = tk.StringVar(value="YOLO")
        self.search_var = tk.StringVar()
        
        # Output
        self.output_dir = None

    def create_ui(self):
        """Build the complete UI"""
        # Main container
        self.main = tk.Frame(self.root, bg=Colors.BG_PRIMARY)
        self.main.pack(fill=tk.BOTH, expand=True)
        
        # Create sections
        self.create_header()
        self.create_body()
        self.create_footer()
    
    def create_header(self):
        """Create minimal header bar"""
        header = tk.Frame(self.main, bg=Colors.BG_SECONDARY, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Left: Logo/Title
        left = tk.Frame(header, bg=Colors.BG_SECONDARY)
        left.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(left, text="AnnotateX", 
                font=("SF Pro Display", 16, "bold"),
                fg=Colors.TEXT_PRIMARY, bg=Colors.BG_SECONDARY).pack(side=tk.LEFT)
        
        tk.Label(left, text="  Pro", 
                font=("SF Pro Display", 10),
                fg=Colors.ACCENT_BLUE, bg=Colors.BG_SECONDARY).pack(side=tk.LEFT, pady=(4, 0))
        
        # Center: File info
        center = tk.Frame(header, bg=Colors.BG_SECONDARY)
        center.pack(side=tk.LEFT, expand=True)
        
        self.file_label = tk.Label(center, text="No file loaded",
                                   font=("SF Pro Text", 10),
                                   fg=Colors.TEXT_TERTIARY, bg=Colors.BG_SECONDARY)
        self.file_label.pack()
        
        # Right: Main actions
        right = tk.Frame(header, bg=Colors.BG_SECONDARY)
        right.pack(side=tk.RIGHT, padx=20)
        
        self.create_header_button(right, "Open", self.load_video, primary=False)
        self.create_header_button(right, "Save", self.save_project, primary=True)
        self.create_icon_button(right, "?", self.show_help, size=28)
    
    def create_header_button(self, parent, text, command, primary=False):
        """Create header action button"""
        bg = Colors.ACCENT_BLUE if primary else Colors.BG_ELEVATED
        hover = Colors.ACCENT_BLUE_HOVER if primary else Colors.BG_HOVER
        
        btn = tk.Label(parent, text=text,
                      font=("SF Pro Text", 10, "bold" if primary else "normal"),
                      fg=Colors.TEXT_PRIMARY, bg=bg,
                      padx=16, pady=6, cursor="hand2")
        btn.pack(side=tk.LEFT, padx=4)
        
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        btn.bind("<Button-1>", lambda e: command())
        
        return btn
    
    def create_icon_button(self, parent, icon, command, size=32, tooltip=None):
        """Create circular icon button"""
        btn = tk.Label(parent, text=icon,
                      font=("SF Pro Text", 11),
                      fg=Colors.TEXT_SECONDARY, bg=Colors.BG_ELEVATED,
                      width=2, height=1, cursor="hand2")
        btn.pack(side=tk.LEFT, padx=4)
        
        btn.bind("<Enter>", lambda e: btn.configure(bg=Colors.BG_HOVER, fg=Colors.TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(bg=Colors.BG_ELEVATED, fg=Colors.TEXT_SECONDARY))
        btn.bind("<Button-1>", lambda e: command())
        
        return btn
    
    def create_body(self):
        """Create main body with sidebar and canvas"""
        body = tk.Frame(self.main, bg=Colors.BG_PRIMARY)
        body.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Left Panel
        self.create_left_panel(body)
        
        # Center: Canvas area
        self.create_canvas_area(body)
        
        # Right Panel
        self.create_right_panel(body)
    
    def create_left_panel(self, parent):
        """Create left sidebar for class selection"""
        panel = tk.Frame(parent, bg=Colors.BG_SECONDARY, width=260)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        panel.pack_propagate(False)
        
        # Padding container
        inner = tk.Frame(panel, bg=Colors.BG_SECONDARY)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Section: Classes
        self.create_section_header(inner, "CLASSES")
        
        # Search
        search_frame = tk.Frame(inner, bg=Colors.BG_TERTIARY, highlightthickness=1,
                               highlightbackground=Colors.BORDER)
        search_frame.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(search_frame, text=Icons.SEARCH, font=("", 10),
                fg=Colors.TEXT_TERTIARY, bg=Colors.BG_TERTIARY).pack(side=tk.LEFT, padx=(10, 5))
        
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                    font=("SF Pro Text", 10),
                                    fg=Colors.TEXT_PRIMARY, bg=Colors.BG_TERTIARY,
                                    insertbackground=Colors.TEXT_PRIMARY,
                                    relief=tk.FLAT, bd=0)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8, padx=(0, 10))
        self.search_entry.insert(0, "Search...")
        self.search_entry.bind("<FocusIn>", self.on_search_focus)
        self.search_entry.bind("<FocusOut>", self.on_search_blur)
        self.search_var.trace("w", self.filter_classes)
        
        # Class list container
        list_frame = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Scrollable class list
        self.class_canvas = tk.Canvas(list_frame, bg=Colors.BG_SECONDARY,
                                      highlightthickness=0, width=220)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                command=self.class_canvas.yview,
                                bg=Colors.BG_TERTIARY, troughcolor=Colors.BG_SECONDARY,
                                width=8)
        
        self.class_list_frame = tk.Frame(self.class_canvas, bg=Colors.BG_SECONDARY)
        
        self.class_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.class_canvas.configure(yscrollcommand=scrollbar.set)
        self.class_canvas_window = self.class_canvas.create_window(
            (0, 0), window=self.class_list_frame, anchor=tk.NW)
        
        self.class_list_frame.bind("<Configure>", self.on_class_list_configure)
        self.class_canvas.bind("<Configure>", self.on_class_canvas_configure)
        
        # Populate class list
        self.populate_class_list()
        
        # Current selection display
        self.selection_frame = tk.Frame(inner, bg=Colors.BG_TERTIARY)
        self.selection_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.selection_color = tk.Canvas(self.selection_frame, width=4, height=40,
                                        bg=Colors.BG_TERTIARY, highlightthickness=0)
        self.selection_color.pack(side=tk.LEFT)
        
        self.selection_label = tk.Label(self.selection_frame, text="No class selected",
                                       font=("SF Pro Text", 11),
                                       fg=Colors.TEXT_SECONDARY, bg=Colors.BG_TERTIARY,
                                       anchor=tk.W, padx=12, pady=10)
        self.selection_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add custom class
        self.create_section_header(inner, "ADD CUSTOM")
        
        custom_frame = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        custom_frame.pack(fill=tk.X)
        
        self.custom_entry = tk.Entry(custom_frame, font=("SF Pro Text", 10),
                                    fg=Colors.TEXT_PRIMARY, bg=Colors.BG_TERTIARY,
                                    insertbackground=Colors.TEXT_PRIMARY,
                                    relief=tk.FLAT, bd=8)
        self.custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        add_btn = tk.Label(custom_frame, text="+", font=("SF Pro Text", 14),
                          fg=Colors.TEXT_PRIMARY, bg=Colors.ACCENT_BLUE,
                          width=3, height=1, cursor="hand2")
        add_btn.pack(side=tk.RIGHT, padx=(8, 0))
        add_btn.bind("<Button-1>", lambda e: self.add_custom_class())
    
    def create_section_header(self, parent, text):
        """Create section header"""
        frame = tk.Frame(parent, bg=Colors.BG_SECONDARY)
        frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(frame, text=text, font=("SF Pro Text", 9, "bold"),
                fg=Colors.TEXT_TERTIARY, bg=Colors.BG_SECONDARY).pack(side=tk.LEFT)
        
        # Separator line
        sep = tk.Frame(frame, bg=Colors.BORDER, height=1)
        sep.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 0), pady=6)
    
    def populate_class_list(self, filter_text=""):
        """Populate the class list"""
        # Clear existing
        for widget in self.class_list_frame.winfo_children():
            widget.destroy()
        
        # Filter classes
        all_classes = self.classes + self.custom_classes
        if filter_text and filter_text != "Search...":
            all_classes = [c for c in all_classes if filter_text.lower() in c.lower()]
        
        # Create class items
        for cls in all_classes:
            self.create_class_item(cls)
    
    def create_class_item(self, class_name):
        """Create a class list item"""
        color = self.get_class_color(class_name)
        
        item = tk.Frame(self.class_list_frame, bg=Colors.BG_SECONDARY, cursor="hand2")
        item.pack(fill=tk.X, pady=1)
        
        # Color indicator
        indicator = tk.Canvas(item, width=3, height=28, bg=color, highlightthickness=0)
        indicator.pack(side=tk.LEFT)
        
        # Label
        label = tk.Label(item, text=class_name.capitalize(),
                        font=("SF Pro Text", 10),
                        fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY,
                        anchor=tk.W, padx=10, pady=6)
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Hover effects
        def on_enter(e):
            item.configure(bg=Colors.BG_TERTIARY)
            label.configure(bg=Colors.BG_TERTIARY, fg=Colors.TEXT_PRIMARY)
        
        def on_leave(e):
            item.configure(bg=Colors.BG_SECONDARY)
            label.configure(bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY)
        
        def on_click(e):
            self.select_class(class_name)
        
        for widget in [item, label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
    
    def on_class_list_configure(self, event):
        self.class_canvas.configure(scrollregion=self.class_canvas.bbox("all"))
    
    def on_class_canvas_configure(self, event):
        self.class_canvas.itemconfig(self.class_canvas_window, width=event.width)
    
    def select_class(self, class_name):
        """Select a class"""
        self.current_class.set(class_name)
        color = self.get_class_color(class_name)
        
        self.selection_color.configure(bg=color)
        self.selection_label.configure(text=class_name.capitalize(), fg=Colors.TEXT_PRIMARY)
        
        self.update_status(f"Selected: {class_name}")
    
    def get_class_color(self, class_name):
        """Get color for class"""
        if class_name in self.class_colors:
            return self.class_colors[class_name]
        
        # Generate color for custom class
        hash_val = hash(class_name) % 360
        return f"#{hash_val % 256:02x}{(hash_val * 2) % 256:02x}{(hash_val * 3) % 256:02x}"
    
    def on_search_focus(self, event):
        if self.search_entry.get() == "Search...":
            self.search_entry.delete(0, tk.END)
    
    def on_search_blur(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search...")
    
    def filter_classes(self, *args):
        self.populate_class_list(self.search_var.get())
    
    def add_custom_class(self):
        """Add a custom class"""
        name = self.custom_entry.get().strip().lower()
        if not name:
            return
        
        if name in self.classes or name in self.custom_classes:
            self.update_status(f"Class '{name}' already exists", error=True)
            return
        
        self.custom_classes.append(name)
        self.populate_class_list()
        self.custom_entry.delete(0, tk.END)
        self.select_class(name)
        self.update_status(f"Added: {name}")
    
    def create_canvas_area(self, parent):
        """Create central canvas area"""
        center = tk.Frame(parent, bg=Colors.BG_PRIMARY)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Toolbar
        self.create_toolbar(center)
        
        # Canvas container
        canvas_container = tk.Frame(center, bg=Colors.BG_PRIMARY)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # Canvas with border
        canvas_border = tk.Frame(canvas_container, bg=Colors.BORDER)
        canvas_border.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_border, bg="#000000",
                               highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Canvas bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        self.canvas.bind("<Button-4>", self.on_canvas_scroll)
        self.canvas.bind("<Button-5>", self.on_canvas_scroll)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # Timeline
        self.create_timeline(center)
        
        # Show welcome
        self.root.after(100, self.show_welcome)
    
    def create_toolbar(self, parent):
        """Create toolbar above canvas"""
        toolbar = tk.Frame(parent, bg=Colors.BG_SECONDARY, height=44)
        toolbar.pack(fill=tk.X, padx=8, pady=(8, 0))
        toolbar.pack_propagate(False)
        
        inner = tk.Frame(toolbar, bg=Colors.BG_SECONDARY)
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        
        # Left: Navigation
        nav = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        nav.pack(side=tk.LEFT)
        
        nav_buttons = [
            (Icons.FIRST, self.go_first, "First frame"),
            (Icons.SKIP_BACK, self.skip_back, "Back 10"),
            (Icons.PREV, self.prev_frame, "Previous"),
            (Icons.NEXT, self.next_frame, "Next"),
            (Icons.SKIP_FWD, self.skip_forward, "Forward 10"),
            (Icons.LAST, self.go_last, "Last frame"),
        ]
        
        for icon, cmd, tip in nav_buttons:
            self.create_toolbar_button(nav, icon, cmd)
        
        # Separator
        self.create_toolbar_separator(inner)
        
        # Frame info
        info = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        info.pack(side=tk.LEFT, padx=8)
        
        self.frame_label = tk.Label(info, text="Frame: -- / --",
                                   font=("SF Mono", 10),
                                   fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY)
        self.frame_label.pack(side=tk.LEFT)
        
        # Jump input
        tk.Label(info, text="  Go to:",
                font=("SF Pro Text", 9),
                fg=Colors.TEXT_TERTIARY, bg=Colors.BG_SECONDARY).pack(side=tk.LEFT, padx=(16, 4))
        
        self.frame_input = tk.Entry(info, width=6, font=("SF Mono", 10),
                                   fg=Colors.TEXT_PRIMARY, bg=Colors.BG_TERTIARY,
                                   insertbackground=Colors.TEXT_PRIMARY,
                                   relief=tk.FLAT, bd=4)
        self.frame_input.pack(side=tk.LEFT)
        self.frame_input.bind("<Return>", lambda e: self.jump_to_frame())
        
        # Separator
        self.create_toolbar_separator(inner)
        
        # Zoom
        zoom = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        zoom.pack(side=tk.LEFT)
        
        self.create_toolbar_button(zoom, Icons.ZOOM_OUT, lambda: self.zoom(-1))
        
        self.zoom_label = tk.Label(zoom, text="100%",
                                  font=("SF Mono", 10), width=5,
                                  fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY)
        self.zoom_label.pack(side=tk.LEFT, padx=4)
        
        self.create_toolbar_button(zoom, Icons.ZOOM_IN, lambda: self.zoom(1))
        self.create_toolbar_button(zoom, Icons.RESET, self.reset_zoom)
        
        # Right: Edit actions
        edit = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        edit.pack(side=tk.RIGHT)
        
        self.create_toolbar_text_button(edit, "Undo", self.undo)
        self.create_toolbar_text_button(edit, "Copy Prev", self.copy_previous)
        self.create_toolbar_text_button(edit, "Clear", self.clear_frame)
        self.create_toolbar_text_button(edit, "Delete", self.delete_selected, danger=True)
    
    def create_toolbar_button(self, parent, icon, command):
        """Create toolbar icon button"""
        btn = tk.Label(parent, text=icon, font=("", 12),
                      fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY,
                      padx=8, pady=4, cursor="hand2")
        btn.pack(side=tk.LEFT)
        
        btn.bind("<Enter>", lambda e: btn.configure(fg=Colors.TEXT_PRIMARY))
        btn.bind("<Leave>", lambda e: btn.configure(fg=Colors.TEXT_SECONDARY))
        btn.bind("<Button-1>", lambda e: command())
        
        return btn
    
    def create_toolbar_text_button(self, parent, text, command, danger=False):
        """Create toolbar text button"""
        fg = Colors.ACCENT_RED if danger else Colors.TEXT_TERTIARY
        fg_hover = Colors.ERROR if danger else Colors.TEXT_PRIMARY
        
        btn = tk.Label(parent, text=text, font=("SF Pro Text", 9),
                      fg=fg, bg=Colors.BG_SECONDARY,
                      padx=10, pady=4, cursor="hand2")
        btn.pack(side=tk.LEFT)
        
        btn.bind("<Enter>", lambda e: btn.configure(fg=fg_hover))
        btn.bind("<Leave>", lambda e: btn.configure(fg=fg))
        btn.bind("<Button-1>", lambda e: command())
        
        return btn
    
    def create_toolbar_separator(self, parent):
        """Create toolbar separator"""
        sep = tk.Frame(parent, bg=Colors.BORDER, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=4)
    
    def create_timeline(self, parent):
        """Create timeline/scrubber"""
        timeline = tk.Frame(parent, bg=Colors.BG_SECONDARY, height=50)
        timeline.pack(fill=tk.X, padx=8, pady=(0, 8))
        timeline.pack_propagate(False)
        
        inner = tk.Frame(timeline, bg=Colors.BG_SECONDARY)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        
        # Time labels
        self.time_current = tk.Label(inner, text="00:00",
                                    font=("SF Mono", 9),
                                    fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY)
        self.time_current.pack(side=tk.LEFT)
        
        # Slider
        slider_frame = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)
        
        self.timeline_canvas = tk.Canvas(slider_frame, bg=Colors.BG_TERTIARY,
                                        height=6, highlightthickness=0, cursor="hand2")
        self.timeline_canvas.pack(fill=tk.X, pady=10)
        
        self.timeline_canvas.bind("<Button-1>", self.on_timeline_click)
        self.timeline_canvas.bind("<B1-Motion>", self.on_timeline_drag)
        
        self.time_total = tk.Label(inner, text="00:00",
                                  font=("SF Mono", 9),
                                  fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY)
        self.time_total.pack(side=tk.RIGHT)
    
    def create_right_panel(self, parent):
        """Create right sidebar"""
        panel = tk.Frame(parent, bg=Colors.BG_SECONDARY, width=240)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(1, 0))
        panel.pack_propagate(False)
        
        inner = tk.Frame(panel, bg=Colors.BG_SECONDARY)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Export settings
        self.create_section_header(inner, "EXPORT")
        
        # Format selector
        format_frame = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        format_frame.pack(fill=tk.X, pady=(0, 16))
        
        formats = ["YOLO", "VOC", "COCO"]
        for fmt in formats:
            self.create_format_option(format_frame, fmt)
        
        # Display options
        self.create_section_header(inner, "DISPLAY")
        
        self.create_toggle(inner, "Show Labels", self.show_labels, self.refresh_display)
        self.create_toggle(inner, "Show Boxes", self.show_boxes, self.refresh_display)
        
        # Statistics
        self.create_section_header(inner, "STATISTICS")
        
        stats_frame = tk.Frame(inner, bg=Colors.BG_SECONDARY)
        stats_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.stats = {
            'total': tk.StringVar(value="0"),
            'frames': tk.StringVar(value="0"),
            'current': tk.StringVar(value="0")
        }
        
        self.create_stat_row(stats_frame, "Total Boxes", self.stats['total'])
        self.create_stat_row(stats_frame, "Annotated Frames", self.stats['frames'])
        self.create_stat_row(stats_frame, "Current Frame", self.stats['current'])
        
        # Shortcuts
        self.create_section_header(inner, "SHORTCUTS")
        
        shortcuts = [
            ("←  →", "Navigate"),
            ("Space", "Next frame"),
            ("Del", "Delete box"),
            ("Ctrl+Z", "Undo"),
            ("Scroll", "Zoom"),
        ]
        
        for key, action in shortcuts:
            self.create_shortcut_row(inner, key, action)
    
    def create_format_option(self, parent, format_name):
        """Create format radio option"""
        is_selected = self.export_format.get() == format_name
        
        btn = tk.Frame(parent, bg=Colors.ACCENT_BLUE if is_selected else Colors.BG_TERTIARY,
                      cursor="hand2")
        btn.pack(side=tk.LEFT, padx=(0, 4))
        
        label = tk.Label(btn, text=format_name,
                        font=("SF Pro Text", 9),
                        fg=Colors.TEXT_PRIMARY,
                        bg=Colors.ACCENT_BLUE if is_selected else Colors.BG_TERTIARY,
                        padx=12, pady=6)
        label.pack()
        
        def on_click(e):
            self.export_format.set(format_name)
            # Refresh all format buttons
            for child in parent.winfo_children():
                child.destroy()
            for fmt in ["YOLO", "VOC", "COCO"]:
                self.create_format_option(parent, fmt)
        
        btn.bind("<Button-1>", on_click)
        label.bind("<Button-1>", on_click)
    
    def create_toggle(self, parent, text, variable, command=None):
        """Create toggle switch"""
        frame = tk.Frame(parent, bg=Colors.BG_SECONDARY)
        frame.pack(fill=tk.X, pady=4)
        
        tk.Label(frame, text=text, font=("SF Pro Text", 10),
                fg=Colors.TEXT_SECONDARY, bg=Colors.BG_SECONDARY).pack(side=tk.LEFT)
        
        # Toggle switch
        toggle_bg = Colors.ACCENT_BLUE if variable.get() else Colors.BG_TERTIARY
        toggle = tk.Canvas(frame, width=36, height=20, bg=Colors.BG_SECONDARY,
                          highlightthickness=0, cursor="hand2")
        toggle.pack(side=tk.RIGHT)
        
        # Draw toggle
        def draw_toggle():
            toggle.delete("all")
            bg = Colors.ACCENT_BLUE if variable.get() else Colors.BG_TERTIARY
            toggle.create_oval(2, 2, 34, 18, fill=bg, outline="")
            
            x = 22 if variable.get() else 10
            toggle.create_oval(x-6, 4, x+6, 16, fill=Colors.TEXT_PRIMARY, outline="")
        
        draw_toggle()
        
        def on_click(e):
            variable.set(not variable.get())
            draw_toggle()
            if command:
                command()
        
        toggle.bind("<Button-1>", on_click)
    
    def create_stat_row(self, parent, label, variable):
        """Create statistics row"""
        row = tk.Frame(parent, bg=Colors.BG_SECONDARY)
        row.pack(fill=tk.X, pady=2)
        
        tk.Label(row, text=label, font=("SF Pro Text", 10),
                fg=Colors.TEXT_TERTIARY, bg=Colors.BG_SECONDARY).pack(side=tk.LEFT)
        
        tk.Label(row, textvariable=variable, font=("SF Mono", 10),
                fg=Colors.TEXT_PRIMARY, bg=Colors.BG_SECONDARY).pack(side=tk.RIGHT)
    
    def create_shortcut_row(self, parent, key, action):
        """Create shortcut row"""
        row = tk.Frame(parent, bg=Colors.BG_SECONDARY)
        row.pack(fill=tk.X, pady=2)
        
        key_label = tk.Label(row, text=key, font=("SF Mono", 8),
                            fg=Colors.TEXT_PRIMARY, bg=Colors.BG_TERTIARY,
                            padx=6, pady=2)
        key_label.pack(side=tk.LEFT)
        
        tk.Label(row, text=action, font=("SF Pro Text", 9),
                fg=Colors.TEXT_TERTIARY, bg=Colors.BG_SECONDARY,
                padx=8).pack(side=tk.LEFT)
    
    def create_footer(self):
        """Create status bar footer"""
        footer = tk.Frame(self.main, bg=Colors.BG_TERTIARY, height=28)
        footer.pack(fill=tk.X)
        footer.pack_propagate(False)
        
        inner = tk.Frame(footer, bg=Colors.BG_TERTIARY)
        inner.pack(fill=tk.BOTH, expand=True, padx=16)
        
        # Status icon
        self.status_icon = tk.Label(inner, text="●", font=("", 8),
                                   fg=Colors.SUCCESS, bg=Colors.BG_TERTIARY)
        self.status_icon.pack(side=tk.LEFT, pady=6)
        
        # Status text
        self.status_label = tk.Label(inner, text="Ready",
                                    font=("SF Pro Text", 9),
                                    fg=Colors.TEXT_SECONDARY, bg=Colors.BG_TERTIARY)
        self.status_label.pack(side=tk.LEFT, padx=(6, 0), pady=6)
        
        # Right: Zoom indicator
        self.status_zoom = tk.Label(inner, text="100%",
                                   font=("SF Mono", 9),
                                   fg=Colors.TEXT_TERTIARY, bg=Colors.BG_TERTIARY)
        self.status_zoom.pack(side=tk.RIGHT, pady=6)
    
    def update_status(self, text, error=False, warning=False):
        """Update status bar"""
        self.status_label.configure(text=text)
        
        if error:
            self.status_icon.configure(fg=Colors.ERROR)
        elif warning:
            self.status_icon.configure(fg=Colors.WARNING)
        else:
            self.status_icon.configure(fg=Colors.SUCCESS)
    
    def show_welcome(self):
        """Show welcome screen on canvas"""
        self.canvas.delete("all")
        
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 500
        
        # Welcome text
        self.canvas.create_text(w//2, h//2 - 30,
                               text="Drop a video file or click Open",
                               font=("SF Pro Display", 16),
                               fill=Colors.TEXT_SECONDARY)
        
        self.canvas.create_text(w//2, h//2 + 10,
                               text="Supported: MP4, AVI, MOV, MKV",
                               font=("SF Pro Text", 11),
                               fill=Colors.TEXT_TERTIARY)
    
    def bind_events(self):
        """Bind keyboard shortcuts"""
        self.root.bind("<Control-o>", lambda e: self.load_video())
        self.root.bind("<Control-s>", lambda e: self.save_project())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-c>", lambda e: self.copy_previous())
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<space>", lambda e: self.next_frame())
        self.root.bind("<Left>", lambda e: self.prev_frame())
        self.root.bind("<Right>", lambda e: self.next_frame())
        self.root.bind("<Home>", lambda e: self.go_first())
        self.root.bind("<End>", lambda e: self.go_last())
        self.root.bind("<Prior>", lambda e: self.skip_back())
        self.root.bind("<Next>", lambda e: self.skip_forward())
        self.root.bind("<Escape>", lambda e: self.deselect())
        self.root.bind("<F1>", lambda e: self.show_help())
        
        for i in range(10):
            self.root.bind(str(i), lambda e, i=i: self.quick_class(i))
    
    # ==================== Video/Frame Operations ====================
    
    def load_video(self):
        """Load video file"""
        path = filedialog.askopenfilename(
            title="Open Video",
            filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv"), ("All", "*.*")]
        )
        
        if not path:
            return
        
        try:
            self.video_path = path
            self.cap = cv2.VideoCapture(path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            
            self.frame_number = 0
            self.annotations = {}
            self.zoom_level = 1.0
            
            self.load_frame()
            
            name = Path(path).name
            self.file_label.configure(text=name, fg=Colors.TEXT_PRIMARY)
            self.update_status(f"Loaded: {name}")
            
            # Update timeline
            total_sec = self.total_frames / self.fps
            self.time_total.configure(text=self.format_time(total_sec))
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def load_frame(self):
        """Load current frame"""
        if not self.cap:
            return
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        ret, frame = self.cap.read()
        
        if ret:
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.display_frame()
            self.update_ui()
    
    def display_frame(self):
        """Display frame on canvas"""
        if self.current_frame is None:
            return
        
        self.canvas.delete("all")
        
        h, w = self.current_frame.shape[:2]
        
        # Calculate scale to fit canvas
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 500
        
        self.scale_factor = min(cw / w, ch / h) * 0.95
        
        # Apply zoom
        display_w = int(w * self.scale_factor * self.zoom_level)
        display_h = int(h * self.scale_factor * self.zoom_level)
        
        # Resize frame
        resized = cv2.resize(self.current_frame, (display_w, display_h),
                            interpolation=cv2.INTER_LINEAR)
        
        self.photo = ImageTk.PhotoImage(Image.fromarray(resized))
        
        # Center on canvas
        x = (cw - display_w) // 2
        y = (ch - display_h) // 2
        
        self.img_offset = (max(0, x), max(0, y))
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo, tags="frame")
        
        # Draw annotations
        if self.show_boxes.get():
            self.draw_annotations()
    
    def draw_annotations(self):
        """Draw annotation boxes"""
        annotations = self.annotations.get(self.frame_number, [])
        scale = self.scale_factor * self.zoom_level
        
        for i, ann in enumerate(annotations):
            x1, y1, x2, y2 = [c * scale + self.img_offset[j % 2] for j, c in enumerate(ann['bbox'])]
            
            color = self.get_class_color(ann['class'])
            width = 3 if i == self.selected_idx else 2
            
            # Draw box
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                        outline=color, width=width, tags="annotation")
            
            # Draw handles if selected
            if i == self.selected_idx:
                for hx, hy in [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]:
                    self.canvas.create_rectangle(hx-4, hy-4, hx+4, hy+4,
                                                fill=color, outline="white",
                                                tags="annotation")
            
            # Draw label
            if self.show_labels.get():
                # Background
                self.canvas.create_rectangle(x1, y1-20, x1 + len(ann['class'])*7 + 8, y1,
                                            fill=color, outline="", tags="annotation")
                # Text
                self.canvas.create_text(x1+4, y1-10, text=ann['class'],
                                       anchor=tk.W, fill="white",
                                       font=("SF Pro Text", 9), tags="annotation")
    
    def refresh_display(self):
        """Refresh the display"""
        self.display_frame()
    
    def update_ui(self):
        """Update UI elements"""
        # Frame info
        self.frame_label.configure(text=f"Frame: {self.frame_number + 1} / {self.total_frames}")
        
        # Time
        if self.fps > 0:
            current_sec = self.frame_number / self.fps
            self.time_current.configure(text=self.format_time(current_sec))
        
        # Timeline
        self.update_timeline()
        
        # Stats
        self.update_stats()
    
    def update_timeline(self):
        """Update timeline slider"""
        self.timeline_canvas.delete("all")
        
        w = self.timeline_canvas.winfo_width()
        h = self.timeline_canvas.winfo_height()
        
        if self.total_frames > 0:
            progress = self.frame_number / self.total_frames
            fill_w = int(w * progress)
            
            # Progress bar
            self.timeline_canvas.create_rectangle(0, 0, fill_w, h,
                                                 fill=Colors.ACCENT_BLUE, outline="")
            
            # Handle
            self.timeline_canvas.create_oval(fill_w-6, -3, fill_w+6, h+3,
                                            fill=Colors.TEXT_PRIMARY, outline="")
    
    def update_stats(self):
        """Update statistics"""
        total = sum(len(a) for a in self.annotations.values())
        frames = len(self.annotations)
        current = len(self.annotations.get(self.frame_number, []))
        
        self.stats['total'].set(str(total))
        self.stats['frames'].set(str(frames))
        self.stats['current'].set(str(current))
    
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        m, s = divmod(int(seconds), 60)
        return f"{m:02d}:{s:02d}"
    
    # ==================== Navigation ====================
    
    def go_first(self):
        if self.cap:
            self.frame_number = 0
            self.load_frame()
    
    def go_last(self):
        if self.cap:
            self.frame_number = self.total_frames - 1
            self.load_frame()
    
    def prev_frame(self):
        if self.cap and self.frame_number > 0:
            self.frame_number -= 1
            self.load_frame()
    
    def next_frame(self):
        if self.cap and self.frame_number < self.total_frames - 1:
            self.frame_number += 1
            self.load_frame()
    
    def skip_back(self):
        if self.cap:
            self.frame_number = max(0, self.frame_number - 10)
            self.load_frame()
    
    def skip_forward(self):
        if self.cap:
            self.frame_number = min(self.total_frames - 1, self.frame_number + 10)
            self.load_frame()
    
    def jump_to_frame(self):
        try:
            frame = int(self.frame_input.get()) - 1
            if 0 <= frame < self.total_frames:
                self.frame_number = frame
                self.load_frame()
                self.frame_input.delete(0, tk.END)
        except ValueError:
            pass
    
    def on_timeline_click(self, event):
        self.seek_timeline(event.x)
    
    def on_timeline_drag(self, event):
        self.seek_timeline(event.x)
    
    def seek_timeline(self, x):
        if not self.cap:
            return
        
        w = self.timeline_canvas.winfo_width()
        progress = max(0, min(1, x / w))
        self.frame_number = int(progress * (self.total_frames - 1))
        self.load_frame()
    
    # ==================== Zoom ====================
    
    def zoom(self, direction):
        factor = 1.2 if direction > 0 else 0.8
        self.zoom_level = max(0.1, min(5.0, self.zoom_level * factor))
        self.display_frame()
        
        zoom_pct = int(self.zoom_level * 100)
        self.zoom_label.configure(text=f"{zoom_pct}%")
        self.status_zoom.configure(text=f"{zoom_pct}%")
    
    def reset_zoom(self):
        self.zoom_level = 1.0
        self.display_frame()
        self.zoom_label.configure(text="100%")
        self.status_zoom.configure(text="100%")
    
    def on_canvas_scroll(self, event):
        if hasattr(event, 'delta'):
            direction = 1 if event.delta > 0 else -1
        else:
            direction = 1 if event.num == 4 else -1
        self.zoom(direction)
    
    # ==================== Canvas Events ====================
    
    def on_canvas_click(self, event):
        if self.current_frame is None:
            return
        
        x, y = event.x, event.y
        
        # Check if clicking on existing box
        annotations = self.annotations.get(self.frame_number, [])
        scale = self.scale_factor * self.zoom_level
        
        for i, ann in enumerate(annotations):
            bx1, by1, bx2, by2 = [c * scale + self.img_offset[j % 2] 
                                  for j, c in enumerate(ann['bbox'])]
            
            # Check corners (resize)
            for cx, cy, mode in [(bx1, by1, "nw"), (bx2, by1, "ne"),
                                  (bx1, by2, "sw"), (bx2, by2, "se")]:
                if abs(x - cx) < 8 and abs(y - cy) < 8:
                    self.selected_idx = i
                    self.is_editing = True
                    self.edit_mode = mode
                    self.drag_start = (x, y)
                    self.display_frame()
                    return
            
            # Check inside (move)
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                self.selected_idx = i
                self.is_editing = True
                self.edit_mode = "move"
                self.drag_start = (x, y)
                self.display_frame()
                return
        
        # Start drawing new box
        if not self.current_class.get():
            self.update_status("Select a class first", warning=True)
            return
        
        self.selected_idx = None
        self.is_drawing = True
        self.drag_start = (x, y)
        self.display_frame()
    
    def on_canvas_drag(self, event):
        if self.is_drawing:
            # Draw preview box
            self.canvas.delete("preview")
            color = self.get_class_color(self.current_class.get())
            self.canvas.create_rectangle(
                self.drag_start[0], self.drag_start[1],
                event.x, event.y,
                outline=color, width=2, dash=(4, 4), tags="preview"
            )
        
        elif self.is_editing and self.selected_idx is not None:
            self.do_edit(event.x, event.y)
    
    def do_edit(self, x, y):
        """Perform edit operation"""
        annotations = self.annotations.get(self.frame_number, [])
        if self.selected_idx >= len(annotations):
            return
        
        ann = annotations[self.selected_idx]
        scale = self.scale_factor * self.zoom_level
        
        dx = (x - self.drag_start[0]) / scale
        dy = (y - self.drag_start[1]) / scale
        
        bx1, by1, bx2, by2 = ann['bbox']
        
        if self.edit_mode == "move":
            ann['bbox'] = [bx1 + dx, by1 + dy, bx2 + dx, by2 + dy]
        else:
            if 'w' in self.edit_mode:
                bx1 += dx
            if 'e' in self.edit_mode:
                bx2 += dx
            if 'n' in self.edit_mode:
                by1 += dy
            if 's' in self.edit_mode:
                by2 += dy
            
            ann['bbox'] = [min(bx1, bx2), min(by1, by2),
                          max(bx1, bx2), max(by1, by2)]
        
        self.drag_start = (x, y)
        self.display_frame()
    
    def on_canvas_release(self, event):
        if self.is_drawing:
            self.finish_drawing(event.x, event.y)
        
        self.is_drawing = False
        self.is_editing = False
        self.edit_mode = None
        self.drag_start = None
    
    def finish_drawing(self, x, y):
        """Finish drawing a box"""
        scale = self.scale_factor * self.zoom_level
        
        x1 = (min(self.drag_start[0], x) - self.img_offset[0]) / scale
        y1 = (min(self.drag_start[1], y) - self.img_offset[1]) / scale
        x2 = (max(self.drag_start[0], x) - self.img_offset[0]) / scale
        y2 = (max(self.drag_start[1], y) - self.img_offset[1]) / scale
        
        # Minimum size
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            self.canvas.delete("preview")
            return
        
        if self.frame_number not in self.annotations:
            self.annotations[self.frame_number] = []
        
        self.annotations[self.frame_number].append({
            'class': self.current_class.get(),
            'bbox': [x1, y1, x2, y2]
        })
        
        self.canvas.delete("preview")
        self.display_frame()
        self.update_stats()
        self.update_status(f"Added: {self.current_class.get()}")
    
    def on_canvas_motion(self, event):
        """Update cursor based on position"""
        if self.current_frame is None:
            return
        
        x, y = event.x, event.y
        annotations = self.annotations.get(self.frame_number, [])
        scale = self.scale_factor * self.zoom_level
        
        for ann in annotations:
            bx1, by1, bx2, by2 = [c * scale + self.img_offset[j % 2]
                                  for j, c in enumerate(ann['bbox'])]
            
            # Check corners
            for cx, cy in [(bx1, by1), (bx2, by1), (bx1, by2), (bx2, by2)]:
                if abs(x - cx) < 8 and abs(y - cy) < 8:
                    self.canvas.configure(cursor="sizing")
                    return
            
            # Check inside
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                self.canvas.configure(cursor="fleur")
                return
        
        self.canvas.configure(cursor="crosshair")
    
    def on_canvas_double_click(self, event):
        self.deselect()
    
    def deselect(self):
        self.selected_idx = None
        self.display_frame()
    
    # ==================== Edit Operations ====================
    
    def delete_selected(self):
        if self.selected_idx is not None:
            annotations = self.annotations.get(self.frame_number, [])
            if self.selected_idx < len(annotations):
                removed = annotations.pop(self.selected_idx)
                self.selected_idx = None
                self.display_frame()
                self.update_stats()
                self.update_status(f"Deleted: {removed['class']}")
    
    def undo(self):
        annotations = self.annotations.get(self.frame_number, [])
        if annotations:
            removed = annotations.pop()
            self.display_frame()
            self.update_stats()
            self.update_status(f"Undid: {removed['class']}")
    
    def copy_previous(self):
        if self.frame_number <= 0:
            return
        
        prev = self.annotations.get(self.frame_number - 1, [])
        if not prev:
            self.update_status("No annotations to copy", warning=True)
            return
        
        if self.frame_number not in self.annotations:
            self.annotations[self.frame_number] = []
        
        for ann in prev:
            self.annotations[self.frame_number].append(copy.deepcopy(ann))
        
        self.display_frame()
        self.update_stats()
        self.update_status(f"Copied {len(prev)} annotations")
    
    def clear_frame(self):
        if self.frame_number in self.annotations:
            count = len(self.annotations[self.frame_number])
            self.annotations[self.frame_number] = []
            self.selected_idx = None
            self.display_frame()
            self.update_stats()
            self.update_status(f"Cleared {count} annotations")
    
    def quick_class(self, idx):
        if idx < len(self.classes):
            self.select_class(self.classes[idx])
    
    # ==================== Save/Export ====================
    
    def save_project(self):
        if not self.annotations:
            messagebox.showwarning("Warning", "No annotations to save")
            return
        
        save_dir = filedialog.askdirectory(title="Select Save Location")
        if not save_dir:
            return
        
        # Project name
        default = Path(self.video_path).stem if self.video_path else "project"
        
        from tkinter import simpledialog
        name = simpledialog.askstring("Project Name", "Enter name:",
                                     initialvalue=default, parent=self.root)
        if not name:
            return
        
        # Create directories
        self.output_dir = Path(save_dir) / name
        (self.output_dir / "images").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "labels").mkdir(parents=True, exist_ok=True)
        
        try:
            fmt = self.export_format.get()
            
            if fmt == "YOLO":
                self.save_yolo()
            elif fmt == "VOC":
                self.save_voc()
            elif fmt == "COCO":
                self.save_coco()
            
            messagebox.showinfo("Success", f"Saved to:\n{self.output_dir}")
            self.update_status(f"Saved: {name}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def save_yolo(self):
        classes = self.classes + self.custom_classes
        
        with open(self.output_dir / "classes.txt", 'w') as f:
            f.write("\n".join(classes))
        
        for frame_num, anns in self.annotations.items():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            
            if ret:
                cv2.imwrite(str(self.output_dir / "images" / f"frame_{frame_num:06d}.jpg"), frame)
                
                h, w = frame.shape[:2]
                
                with open(self.output_dir / "labels" / f"frame_{frame_num:06d}.txt", 'w') as f:
                    for ann in anns:
                        cls_idx = classes.index(ann['class'])
                        x1, y1, x2, y2 = ann['bbox']
                        
                        cx = (x1 + x2) / 2 / w
                        cy = (y1 + y2) / 2 / h
                        bw = (x2 - x1) / w
                        bh = (y2 - y1) / h
                        
                        f.write(f"{cls_idx} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
    
    def save_voc(self):
        for frame_num, anns in self.annotations.items():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            
            if ret:
                img_name = f"frame_{frame_num:06d}.jpg"
                cv2.imwrite(str(self.output_dir / "images" / img_name), frame)
                
                root = ET.Element("annotation")
                ET.SubElement(root, "filename").text = img_name
                
                size = ET.SubElement(root, "size")
                ET.SubElement(size, "width").text = str(frame.shape[1])
                ET.SubElement(size, "height").text = str(frame.shape[0])
                ET.SubElement(size, "depth").text = "3"
                
                for ann in anns:
                    obj = ET.SubElement(root, "object")
                    ET.SubElement(obj, "name").text = ann['class']
                    
                    bbox = ET.SubElement(obj, "bndbox")
                    ET.SubElement(bbox, "xmin").text = str(int(ann['bbox'][0]))
                    ET.SubElement(bbox, "ymin").text = str(int(ann['bbox'][1]))
                    ET.SubElement(bbox, "xmax").text = str(int(ann['bbox'][2]))
                    ET.SubElement(bbox, "ymax").text = str(int(ann['bbox'][3]))
                
                tree = ET.ElementTree(root)
                tree.write(str(self.output_dir / "labels" / f"frame_{frame_num:06d}.xml"))
    
    def save_coco(self):
        classes = self.classes + self.custom_classes
        
        coco = {
            "images": [],
            "annotations": [],
            "categories": [{"id": i+1, "name": c} for i, c in enumerate(classes)]
        }
        
        ann_id = 1
        
        for frame_num, anns in self.annotations.items():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()
            
            if ret:
                img_name = f"frame_{frame_num:06d}.jpg"
                cv2.imwrite(str(self.output_dir / "images" / img_name), frame)
                
                img_id = frame_num + 1
                coco["images"].append({
                    "id": img_id,
                    "file_name": img_name,
                    "width": frame.shape[1],
                    "height": frame.shape[0]
                })
                
                for ann in anns:
                    x1, y1, x2, y2 = ann['bbox']
                    coco["annotations"].append({
                        "id": ann_id,
                        "image_id": img_id,
                        "category_id": classes.index(ann['class']) + 1,
                        "bbox": [x1, y1, x2-x1, y2-y1],
                        "area": (x2-x1) * (y2-y1),
                        "iscrowd": 0
                    })
                    ann_id += 1
        
        with open(self.output_dir / "annotations.json", 'w') as f:
            json.dump(coco, f, indent=2)
    
    def show_help(self):
        """Show help dialog"""
        help_win = tk.Toplevel(self.root)
        help_win.title("Help")
        help_win.geometry("450x500")
        help_win.configure(bg=Colors.BG_PRIMARY)
        help_win.transient(self.root)
        
        # Content
        inner = tk.Frame(help_win, bg=Colors.BG_PRIMARY)
        inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        tk.Label(inner, text="AnnotateX Help",
                font=("SF Pro Display", 18, "bold"),
                fg=Colors.TEXT_PRIMARY, bg=Colors.BG_PRIMARY).pack(anchor=tk.W)
        
        sections = [
            ("Getting Started", [
                "1. Open a video file",
                "2. Select a class from the left panel",
                "3. Click and drag to draw boxes",
                "4. Save your annotations"
            ]),
            ("Mouse Controls", [
                "• Click + drag: Draw new box",
                "• Click on box: Select it",
                "• Drag box: Move it",
                "• Drag corners: Resize",
                "• Scroll: Zoom in/out"
            ]),
            ("Keyboard", [
                "← →  Navigate frames",
                "Space  Next frame",
                "Del  Delete selected",
                "Ctrl+Z  Undo",
                "Esc  Deselect"
            ])
        ]
        
        for title, items in sections:
            tk.Label(inner, text=title,
                    font=("SF Pro Text", 12, "bold"),
                    fg=Colors.ACCENT_BLUE, bg=Colors.BG_PRIMARY).pack(anchor=tk.W, pady=(20, 8))
            
            for item in items:
                tk.Label(inner, text=item,
                        font=("SF Pro Text", 10),
                        fg=Colors.TEXT_SECONDARY, bg=Colors.BG_PRIMARY).pack(anchor=tk.W, padx=12)
        
        # Close button
        close = tk.Label(inner, text="Close",
                        font=("SF Pro Text", 10),
                        fg=Colors.TEXT_PRIMARY, bg=Colors.BG_ELEVATED,
                        padx=20, pady=8, cursor="hand2")
        close.pack(pady=24)
        close.bind("<Button-1>", lambda e: help_win.destroy())
    
    def cleanup(self):
        if self.cap:
            self.cap.release()


def main():
    root = tk.Tk()
    app = AnnotateX(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()