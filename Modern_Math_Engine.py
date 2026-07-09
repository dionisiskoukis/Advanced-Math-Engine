import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, solve, diff, integrate, simplify, sympify, lambdify, SympifyError, Eq, log, ln, exp, sqrt, sin, cos, tan, asin, acos, atan
import threading
from PIL import Image, ImageTk
import json
import re
import webbrowser
from datetime import datetime
from pathlib import Path

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Application constants
APP_NAME = "ProMath Calculator"
APP_VERSION = "2.0.0"
APP_COPYRIGHT = "© 2024 ProMath Solutions"
APP_LICENSE = "Commercial License"

x = symbols('x')

# Compatibility function for math.comb (Python < 3.8)
def safe_comb(n, k):
    """Calculate combinations with fallback for Python < 3.8"""
    if hasattr(math, 'comb'):
        return math.comb(n, k)
    else:
        if k > n or k < 0 or n < 0:
            raise ValueError("Invalid combination parameters")
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

class CommercialMathCalculator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("ProMath Calculator - Professional Mathematical Suite")
        self.root.geometry("1600x1000")
        self.root.state('zoomed')  # Start maximized on Windows
        
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Initialize variables
        self.graph_functions = []
        self.current_theme = "dark"
        self.auto_save_enabled = True
        
        # Create user data directory
        self.user_data_dir = Path.home() / ".promath_calculator"
        self.user_data_dir.mkdir(exist_ok=True)
        
        # Set up window closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()
        self.setup_graph()
        self.setup_keyboard_shortcuts()
        self.schedule_auto_save()
        
    def setup_ui(self):
        # Top menu bar
        self.create_menu_bar()
        
        # Status bar
        self.create_status_bar()
        
        # Main container
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(1, weight=2)
        main_container.grid_columnconfigure(2, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left panel - Operations
        self.create_operations_panel(main_container)
        
        # Center panel - Graph
        self.create_graph_panel(main_container)
        
        # Right panel - Output and Controls
        self.create_output_panel(main_container)
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready", 
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Version info on right
        version_label = ctk.CTkLabel(
            self.status_frame, 
            text=f"{APP_NAME} v{APP_VERSION}", 
            font=ctk.CTkFont(size=11),
            anchor="e"
        )
        version_label.pack(side="right", padx=10, pady=5)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=message)
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-s>', lambda e: self.save_results())
        self.root.bind('<Control-o>', lambda e: self.load_session())
        self.root.bind('<Control-n>', lambda e: self.clear_all_data())
        self.root.bind('<Control-c>', lambda e: self.copy_results())
        self.root.bind('<Control-z>', lambda e: self.undo_last())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Delete>', lambda e: self.clear_output())
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        self.update_status("Fullscreen toggled")
        
    def create_menu_bar(self):
        """Create professional menu bar"""
        menu_frame = ctk.CTkFrame(self.root, height=50, corner_radius=0)
        menu_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        menu_frame.grid_columnconfigure(0, weight=1)
        
        # Logo and title
        title_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🧮 ProMath Calculator", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray10", "white")
        )
        title_label.pack(side="left")
        
        # Menu buttons
        menu_buttons_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        menu_buttons_frame.grid(row=0, column=1, sticky="e", padx=20, pady=10)
        
        buttons = [
            ("📁 File", self.file_menu),
            ("✏️ Edit", self.edit_menu),
            ("🔧 Tools", self.tools_menu),
            ("🎨 View", self.view_menu),
            ("❓ Help", self.help_menu)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_buttons_frame,
                text=text,
                command=command,
                width=100,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color=("gray80", "gray20")
            )
            btn.pack(side="left", padx=5)
    
    def create_operations_panel(self, parent):
        """Create modern operations panel"""
        ops_frame = ctk.CTkScrollableFrame(
            parent, 
            width=350,
            corner_radius=15,
            label_text="📊 Mathematical Operations",
            label_font=ctk.CTkFont(size=16, weight="bold")
        )
        ops_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        ops_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.create_operation_buttons(ops_frame)
    
    def create_graph_panel(self, parent):
        """Create advanced graphing panel"""
        graph_frame = ctk.CTkFrame(parent, corner_radius=15)
        graph_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        graph_frame.grid_columnconfigure(0, weight=1)
        graph_frame.grid_rowconfigure(1, weight=1)
        
        # Graph controls header
        controls_frame = ctk.CTkFrame(graph_frame, height=80, corner_radius=10)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Function input
        ctk.CTkLabel(
            controls_frame, 
            text="📈 Function Plotter", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(10, 5))
        
        ctk.CTkLabel(controls_frame, text="f(x) =").grid(row=1, column=0, padx=(10, 5), pady=5)
        
        self.function_entry = ctk.CTkEntry(
            controls_frame, 
            placeholder_text="Enter function (e.g., x**2, sin(x), log(x))",
            width=300,
            font=ctk.CTkFont(size=12)
        )
        self.function_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.function_entry.bind("<Return>", lambda e: self.plot_function())
        
        plot_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Plot",
            command=self.plot_function,
            width=80,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        plot_btn.grid(row=1, column=2, padx=(5, 10), pady=5)
        
        # Range controls
        range_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        range_frame.grid(row=2, column=0, columnspan=3, pady=5, padx=10, sticky="ew")
        range_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(range_frame, text="X Range:").grid(row=0, column=0, padx=(0, 5))
        self.x_min_entry = ctk.CTkEntry(range_frame, width=60, placeholder_text="-10")
        self.x_min_entry.grid(row=0, column=1, padx=2)
        ctk.CTkLabel(range_frame, text="to").grid(row=0, column=2, padx=5)
        self.x_max_entry = ctk.CTkEntry(range_frame, width=60, placeholder_text="10")
        self.x_max_entry.grid(row=0, column=3, padx=2)
        
        clear_btn = ctk.CTkButton(
            range_frame,
            text="🗑️ Clear",
            command=self.clear_graph,
            width=80,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray30"),
            border_width=2,
            border_color=("gray50", "gray50"),
            text_color=("gray10", "gray90"),
            hover_color=("gray60", "gray40")
        )
        clear_btn.grid(row=0, column=4, padx=(10, 0))
        
        # Graph canvas frame
        canvas_frame = ctk.CTkFrame(graph_frame, corner_radius=10)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        # This will be set up in setup_graph()
        self.canvas_frame = canvas_frame
    
    def create_output_panel(self, parent):
        """Create modern output panel"""
        output_frame = ctk.CTkFrame(parent, width=400, corner_radius=15)
        output_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(1, weight=1)
        
        # Output header
        header_frame = ctk.CTkFrame(output_frame, height=60, corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, 
            text="📋 Calculation Results", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, pady=15)
        
        # Output text area
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10,
            wrap="word"
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Control buttons
        button_frame = ctk.CTkFrame(output_frame, height=50, corner_radius=10)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        clear_output_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear Output",
            command=self.clear_output,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray70", "gray30"),
            border_width=2,
            border_color=("gray50", "gray50"),
            text_color=("gray10", "gray90"),
            hover_color=("gray60", "gray40")
        )
        clear_output_btn.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Results",
            command=self.save_results,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "gray25"),
            hover_color=("gray65", "gray35")
        )
        save_btn.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
    
    def setup_graph(self):
        """Setup matplotlib graph"""
        # Create figure with dark theme
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#212121')
        self.ax = self.fig.add_subplot(111, facecolor='#2b2b2b')
        
        # Customize appearance
        self.ax.grid(True, alpha=0.3, color='white')
        self.ax.set_xlabel('x', color='white', fontsize=12)
        self.ax.set_ylabel('y', color='white', fontsize=12)
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add navigation toolbar
        toolbar_frame = ctk.CTkFrame(self.canvas_frame, height=40)
        toolbar_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Customize toolbar appearance
        self.toolbar.configure(bg='#2b2b2b')
        for child in self.toolbar.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg='#404040', fg='white', relief='flat', bd=1)
    
    def create_operation_buttons(self, parent):
        """Create all operation buttons with modern styling"""
        operations = [
            ("🔢 Basic Operations", [
                ("➕ Addition", self.addition),
                ("➖ Subtraction", self.subtraction),
                ("✖️ Multiplication", self.multiplication),
                ("➗ Division", self.division),
                ("⚡ Power", self.power),
                ("√ Square Root", self.square_root),
                ("∛ Cube Root", self.cbrt),
                ("| | Absolute Value", self.absolute_value),
                ("ln Natural Log", self.natural_log),
                ("log₁₀ Base-10 Log", self.log10),
            ]),
            ("📐 Trigonometry", [
                ("sin Sine", self.sine),
                ("cos Cosine", self.cosine),
                ("tan Tangent", self.tangent),
                ("asin Arc Sine", self.arc_sine),
                ("acos Arc Cosine", self.arc_cosine),
                ("atan Arc Tangent", self.arc_tangent),
                ("°→rad Deg to Rad", self.degrees_to_radians),
                ("rad→° Rad to Deg", self.radians_to_degrees),
            ]),
            ("⚛️ Physics Formulas", [
                ("🏋️ Density (d=m/v)", self.density),
                ("⚖️ Weight (w=mg)", self.weight),
                ("🚀 Newton's Law (F=ma)", self.newtons_law),
                ("📏 Pythagorean Theorem", self.pythagorean_theorem),
            ]),
            ("🎯 Advanced Math", [
                ("! Factorial", self.factorial),
                ("C Combination", self.comb),
                ("P Permutation", self.permutation),
                ("Γ Gamma Function", self.gamma),
                ("= Solve Equation", self.equation),
                ("d/dx Derivative", self.symbolic_derivative),
                ("∫ Integral", self.symbolic_integral),
                ("≡ Simplify Expression", self.symbolic_simplify),
                ("lim Limit", self.symbolic_limit),
            ]),
            ("📐 Geometry", [
                ("⭕ Circle Circumference", self.circumference_of_circle),
                ("🔵 Circle Area", self.area),
                ("📐 Triangle Area", self.triangle_area),
                ("▭ Rectangle Area", self.rectangle_area),
            ]),
            ("🔢 Constants", [
                ("π Pi", self.pi),
                ("e Euler's number", self.e),
                ("τ Tau", self.tau),
            ]),
            ("💰 Finance", [
                ("📈 ROI Calculator", self.calculate_roi),
                ("💵 Simple Interest", self.simple_interest),
                ("🏦 Compound Interest", self.compound_interest),
            ])
        ]
        
        row = 0
        for category, ops in operations:
            # Category header
            category_label = ctk.CTkLabel(
                parent, 
                text=category, 
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            category_label.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(15, 8), padx=10)
            row += 1
            
            # Operation buttons
            col = 0
            for op_name, op_func in ops:
                btn = ctk.CTkButton(
                    parent,
                    text=op_name,
                    command=op_func,
                    height=40,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    corner_radius=8,
                    hover_color=("gray70", "gray30"),
                    fg_color=("gray75", "gray25"),
                    text_color=("gray10", "gray90"),
                    border_width=1,
                    border_color=("gray60", "gray40")
                )
                btn.grid(row=row, column=col, padx=5, pady=3, sticky="ew")
                col += 1
                if col > 1:
                    col = 0
                    row += 1
            
            if col != 0:
                row += 1
    
    def parse_mathematical_expression(self, expr_str):
        """Parse and clean mathematical expressions for better display and evaluation"""
        if not expr_str:
            return expr_str
            
        # Replace common mathematical notation
        expr_str = expr_str.replace('^', '**')  # Power notation
        expr_str = expr_str.replace('ln', 'log')  # Natural log
        
        # Handle implicit multiplication comprehensively
        import re
        
        # Number followed by variable or function: 2x, 3sin, 10cos -> 2*x, 3*sin, 10*cos
        expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
        
        # Number followed by parenthesis: 2( -> 2*(
        expr_str = re.sub(r'(\d)(\()', r'\1*\2', expr_str)
        
        # Closing parenthesis followed by variable/function: )x, )sin -> )*x, )*sin
        expr_str = re.sub(r'(\))([a-zA-Z])', r'\1*\2', expr_str)
        
        # Closing parenthesis followed by opening parenthesis: )( -> )*(
        expr_str = re.sub(r'(\))(\()', r'\1*\2', expr_str)
        
        # Variable followed by parenthesis: x( -> x*(
        expr_str = re.sub(r'([a-zA-Z])(\()', r'\1*\2', expr_str)
        
        # Variable followed by function: xsin, xcos -> x*sin, x*cos
        expr_str = re.sub(r'([a-zA-Z])([a-zA-Z]{2,})', r'\1*\2', expr_str)
        
        # Handle special cases for common functions
        # Fix over-multiplication of function names
        expr_str = re.sub(r's\*i\*n', 'sin', expr_str)
        expr_str = re.sub(r'c\*o\*s', 'cos', expr_str)
        expr_str = re.sub(r't\*a\*n', 'tan', expr_str)
        expr_str = re.sub(r'l\*o\*g', 'log', expr_str)
        expr_str = re.sub(r's\*q\*r\*t', 'sqrt', expr_str)
        expr_str = re.sub(r'e\*x\*p', 'exp', expr_str)
        expr_str = re.sub(r'a\*b\*s', 'abs', expr_str)
        
        return expr_str
    
    def format_expression_for_display(self, expr_str):
        """Format expression for better display"""
        if not expr_str:
            return expr_str
            
        # Replace ** with ^ for display
        display_expr = expr_str.replace('**', '^')
        # Replace * with · for better visual appearance
        display_expr = re.sub(r'(\d)\*([a-zA-Z])', r'\1·\2', display_expr)
        display_expr = re.sub(r'([a-zA-Z])\*(\d)', r'\1·\2', display_expr)
        
        return display_expr
    
    # Graph functions
    def plot_function(self):
        """Plot mathematical function"""
        try:
            func_str = self.function_entry.get().strip()
            if not func_str:
                messagebox.showwarning("Warning", "Please enter a function")
                return
            
            # Get range
            try:
                x_min = float(self.x_min_entry.get()) if self.x_min_entry.get() else -20
                x_max = float(self.x_max_entry.get()) if self.x_max_entry.get() else 20
            except ValueError:
                x_min, x_max = -20, 20
            
            # Create x values
            x_vals = np.linspace(x_min, x_max, 2000)  # More points for smoother curves
            
            # Parse and evaluate function
            try:
                # Parse the mathematical expression
                parsed_func = self.parse_mathematical_expression(func_str)
                display_func = self.format_expression_for_display(func_str)
                
                # Convert to sympy expression
                expr = sympify(parsed_func)
                
                # Convert to numpy function
                func = lambdify(x, expr, modules=['numpy', 'math'])
                
                # Evaluate function
                with np.errstate(divide='ignore', invalid='ignore'):
                    y_vals = func(x_vals)
                
                # Handle infinite and NaN values
                y_vals = np.where(np.isfinite(y_vals), y_vals, np.nan)
                
                # Plot
                colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                color = colors[len(self.graph_functions) % len(colors)]
                
                line, = self.ax.plot(x_vals, y_vals, color=color, linewidth=2.5, 
                                   label=f'f(x) = {display_func}', alpha=0.8)
                
                self.graph_functions.append((display_func, line))
                
                # Update legend with better styling
                legend = self.ax.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white', 
                                      framealpha=0.9, fontsize=10)
                legend.get_frame().set_linewidth(1)
                
                self.ax.set_xlim(x_min, x_max)
                
                # Auto-scale y-axis
                finite_y = y_vals[np.isfinite(y_vals)]
                if len(finite_y) > 0:
                    y_range = np.max(finite_y) - np.min(finite_y)
                    y_margin = max(y_range * 0.1, 1)  # At least 1 unit margin
                    y_min = np.min(finite_y) - y_margin
                    y_max = np.max(finite_y) + y_margin
                    
                    # Limit extreme values
                    if y_max - y_min > 1000:
                        y_center = (y_max + y_min) / 2
                        y_min = y_center - 500
                        y_max = y_center + 500
                    
                    self.ax.set_ylim(y_min, y_max)
                
                self.canvas.draw()
                self.log_output(f"📊 Plotted function: f(x) = {display_func}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error plotting function: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def clear_graph(self):
        """Clear the graph"""
        self.ax.clear()
        self.graph_functions.clear()
        
        # Reset graph appearance
        self.ax.grid(True, alpha=0.3, color='white', linestyle='-', linewidth=0.5)
        self.ax.axhline(y=0, color='white', linewidth=1, alpha=0.7)
        self.ax.axvline(x=0, color='white', linewidth=1, alpha=0.7)
        self.ax.set_xlabel('x', color='white', fontsize=12)
        self.ax.set_ylabel('y', color='white', fontsize=12)
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        self.canvas.draw()
        self.log_output("🗑️ Graph cleared")
    
    # Menu functions
    def file_menu(self):
        """File menu operations"""
        menu_window = ctk.CTkToplevel(self.root)
        menu_window.title("File Menu")
        menu_window.geometry("300x400")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        buttons = [
            ("📄 New Session", self.clear_all_data),
            ("📁 Load Session", self.load_session),
            ("💾 Save Session", self.save_session),
            ("💾 Save Results", self.save_results),
            ("📤 Export Graph", self.export_graph),
            ("📊 Export All Data", self.export_all_data),
            ("📥 Import Data", self.import_data),
            ("🖨️ Print Results", self.print_results),
            ("❌ Exit", self.on_closing)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                menu_window,
                text=text,
                command=lambda cmd=command: [cmd(), menu_window.destroy()],
                width=250,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(pady=5, padx=25)
    
    def edit_menu(self):
        """Edit menu operations"""
        menu_window = ctk.CTkToplevel(self.root)
        menu_window.title("Edit Menu")
        menu_window.geometry("300x300")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        buttons = [
            ("📋 Copy Results", self.copy_results),
            ("↶ Undo Last", self.undo_last),
            ("🗑️ Clear Output", self.clear_output),
            ("🗑️ Clear All Data", self.clear_all_data),
            ("⚙️ Preferences", self.show_preferences)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_window,
                text=text,
                command=lambda cmd=command: [cmd(), menu_window.destroy()],
                width=250,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(pady=5, padx=25)
    
    def tools_menu(self):
        """Tools menu operations"""
        menu_window = ctk.CTkToplevel(self.root)
        menu_window.title("Tools Menu")
        menu_window.geometry("300x350")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        buttons = [
            ("📚 Function Library", self.show_function_library),
            ("🔄 Unit Converter", self.show_unit_converter),
            ("📊 Statistics Calculator", self.show_statistics),
            ("🔍 Check for Updates", self.check_for_updates)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_window,
                text=text,
                command=lambda cmd=command: [cmd(), menu_window.destroy()],
                width=250,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(pady=5, padx=25)
    
    def view_menu(self):
        """View menu operations"""
        menu_window = ctk.CTkToplevel(self.root)
        menu_window.title("View Menu")
        menu_window.geometry("300x250")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        buttons = [
            ("🎨 Toggle Theme", self.toggle_theme),
            ("🖥️ Toggle Fullscreen", self.toggle_fullscreen),
            ("📊 Export Graph", self.export_graph)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_window,
                text=text,
                command=lambda cmd=command: [cmd(), menu_window.destroy()],
                width=250,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(pady=5, padx=25)
    
    def help_menu(self):
        """Help menu operations"""
        menu_window = ctk.CTkToplevel(self.root)
        menu_window.title("Help Menu")
        menu_window.geometry("300x350")
        menu_window.transient(self.root)
        menu_window.grab_set()
        
        buttons = [
            ("📖 User Guide", self.show_user_guide),
            ("⌨️ Keyboard Shortcuts", self.show_shortcuts),
            ("🐛 Report Bug", self.report_bug),
            ("📞 Contact Support", self.contact_support),
            ("ℹ️ About", self.show_about)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_window,
                text=text,
                command=lambda cmd=command: [cmd(), menu_window.destroy()],
                width=250,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            btn.pack(pady=5, padx=25)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "dark":
            ctk.set_appearance_mode("light")
            self.current_theme = "light"
            plt.style.use('default')
        else:
            ctk.set_appearance_mode("dark")
            self.current_theme = "dark"
            plt.style.use('dark_background')
        
        # Recreate graph with new theme
        self.setup_graph()
        self.log_output(f"🎨 Theme changed to {self.current_theme}")
    
    def export_graph(self):
        """Export current graph"""
        if not self.graph_functions:
            messagebox.showwarning("Warning", "No graph to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")]
        )
        
        if filename:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            self.log_output(f"📊 Graph exported to {filename}")
    
    def save_results(self):
        """Save calculation results"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf")]
        )
        
        if filename:
            try:
                content = self.output_text.get("1.0", "end-1c")
                
                if not content.strip():
                    messagebox.showwarning("Warning", "No results to save. Please perform some calculations first.")
                    return
                
                if filename.lower().endswith('.pdf'):
                    self.save_as_pdf(filename, content)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.log_output(f"💾 Results saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving results: {str(e)}")
                self.update_status("Error saving results")
    
    def copy_results(self):
        """Copy results to clipboard"""
        try:
            content = self.output_text.get("1.0", "end-1c")
            if not content.strip():
                messagebox.showwarning("Warning", "No results to copy!")
                return
            
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("Results copied to clipboard")
            messagebox.showinfo("Success", "Results copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying results: {e}")
    
    def clear_all_data(self):
        """Clear all data with confirmation"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all data? This cannot be undone."):
            self.clear_output()
            if hasattr(self, 'ax'):
                self.ax.clear()
                self.setup_graph()
                self.canvas.draw()
            self.update_status("All data cleared")
    
    def undo_last(self):
        """Undo last calculation (simple implementation)"""
        try:
            content = self.output_text.get("1.0", "end-1c")
            lines = content.strip().split('\n')
            if len(lines) > 1:
                # Remove last line
                new_content = '\n'.join(lines[:-1]) + '\n'
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", new_content)
                self.update_status("Last calculation undone")
            else:
                messagebox.showinfo("Info", "Nothing to undo")
        except Exception as e:
            messagebox.showerror("Error", f"Error undoing: {e}")
    
    def import_data(self):
        """Import data from file"""
        try:
            filename = filedialog.askopenfilename(
                title="Import Data",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    if filename.endswith('.json'):
                        data = json.load(f)
                        if 'calculations' in data:
                            self.output_text.insert("end", data['calculations'])
                    else:
                        content = f.read()
                        self.output_text.insert("end", content)
                self.update_status(f"Data imported from {filename}")
                messagebox.showinfo("Success", "Data imported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {e}")
    
    def export_all_data(self):
        """Export all data including settings"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export All Data",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                data = {
                    'app_version': APP_VERSION,
                    'export_date': datetime.now().isoformat(),
                    'calculations': self.output_text.get("1.0", "end-1c"),
                    'theme': ctk.get_appearance_mode(),
                    'settings': {
                        'auto_save': self.auto_save_enabled,
                        'window_geometry': self.root.geometry()
                    }
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.update_status(f"All data exported to {filename}")
                messagebox.showinfo("Success", f"All data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {e}")
    
    def show_preferences(self):
        """Show preferences dialog"""
        pref_window = ctk.CTkToplevel(self.root)
        pref_window.title("Preferences")
        pref_window.geometry("400x300")
        pref_window.transient(self.root)
        pref_window.grab_set()
        
        # Auto-save setting
        auto_save_var = ctk.BooleanVar(value=self.auto_save_enabled)
        auto_save_check = ctk.CTkCheckBox(
            pref_window, 
            text="Enable auto-save", 
            variable=auto_save_var
        )
        auto_save_check.pack(pady=20, padx=20, anchor="w")
        
        # Theme setting
        theme_label = ctk.CTkLabel(pref_window, text="Theme:")
        theme_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            pref_window, 
            values=["Light", "Dark", "System"],
            variable=theme_var
        )
        theme_menu.pack(pady=5, padx=20, anchor="w")
        
        def save_preferences():
            self.auto_save_enabled = auto_save_var.get()
            ctk.set_appearance_mode(theme_var.get())
            self.update_status("Preferences saved")
            pref_window.destroy()
        
        save_btn = ctk.CTkButton(pref_window, text="Save", command=save_preferences)
        save_btn.pack(pady=20)
    
    def print_results(self):
        """Print results (opens print dialog)"""
        try:
            content = self.output_text.get("1.0", "end-1c")
            if not content.strip():
                messagebox.showwarning("Warning", "No results to print!")
                return
            
            # Create temporary HTML file for printing
            temp_file = self.user_data_dir / "temp_print.html"
            html_content = f"""
            <html>
            <head><title>{APP_NAME} - Results</title></head>
            <body>
            <h1>{APP_NAME} - Calculation Results</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <pre>{content}</pre>
            </body>
            </html>
            """
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            webbrowser.open(f"file://{temp_file}")
            self.update_status("Print dialog opened")
        except Exception as e:
            messagebox.showerror("Error", f"Error printing: {e}")
    
    def show_function_library(self):
        """Show function library dialog"""
        lib_window = ctk.CTkToplevel(self.root)
        lib_window.title("Function Library")
        lib_window.geometry("600x400")
        lib_window.transient(self.root)
        
        functions_text = """
Mathematical Functions Available:

Basic Functions:
• sin(x), cos(x), tan(x) - Trigonometric functions
• asin(x), acos(x), atan(x) - Inverse trigonometric
• log(x), ln(x) - Logarithmic functions
• sqrt(x), exp(x) - Square root and exponential
• abs(x) - Absolute value

Advanced Functions:
• factorial(n) - n!
• gamma(x) - Gamma function
• erf(x), erfc(x) - Error functions
• comb(n,k), perm(n,k) - Combinations and permutations

Constants:
• pi, e, tau - Mathematical constants

Operators:
• +, -, *, / - Basic arithmetic
• ** or ^ - Exponentiation
• Implicit multiplication: 2x = 2*x, 3sin(x) = 3*sin(x)
        """
        
        text_widget = ctk.CTkTextbox(lib_window, width=580, height=360)
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)
        text_widget.insert("1.0", functions_text)
        text_widget.configure(state="disabled")
    
    def show_unit_converter(self):
        """Show unit converter dialog"""
        conv_window = ctk.CTkToplevel(self.root)
        conv_window.title("Unit Converter")
        conv_window.geometry("400x300")
        conv_window.transient(self.root)
        
        # Simple length converter example
        ctk.CTkLabel(conv_window, text="Length Converter", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        value_entry = ctk.CTkEntry(conv_window, placeholder_text="Enter value")
        value_entry.pack(pady=10)
        
        from_unit = ctk.CTkOptionMenu(conv_window, values=["meters", "feet", "inches", "centimeters"])
        from_unit.pack(pady=5)
        
        to_unit = ctk.CTkOptionMenu(conv_window, values=["meters", "feet", "inches", "centimeters"])
        to_unit.pack(pady=5)
        
        result_label = ctk.CTkLabel(conv_window, text="Result will appear here")
        result_label.pack(pady=10)
        
        def convert():
            try:
                val = float(value_entry.get())
                # Simple conversion logic (extend as needed)
                conversions = {
                    "meters": 1.0,
                    "feet": 3.28084,
                    "inches": 39.3701,
                    "centimeters": 100.0
                }
                
                from_factor = conversions[from_unit.get()]
                to_factor = conversions[to_unit.get()]
                
                # Convert to meters first, then to target unit
                meters = val / from_factor
                result = meters * to_factor
                
                result_label.configure(text=f"{val} {from_unit.get()} = {result:.6f} {to_unit.get()}")
            except ValueError:
                result_label.configure(text="Please enter a valid number")
            except Exception as e:
                result_label.configure(text=f"Error: {e}")
        
        ctk.CTkButton(conv_window, text="Convert", command=convert).pack(pady=10)
        
        conv_window.transient(self.root)
        conv_window.grab_set()
    
    def show_statistics(self):
        """Show statistics calculator"""
        stats_window = ctk.CTkToplevel(self.root)
        stats_window.title("Statistics Calculator")
        stats_window.geometry("500x400")
        stats_window.transient(self.root)
        
        ctk.CTkLabel(stats_window, text="Statistics Calculator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        data_entry = ctk.CTkTextbox(stats_window, height=100, placeholder_text="Enter numbers separated by commas or spaces")
        data_entry.pack(pady=10, padx=20, fill="x")
        
        result_text = ctk.CTkTextbox(stats_window, height=200)
        result_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        def calculate_stats():
            try:
                data_str = data_entry.get("1.0", "end-1c")
                # Parse numbers from text
                import re
                numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', data_str)]
                
                if not numbers:
                    result_text.delete("1.0", "end")
                    result_text.insert("1.0", "Please enter some numbers")
                    return
                
                # Calculate statistics
                n = len(numbers)
                mean = sum(numbers) / n
                sorted_nums = sorted(numbers)
                
                # Median
                if n % 2 == 0:
                    median = (sorted_nums[n//2-1] + sorted_nums[n//2]) / 2
                else:
                    median = sorted_nums[n//2]
                
                # Standard deviation
                variance = sum((x - mean) ** 2 for x in numbers) / n
                std_dev = variance ** 0.5
                
                stats_result = f"""Statistics for {n} numbers:

Data: {numbers}

Mean (Average): {mean:.6f}
Median: {median:.6f}
Minimum: {min(numbers):.6f}
Maximum: {max(numbers):.6f}
Range: {max(numbers) - min(numbers):.6f}
Sum: {sum(numbers):.6f}

Standard Deviation: {std_dev:.6f}
Variance: {variance:.6f}
"""
                
                result_text.delete("1.0", "end")
                result_text.insert("1.0", stats_result)
                
            except Exception as e:
                result_text.delete("1.0", "end")
                result_text.insert("1.0", f"Error calculating statistics: {e}")
        
        ctk.CTkButton(stats_window, text="Calculate Statistics", command=calculate_stats).pack(pady=10)
    
    def check_for_updates(self):
        """Check for updates (placeholder)"""
        messagebox.showinfo("Updates", f"You are running {APP_NAME} version {APP_VERSION}\n\nThis is the latest version.")
        self.update_status("Checked for updates")
    
    def show_user_guide(self):
        """Show user guide"""
        webbrowser.open("https://your-website.com/user-guide")  # Replace with actual URL
        self.update_status("User guide opened")
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_window = ctk.CTkToplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x300")
        shortcuts_window.transient(self.root)
        
        shortcuts_text = """
Keyboard Shortcuts:

File Operations:
• Ctrl+S - Save Results
• Ctrl+O - Load Session
• Ctrl+N - New Session
• Ctrl+Q - Quit

Edit Operations:
• Ctrl+C - Copy Results
• Ctrl+Z - Undo Last
• Delete - Clear Output

View:
• F11 - Toggle Fullscreen
• Ctrl+T - Toggle Theme

Help:
• F1 - Show Help
        """
        
        text_widget = ctk.CTkTextbox(shortcuts_window, width=380, height=260)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert("1.0", shortcuts_text)
        text_widget.configure(state="disabled")
    
    def report_bug(self):
        """Report a bug"""
        webbrowser.open("mailto:support@your-company.com?subject=Bug Report - MathPro Calculator")  # Replace with actual email
        self.update_status("Bug report email opened")
    
    def contact_support(self):
        """Contact support"""
        webbrowser.open("mailto:support@your-company.com?subject=Support Request - MathPro Calculator")  # Replace with actual email
        self.update_status("Support email opened")
    
    def schedule_auto_save(self):
        """Schedule auto-save every 5 minutes"""
        if self.auto_save_enabled:
            self.auto_save()
        self.root.after(300000, self.schedule_auto_save)  # 5 minutes
    
    def auto_save(self):
        """Auto-save session"""
        try:
            auto_save_file = self.user_data_dir / "auto_save.json"
            content = self.output_text.get("1.0", "end-1c")
            if content.strip():
                session_data = {
                    'timestamp': datetime.now().isoformat(),
                    'calculations': content,
                    'theme': ctk.get_appearance_mode()
                }
                with open(auto_save_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silent fail for auto-save
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit? Unsaved work will be lost."):
            self.auto_save()  # Final auto-save
            self.root.destroy()
    
    def save_session(self):
        """Save current session"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            session_data = {
                "functions": [func for func, _ in self.graph_functions],
                "output": self.output_text.get("1.0", "end-1c")
            }
            
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            self.log_output(f"💾 Session saved to {filename}")
    
    def load_session(self):
        """Load saved session"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    session_data = json.load(f)
                
                # Clear current session
                self.clear_graph()
                self.clear_output()
                
                # Load functions
                for func_str in session_data.get("functions", []):
                    self.function_entry.delete(0, "end")
                    self.function_entry.insert(0, func_str)
                    self.plot_function()
                
                # Load output
                output = session_data.get("output", "")
                self.output_text.insert("1.0", output)
                
                self.log_output(f"📁 Session loaded from {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error loading session: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title(f"About {APP_NAME}")
        about_window.geometry("500x400")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Logo/Icon area
        logo_frame = ctk.CTkFrame(about_window)
        logo_frame.pack(pady=20, padx=20, fill="x")
        
        app_title = ctk.CTkLabel(
            logo_frame, 
            text=APP_NAME, 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        app_title.pack(pady=10)
        
        version_label = ctk.CTkLabel(
            logo_frame, 
            text=f"Version {APP_VERSION}", 
            font=ctk.CTkFont(size=14)
        )
        version_label.pack()
        
        # About text
        about_text = f"""
{APP_COPYRIGHT}

A professional mathematical calculator with advanced 
graphing capabilities, symbolic computation, and 
comprehensive mathematical functions.

Features:
• Advanced mathematical calculations
• Interactive function graphing
• Symbolic mathematics with SymPy
• Export capabilities (PDF, PNG, SVG)
• Session management
• Commercial-grade interface

Built with Python, CustomTkinter, and Matplotlib.

License: {APP_LICENSE}

For support, visit: support@your-company.com
Website: https://your-website.com
        """
        
        text_widget = ctk.CTkTextbox(about_window, height=200)
        text_widget.pack(pady=10, padx=20, fill="both", expand=True)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")
        
        # Buttons
        button_frame = ctk.CTkFrame(about_window)
        button_frame.pack(pady=10, padx=20, fill="x")
        
        website_btn = ctk.CTkButton(
            button_frame, 
            text="Visit Website", 
            command=lambda: webbrowser.open("https://your-website.com")
        )
        website_btn.pack(side="left", padx=5)
        
        ok_button = ctk.CTkButton(button_frame, text="OK", command=about_window.destroy)
        ok_button.pack(side="right", padx=5)
    
    def save_as_pdf(self, filename, content):
        """Save results as PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create custom style for monospace content
            mono_style = ParagraphStyle(
                'MonoStyle',
                parent=styles['Normal'],
                fontName='Courier',
                fontSize=10,
                spaceAfter=6,
                leftIndent=0.25*inch
            )
            
            # Create title style
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=0.3*inch,
                textColor=colors.darkblue
            )
            
            # Build PDF content
            story = []
            
            # Add title
            story.append(Paragraph("ProMath Calculator - Calculation Results", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Add timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"Generated on: {timestamp}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Add content
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    # Escape HTML characters and preserve formatting
                    escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(escaped_line, mono_style))
                else:
                    story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            
        except ImportError:
            messagebox.showerror("Error", 
                "PDF export requires reportlab library.\n"
                "Please install it with: pip install reportlab\n"
                "Saving as text file instead.")
            # Fallback to text file
            txt_filename = filename.replace('.pdf', '.txt')
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating PDF: {str(e)}")
            # Fallback to text file
            txt_filename = filename.replace('.pdf', '.txt')
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(content)
    
    # Utility functions
    def log_output(self, message):
        """Add message to output text area"""
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.root.update()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete("1.0", "end")
    
    def get_float_input(self, prompt):
        """Get float input from user via modern dialog"""
        dialog = ctk.CTkInputDialog(text=prompt, title="Input Required")
        result = dialog.get_input()
        if result is None or result.strip() == "":
            return None
        try:
            if '.' in result:
                return float(result)
            else:
                return float(result)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return self.get_float_input(prompt)
    
    def get_int_input(self, prompt):
        """Get integer input from user via modern dialog with validation"""
        dialog = ctk.CTkInputDialog(text=prompt, title="Input Required")
        result = dialog.get_input()
        if result is None or result.strip() == "":
            return None
        try:
            float_val = float(result)
            if not float_val.is_integer():
                messagebox.showerror("Error", "Please enter a whole number (no decimals)")
                return self.get_int_input(prompt)
            return int(float_val)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid whole number")
            return self.get_int_input(prompt)
    
    def get_string_input(self, prompt):
        """Get string input from user via modern dialog"""
        dialog = ctk.CTkInputDialog(text=prompt, title="Input Required")
        result = dialog.get_input()
        return result if result is not None and result.strip() != "" else None
    
    # Mathematical operations (keeping all your original functions with improvements)
    def addition(self):
        a = self.get_float_input("Enter first number (decimals allowed):")
        if a is None: return
        b = self.get_float_input("Enter second number (decimals allowed):")
        if b is None: return
        c = a + b
        self.log_output(f"➕ Addition: {a} + {b} = {c}")
    
    def subtraction(self):
        a = self.get_float_input("Enter first number (decimals allowed):")
        if a is None: return
        b = self.get_float_input("Enter second number (decimals allowed):")
        if b is None: return
        c = a - b
        self.log_output(f"➖ Subtraction: {a} - {b} = {c}")
    
    def multiplication(self):
        a = self.get_float_input("Enter first number (decimals allowed):")
        if a is None: return
        b = self.get_float_input("Enter second number (decimals allowed):")
        if b is None: return
        c = a * b
        self.log_output(f"✖️ Multiplication: {a} × {b} = {c}")
    
    def division(self):
        a = self.get_float_input("Enter first number (decimals allowed):")
        if a is None: return
        b = self.get_float_input("Enter second number (decimals allowed):")
        if b is None: return
        if b == 0:
            messagebox.showerror("Error", "Division by zero is not allowed")
            return
        c = a / b
        self.log_output(f"➗ Division: {a} ÷ {b} = {c}")
    
    def power(self):
        a = self.get_float_input("Enter base (decimals allowed):")
        if a is None: return
        b = self.get_float_input("Enter exponent (decimals allowed):")
        if b is None: return
        c = math.pow(a, b)
        self.log_output(f"⚡ Power: {a}^{b} = {c}")
    
    def square_root(self):
        a = self.get_float_input("Enter number (decimals allowed):")
        if a is None: return
        if a < 0:
            messagebox.showerror("Error", "Cannot calculate square root of negative number")
            return
        b = math.sqrt(a)
        self.log_output(f"√ Square root: √{a} = {b}")
    
    def cbrt(self):
        a = self.get_float_input("Enter number (decimals allowed):")
        if a is None: return
        b = math.pow(a, 1/3)
        self.log_output(f"∛ Cube root: ∛{a} = {b}")
    
    def absolute_value(self):
        a = self.get_float_input("Enter number (decimals allowed):")
        if a is None: return
        b = abs(a)
        self.log_output(f"| | Absolute value: |{a}| = {b}")
    
    def natural_log(self):
        a = self.get_float_input("Enter number (must be positive, decimals allowed):")
        if a is None: return
        if a <= 0:
            messagebox.showerror("Error", "Natural logarithm is only defined for positive numbers")
            return
        b = math.log(a)
        self.log_output(f"ln Natural logarithm: ln({a}) = {b}")
    
    def log10(self):
        a = self.get_float_input("Enter number (must be positive, decimals allowed):")
        if a is None: return
        if a <= 0:
            messagebox.showerror("Error", "Logarithm is only defined for positive numbers")
            return
        b = math.log10(a)
        self.log_output(f"log₁₀ Base-10 logarithm: log₁₀({a}) = {b}")
    
    # Trigonometry
    def sine(self):
        a = self.get_float_input("Enter angle in radians (decimals allowed):")
        if a is None: return
        b = math.sin(a)
        self.log_output(f"sin({a}) = {b}")
    
    def cosine(self):
        a = self.get_float_input("Enter angle in radians (decimals allowed):")
        if a is None: return
        b = math.cos(a)
        self.log_output(f"cos({a}) = {b}")
    
    def tangent(self):
        a = self.get_float_input("Enter angle in radians (decimals allowed):")
        if a is None: return
        b = math.tan(a)
        self.log_output(f"tan({a}) = {b}")
    
    def arc_sine(self):
        a = self.get_float_input("Enter value between -1 and 1 (decimals allowed):")
        if a is None: return
        if not -1 <= a <= 1:
            messagebox.showerror("Error", "Value must be between -1 and 1")
            return
        b = math.asin(a)
        self.log_output(f"arcsin({a}) = {b} radians")
    
    def arc_cosine(self):
        a = self.get_float_input("Enter value between -1 and 1 (decimals allowed):")
        if a is None: return
        if not -1 <= a <= 1:
            messagebox.showerror("Error", "Value must be between -1 and 1")
            return
        b = math.acos(a)
        self.log_output(f"arccos({a}) = {b} radians")
    
    def arc_tangent(self):
        a = self.get_float_input("Enter value (decimals allowed):")
        if a is None: return
        b = math.atan(a)
        self.log_output(f"arctan({a}) = {b} radians")
    
    def degrees_to_radians(self):
        a = self.get_float_input("Enter angle in degrees (decimals allowed):")
        if a is None: return
        b = math.radians(a)
        self.log_output(f"{a}° = {b} radians")
    
    def radians_to_degrees(self):
        a = self.get_float_input("Enter angle in radians (decimals allowed):")
        if a is None: return
        b = math.degrees(a)
        self.log_output(f"{a} radians = {b}°")
    
    # Physics Formulas
    def density(self):
        missing = self.get_string_input("What is missing? (d, m, or v):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "d":
            m = self.get_float_input("Enter mass (m) - decimals allowed:")
            if m is None: return
            v = self.get_float_input("Enter volume (v) - decimals allowed:")
            if v is None: return
            if v == 0:
                messagebox.showerror("Error", "Volume cannot be zero")
                return
            d = m / v
            self.log_output(f"🏋️ Density: d = m/v = {m}/{v} = {d}")
        elif missing == "m":
            d = self.get_float_input("Enter density (d) - decimals allowed:")
            if d is None: return
            v = self.get_float_input("Enter volume (v) - decimals allowed:")
            if v is None: return
            m = d * v
            self.log_output(f"🏋️ Mass: m = d×v = {d}×{v} = {m}")
        elif missing == "v":
            m = self.get_float_input("Enter mass (m) - decimals allowed:")
            if m is None: return
            d = self.get_float_input("Enter density (d) - decimals allowed:")
            if d is None: return
            if d == 0:
                messagebox.showerror("Error", "Density cannot be zero")
                return
            v = m / d
            self.log_output(f"🏋️ Volume: v = m/d = {m}/{d} = {v}")
        else:
            messagebox.showerror("Error", "Please enter 'd', 'm', or 'v'")
    
    def weight(self):
        missing = self.get_string_input("What is missing? (w, m, or g):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "w":
            m = self.get_float_input("Enter mass (m) - decimals allowed:")
            if m is None: return
            g = 9.81
            w = m * g
            self.log_output(f"⚖️ Weight: w = m×g = {m}×{g} = {w} N")
        elif missing == "m":
            w = self.get_float_input("Enter weight (w) - decimals allowed:")
            if w is None: return
            g = 9.81
            m = w / g
            self.log_output(f"⚖️ Mass: m = w/g = {w}/{g} = {m} kg")
        elif missing == "g":
            self.log_output("⚖️ g = 9.81 m/s² (gravitational acceleration)")
        else:
            messagebox.showerror("Error", "Please enter 'w', 'm', or 'g'")
    
    def newtons_law(self):
        missing = self.get_string_input("What is missing? (F, m, or a):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "f":
            m = self.get_float_input("Enter mass (m) - decimals allowed:")
            if m is None: return
            a = self.get_float_input("Enter acceleration (a) - decimals allowed:")
            if a is None: return
            f = m * a
            self.log_output(f"🚀 Force: F = m×a = {m}×{a} = {f} N")
        elif missing == "m":
            f = self.get_float_input("Enter force (F) - decimals allowed:")
            if f is None: return
            a = self.get_float_input("Enter acceleration (a) - decimals allowed:")
            if a is None: return
            if a == 0:
                messagebox.showerror("Error", "Acceleration cannot be zero")
                return
            m = f / a
            self.log_output(f"🚀 Mass: m = F/a = {f}/{a} = {m} kg")
        elif missing == "a":
            f = self.get_float_input("Enter force (F) - decimals allowed:")
            if f is None: return
            m = self.get_float_input("Enter mass (m) - decimals allowed:")
            if m is None: return
            if m == 0:
                messagebox.showerror("Error", "Mass cannot be zero")
                return
            a = f / m
            self.log_output(f"🚀 Acceleration: a = F/m = {f}/{m} = {a} m/s²")
        else:
            messagebox.showerror("Error", "Please enter 'F', 'm', or 'a'")
    
    def pythagorean_theorem(self):
        missing = self.get_string_input("What is missing? (a, b, or c):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "a":
            b = self.get_float_input("Enter side b (decimals allowed):")
            if b is None: return
            c = self.get_float_input("Enter hypotenuse c (decimals allowed):")
            if c is None: return
            if c <= b:
                messagebox.showerror("Error", "Hypotenuse must be the longest side")
                return
            a = math.sqrt(c**2 - b**2)
            self.log_output(f"📏 Side a: a = √(c²-b²) = √({c}²-{b}²) = {a}")
        elif missing == "b":
            a = self.get_float_input("Enter side a (decimals allowed):")
            if a is None: return
            c = self.get_float_input("Enter hypotenuse c (decimals allowed):")
            if c is None: return
            if c <= a:
                messagebox.showerror("Error", "Hypotenuse must be the longest side")
                return
            b = math.sqrt(c**2 - a**2)
            self.log_output(f"📏 Side b: b = √(c²-a²) = √({c}²-{a}²) = {b}")
        elif missing == "c":
            a = self.get_float_input("Enter side a (decimals allowed):")
            if a is None: return
            b = self.get_float_input("Enter side b (decimals allowed):")
            if b is None: return
            c = math.sqrt(a**2 + b**2)
            self.log_output(f"📏 Hypotenuse c: c = √(a²+b²) = √({a}²+{b}²) = {c}")
        else:
            messagebox.showerror("Error", "Please enter 'a', 'b', or 'c'")
    
    # Advanced Math
    def factorial(self):
        n = self.get_int_input("Enter a whole number (no decimals):")
        if n is None: return
        if n < 0:
            messagebox.showerror("Error", "Factorial is not defined for negative numbers")
            return
        try:
            result = math.factorial(n)
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Error", f"Error calculating factorial: {e}")
            return
        self.log_output(f"! Factorial: {n}! = {result}")
    
    def comb(self):
        n = self.get_int_input("Enter n (whole number, no decimals):")
        if n is None: return
        if n < 0:
            messagebox.showerror("Error", "n must be a non-negative integer")
            return
        k = self.get_int_input("Enter k (whole number, no decimals):")
        if k is None: return
        if k < 0:
            messagebox.showerror("Error", "k must be a non-negative integer")
            return
        if k > n:
            messagebox.showerror("Error", "k must be less than or equal to n")
            return
        try:
            result = safe_comb(n, k)
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Error", f"Error calculating combination: {e}")
            return
        self.log_output(f"C Combination: C({n},{k}) = {result}")
    
    def permutation(self):
        n = self.get_int_input("Enter n (whole number, no decimals):")
        if n is None: return
        if n < 0:
            messagebox.showerror("Error", "n must be a non-negative integer")
            return
        k = self.get_int_input("Enter k (whole number, no decimals):")
        if k is None: return
        if k < 0:
            messagebox.showerror("Error", "k must be a non-negative integer")
            return
        if k > n:
            messagebox.showerror("Error", "k must be less than or equal to n")
            return
        try:
            result = math.factorial(n) // math.factorial(n - k)
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Error", f"Error calculating permutation: {e}")
            return
        self.log_output(f"P Permutation: P({n},{k}) = {result}")
    
    def gamma(self):
        a = self.get_float_input("Enter value (decimals allowed):")
        if a is None: return
        try:
            result = math.gamma(a)
            self.log_output(f"Γ Gamma function: Γ({a}) = {result}")
        except (ValueError, OverflowError) as e:
            messagebox.showerror("Error", f"Invalid input for gamma function: {e}")
    
    def equation(self):
        eq = self.get_string_input("Enter equation to solve (e.g., 'x**2 = 4' or '2*x + 3 - 7'):")
        if eq is None: return
        try:
            if '=' in eq:
                parts = eq.split('=', 1)
                if len(parts) != 2:
                    messagebox.showerror("Error", "Invalid equation format")
                    return
                lhs_str, rhs_str = parts[0].strip(), parts[1].strip()
                
                lhs = sympify(lhs_str)
                rhs = sympify(rhs_str)
                
                equation = Eq(lhs, rhs)
                sol = solve(equation, x)
                self.log_output(f"= Solution of '{eq}': {sol}")
            else:
                expr = sympify(eq)
                sol = solve(expr, x)
                self.log_output(f"= Solution of '{eq} = 0': {sol}")
        except (SympifyError, ValueError, TypeError, SyntaxError) as e:
            messagebox.showerror("Error", f"Error solving equation: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error solving equation: {e}")
    
    def symbolic_derivative(self):
        expr = self.get_string_input("Enter function to derive (e.g., 'x**2 + sin(x)'):")
        if expr is None: return
        try:
            expression = sympify(expr)
            d = diff(expression, x)
            self.log_output(f"d/dx Derivative of '{expr}': {d}")
        except (SympifyError, ValueError, TypeError, SyntaxError) as e:
            messagebox.showerror("Error", f"Error computing derivative: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error computing derivative: {e}")
    
    def symbolic_integral(self):
        expr = self.get_string_input("Enter function to integrate (e.g., 'x**2'):")
        if expr is None: return
        try:
            expression = sympify(expr)
            i = integrate(expression, x)
            self.log_output(f"∫ Integral of '{expr}': {i}")
        except (SympifyError, ValueError, TypeError, SyntaxError) as e:
            messagebox.showerror("Error", f"Error computing integral: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error computing integral: {e}")
    
    def symbolic_simplify(self):
        expr = self.get_string_input("Enter expression to simplify (e.g., '(x**2 - 1)/(x - 1)'):")
        if expr is None: return
        try:
            expression = sympify(expr)
            s = simplify(expression)
            self.log_output(f"≡ Simplified '{expr}': {s}")
        except (SympifyError, ValueError, TypeError, SyntaxError) as e:
            messagebox.showerror("Error", f"Error simplifying expression: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error simplifying expression: {e}")
    
    def symbolic_limit(self):
        from sympy import limit, oo
        expr = self.get_string_input("Enter function (e.g., 'sin(x)/x'):")
        if expr is None: return
        
        limit_point = self.get_string_input("Enter limit point (e.g., '0', 'oo' for infinity):")
        if limit_point is None: return
        
        try:
            expression = sympify(expr)
            if limit_point.lower() == 'oo' or limit_point == '∞':
                point = oo
            else:
                point = sympify(limit_point)
            
            result = limit(expression, x, point)
            self.log_output(f"lim Limit of '{expr}' as x→{limit_point}: {result}")
        except (SympifyError, ValueError, TypeError, SyntaxError) as e:
            messagebox.showerror("Error", f"Error computing limit: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error computing limit: {e}")
    
    # Geometry
    def circumference_of_circle(self):
        radius = self.get_float_input("Enter radius (decimals allowed):")
        if radius is None: return
        if radius < 0:
            messagebox.showerror("Error", "Radius cannot be negative")
            return
        circumference = 2 * math.pi * radius
        self.log_output(f"⭕ Circumference: C = 2πr = 2×π×{radius} = {circumference}")
    
    def area(self):
        radius = self.get_float_input("Enter radius (decimals allowed):")
        if radius is None: return
        if radius < 0:
            messagebox.showerror("Error", "Radius cannot be negative")
            return
        area = math.pi * radius ** 2
        self.log_output(f"🔵 Area: A = πr² = π×{radius}² = {area}")
    
    def triangle_area(self):
        base = self.get_float_input("Enter base (decimals allowed):")
        if base is None: return
        if base < 0:
            messagebox.showerror("Error", "Base cannot be negative")
            return
        height = self.get_float_input("Enter height (decimals allowed):")
        if height is None: return
        if height < 0:
            messagebox.showerror("Error", "Height cannot be negative")
            return
        area = 0.5 * base * height
        self.log_output(f"📐 Triangle Area: A = ½×b×h = ½×{base}×{height} = {area}")
    
    def rectangle_area(self):
        length = self.get_float_input("Enter length (decimals allowed):")
        if length is None: return
        if length < 0:
            messagebox.showerror("Error", "Length cannot be negative")
            return
        width = self.get_float_input("Enter width (decimals allowed):")
        if width is None: return
        if width < 0:
            messagebox.showerror("Error", "Width cannot be negative")
            return
        area = length * width
        self.log_output(f"▭ Rectangle Area: A = l×w = {length}×{width} = {area}")
    
    # Constants
    def pi(self):
        self.log_output(f"π = {math.pi}")
    
    def e(self):
        self.log_output(f"e = {math.e}")
    
    def tau(self):
        self.log_output(f"τ = {math.tau}")
    
    # Finance
    def calculate_roi(self):
        try:
            gain = self.get_float_input("Enter total gain from investment (decimals allowed):")
            if gain is None: return
            cost = self.get_float_input("Enter total cost of investment (decimals allowed):")
            if cost is None: return
            
            if cost == 0:
                messagebox.showerror("Error", "Cost of investment cannot be zero")
                return
            
            roi = ((gain - cost) / cost) * 100
            self.log_output(f"📈 ROI = ((gain - cost) / cost) × 100 = (({gain} - {cost}) / {cost}) × 100 = {roi:.2f}%")
        except (ValueError, TypeError, ZeroDivisionError) as e:
            messagebox.showerror("Error", f"Error calculating ROI: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error calculating ROI: {e}")
    
    def simple_interest(self):
        principal = self.get_float_input("Enter principal amount (decimals allowed):")
        if principal is None: return
        rate = self.get_float_input("Enter interest rate as percentage (decimals allowed):")
        if rate is None: return
        time = self.get_float_input("Enter time period (decimals allowed):")
        if time is None: return
        
        interest = (principal * rate * time) / 100
        self.log_output(f"💵 Simple Interest: I = PRT/100 = {principal}×{rate}×{time}/100 = {interest}")
    
    def compound_interest(self):
        principal = self.get_float_input("Enter principal amount (decimals allowed):")
        if principal is None: return
        rate = self.get_float_input("Enter interest rate as percentage (decimals allowed):")
        if rate is None: return
        time = self.get_float_input("Enter time period (decimals allowed):")
        if time is None: return
        n = self.get_int_input("Enter number of times interest is compounded per year (whole number):")
        if n is None: return
        
        amount = principal * math.pow(1 + (rate / 100) / n, n * time)
        interest = amount - principal
        self.log_output(f"🏦 Compound Interest: A = P(1 + r/n)^(nt) = {amount:.2f}")
        self.log_output(f"Interest earned: {interest:.2f}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = CommercialMathCalculator()
    app.run()

if __name__ == "__main__":
    main()