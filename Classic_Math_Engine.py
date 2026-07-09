import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from sympy import symbols, solve, diff, integrate, simplify, sympify
import threading

x = symbols('x')

class MathCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Mathematical Calculator")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced Mathematical Calculator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel for buttons
        button_frame = ttk.LabelFrame(main_frame, text="Operations", padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Right panel for input/output
        io_frame = ttk.LabelFrame(main_frame, text="Input/Output", padding="10")
        io_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        io_frame.columnconfigure(0, weight=1)
        io_frame.rowconfigure(1, weight=1)
        
        # Create scrollable button area
        canvas = tk.Canvas(button_frame, bg='white')
        scrollbar = ttk.Scrollbar(button_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(io_frame, height=20, width=50, 
                                                    font=('Consolas', 10))
        self.output_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Clear output button
        clear_btn = ttk.Button(io_frame, text="Clear Output", command=self.clear_output)
        clear_btn.grid(row=2, column=0, pady=(0, 10))
        
        # Create operation buttons
        self.create_buttons(scrollable_frame)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def create_buttons(self, parent):
        """Create all operation buttons"""
        operations = [
            ("Basic Operations", [
                ("Addition", self.addition),
                ("Subtraction", self.subtraction),
                ("Multiplication", self.multiplication),
                ("Division", self.division),
                ("Power", self.power),
                ("Square Root", self.square_root),
                ("Cube Root", self.cbrt),
                ("Absolute Value", self.absolute_value),
            ]),
            ("Trigonometry", [
                ("Sine", self.sine),
                ("Cosine", self.cosine),
                ("Tangent", self.tangent),
                ("Arc Sine", self.arc_sine),
                ("Arc Cosine", self.arc_cosine),
                ("Arc Tangent", self.arc_tangent),
                ("Arc Tangent2", self.arc_tangent2),
                ("Degrees to Radians", self.degrees_to_radians),
                ("Radians to Degrees", self.radians_to_degrees),
            ]),
            ("Physics Formulas", [
                ("Density (d=m/v)", self.density),
                ("Weight (w=mg)", self.weight),
                ("Newton's Law (F=ma)", self.newtons_law),
                ("Gravitational PE", self.gravitational_potential_energy),
                ("Pythagorean Theorem", self.pythagorean_theorem),
            ]),
            ("Advanced Math", [
                ("Factorial", self.factorial),
                ("Combination", self.comb),
                ("Gamma Function", self.gamma),
                ("Error Function", self.erf),
                ("Complementary Error Function", self.erfc),
                ("Solve Equation", self.equation),
                ("Derivative", self.symbolic_derivative),
                ("Integral", self.symbolic_integral),
                ("Simplify Expression", self.symbolic_simplify),
            ]),
            ("Geometry", [
                ("Circle Circumference", self.circumference_of_circle),
                ("Circle Area", self.area),
            ]),
            ("Constants", [
                ("Pi (π)", self.pi),
                ("Euler's number (e)", self.e),
                ("Tau (τ)", self.tau),
            ]),
            ("Finance", [
                ("ROI Calculator", self.calculate_roi),
            ])
        ]
        
        row = 0
        for category, ops in operations:
            # Category header
            header = ttk.Label(parent, text=category, font=('Arial', 11, 'bold'))
            header.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
            row += 1
            
            # Operation buttons
            col = 0
            for op_name, op_func in ops:
                btn = ttk.Button(parent, text=op_name, command=op_func, width=20)
                btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.W+tk.E)
                col += 1
                if col > 1:
                    col = 0
                    row += 1
            
            if col == 1:  # If odd number of buttons, move to next row
                row += 1
    
    def log_output(self, message):
        """Add message to output text area"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
    
    def get_float_input(self, prompt):
        """Get float input from user via dialog"""
        while True:
            try:
                result = tk.simpledialog.askfloat("Input Required", prompt)
                if result is None:  # User cancelled
                    return None
                return result
            except:
                messagebox.showerror("Error", "Please enter a valid number")
    
    def get_int_input(self, prompt):
        """Get integer input from user via dialog"""
        while True:
            try:
                result = tk.simpledialog.askinteger("Input Required", prompt)
                if result is None:  # User cancelled
                    return None
                return result
            except:
                messagebox.showerror("Error", "Please enter a valid integer")
    
    def get_string_input(self, prompt):
        """Get string input from user via dialog"""
        result = tk.simpledialog.askstring("Input Required", prompt)
        return result
    
    # Basic Operations
    def addition(self):
        a = self.get_float_input("Enter first number:")
        if a is None: return
        b = self.get_float_input("Enter second number:")
        if b is None: return
        c = a + b
        self.log_output(f"Addition: {a} + {b} = {c}")
    
    def subtraction(self):
        a = self.get_float_input("Enter first number:")
        if a is None: return
        b = self.get_float_input("Enter second number:")
        if b is None: return
        c = a - b
        self.log_output(f"Subtraction: {a} - {b} = {c}")
    
    def multiplication(self):
        a = self.get_float_input("Enter first number:")
        if a is None: return
        b = self.get_float_input("Enter second number:")
        if b is None: return
        c = a * b
        self.log_output(f"Multiplication: {a} × {b} = {c}")
    
    def division(self):
        a = self.get_float_input("Enter first number:")
        if a is None: return
        b = self.get_float_input("Enter second number:")
        if b is None: return
        if b == 0:
            messagebox.showerror("Error", "Division by zero is not allowed")
            return
        c = a / b
        self.log_output(f"Division: {a} ÷ {b} = {c}")
    
    def power(self):
        a = self.get_float_input("Enter base:")
        if a is None: return
        b = self.get_float_input("Enter exponent:")
        if b is None: return
        c = math.pow(a, b)
        self.log_output(f"Power: {a}^{b} = {c}")
    
    def square_root(self):
        a = self.get_float_input("Enter number:")
        if a is None: return
        if a < 0:
            messagebox.showerror("Error", "Cannot calculate square root of negative number")
            return
        b = math.sqrt(a)
        self.log_output(f"Square root: √{a} = {b}")
    
    def cbrt(self):
        a = self.get_float_input("Enter number:")
        if a is None: return
        b = math.pow(a, 1/3)
        self.log_output(f"Cube root: ∛{a} = {b}")
    
    def absolute_value(self):
        a = self.get_float_input("Enter number:")
        if a is None: return
        b = abs(a)
        self.log_output(f"Absolute value: |{a}| = {b}")
    
    # Trigonometry
    def sine(self):
        a = self.get_float_input("Enter angle in radians:")
        if a is None: return
        b = math.sin(a)
        self.log_output(f"sin({a}) = {b}")
    
    def cosine(self):
        a = self.get_float_input("Enter angle in radians:")
        if a is None: return
        b = math.cos(a)
        self.log_output(f"cos({a}) = {b}")
    
    def tangent(self):
        a = self.get_float_input("Enter angle in radians:")
        if a is None: return
        b = math.tan(a)
        self.log_output(f"tan({a}) = {b}")
    
    def arc_sine(self):
        a = self.get_float_input("Enter value (between -1 and 1):")
        if a is None: return
        if not -1 <= a <= 1:
            messagebox.showerror("Error", "Value must be between -1 and 1")
            return
        b = math.asin(a)
        self.log_output(f"arcsin({a}) = {b} radians")
    
    def arc_cosine(self):
        a = self.get_float_input("Enter value (between -1 and 1):")
        if a is None: return
        if not -1 <= a <= 1:
            messagebox.showerror("Error", "Value must be between -1 and 1")
            return
        b = math.acos(a)
        self.log_output(f"arccos({a}) = {b} radians")
    
    def arc_tangent(self):
        a = self.get_float_input("Enter value:")
        if a is None: return
        b = math.atan(a)
        self.log_output(f"arctan({a}) = {b} radians")
    
    def arc_tangent2(self):
        y = self.get_float_input("Enter y:")
        if y is None: return
        x = self.get_float_input("Enter x:")
        if x is None: return
        b = math.atan2(y, x)
        self.log_output(f"atan2({y}, {x}) = {b} radians")
    
    def degrees_to_radians(self):
        a = self.get_float_input("Enter angle in degrees:")
        if a is None: return
        b = math.radians(a)
        self.log_output(f"{a}° = {b} radians")
    
    def radians_to_degrees(self):
        a = self.get_float_input("Enter angle in radians:")
        if a is None: return
        b = math.degrees(a)
        self.log_output(f"{a} radians = {b}°")
    
    # Physics Formulas
    def density(self):
        missing = self.get_string_input("What is missing? (d, m, or v):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "d":
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            v = self.get_float_input("Enter volume (v):")
            if v is None: return
            if v == 0:
                messagebox.showerror("Error", "Volume cannot be zero")
                return
            d = m / v
            self.log_output(f"Density: d = m/v = {m}/{v} = {d}")
        elif missing == "m":
            d = self.get_float_input("Enter density (d):")
            if d is None: return
            v = self.get_float_input("Enter volume (v):")
            if v is None: return
            m = d * v
            self.log_output(f"Mass: m = d×v = {d}×{v} = {m}")
        elif missing == "v":
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            d = self.get_float_input("Enter density (d):")
            if d is None: return
            if d == 0:
                messagebox.showerror("Error", "Density cannot be zero")
                return
            v = m / d
            self.log_output(f"Volume: v = m/d = {m}/{d} = {v}")
        else:
            messagebox.showerror("Error", "Please enter 'd', 'm', or 'v'")
    
    def weight(self):
        missing = self.get_string_input("What is missing? (w, m, or g):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "w":
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            g = 9.81
            w = m * g
            self.log_output(f"Weight: w = m×g = {m}×{g} = {w} N")
        elif missing == "m":
            w = self.get_float_input("Enter weight (w):")
            if w is None: return
            g = 9.81
            m = w / g
            self.log_output(f"Mass: m = w/g = {w}/{g} = {m} kg")
        elif missing == "g":
            self.log_output("g = 9.81 m/s² (gravitational acceleration)")
        else:
            messagebox.showerror("Error", "Please enter 'w', 'm', or 'g'")
    
    def newtons_law(self):
        missing = self.get_string_input("What is missing? (F, m, or a):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "f":
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            a = self.get_float_input("Enter acceleration (a):")
            if a is None: return
            f = m * a
            self.log_output(f"Force: F = m×a = {m}×{a} = {f} N")
        elif missing == "m":
            f = self.get_float_input("Enter force (F):")
            if f is None: return
            a = self.get_float_input("Enter acceleration (a):")
            if a is None: return
            if a == 0:
                messagebox.showerror("Error", "Acceleration cannot be zero")
                return
            m = f / a
            self.log_output(f"Mass: m = F/a = {f}/{a} = {m} kg")
        elif missing == "a":
            f = self.get_float_input("Enter force (F):")
            if f is None: return
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            if m == 0:
                messagebox.showerror("Error", "Mass cannot be zero")
                return
            a = f / m
            self.log_output(f"Acceleration: a = F/m = {f}/{m} = {a} m/s²")
        else:
            messagebox.showerror("Error", "Please enter 'F', 'm', or 'a'")
    
    def gravitational_potential_energy(self):
        missing = self.get_string_input("What is missing? (U, m, h, or g):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "u":
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            h = self.get_float_input("Enter height (h):")
            if h is None: return
            g = 9.81
            u = m * g * h
            self.log_output(f"Gravitational PE: U = m×g×h = {m}×{g}×{h} = {u} J")
        elif missing == "m":
            u = self.get_float_input("Enter potential energy (U):")
            if u is None: return
            h = self.get_float_input("Enter height (h):")
            if h is None: return
            g = 9.81
            if h == 0:
                messagebox.showerror("Error", "Height cannot be zero")
                return
            m = u / (g * h)
            self.log_output(f"Mass: m = U/(g×h) = {u}/({g}×{h}) = {m} kg")
        elif missing == "h":
            u = self.get_float_input("Enter potential energy (U):")
            if u is None: return
            m = self.get_float_input("Enter mass (m):")
            if m is None: return
            g = 9.81
            if m == 0:
                messagebox.showerror("Error", "Mass cannot be zero")
                return
            h = u / (m * g)
            self.log_output(f"Height: h = U/(m×g) = {u}/({m}×{g}) = {h} m")
        elif missing == "g":
            self.log_output("g = 9.81 m/s² (gravitational acceleration)")
        else:
            messagebox.showerror("Error", "Please enter 'U', 'm', 'h', or 'g'")
    
    def pythagorean_theorem(self):
        missing = self.get_string_input("What is missing? (a, b, or c):")
        if missing is None: return
        missing = missing.lower()
        
        if missing == "a":
            b = self.get_float_input("Enter side b:")
            if b is None: return
            c = self.get_float_input("Enter hypotenuse c:")
            if c is None: return
            if c <= b:
                messagebox.showerror("Error", "Hypotenuse must be the longest side")
                return
            a = math.sqrt(c**2 - b**2)
            self.log_output(f"Side a: a = √(c²-b²) = √({c}²-{b}²) = {a}")
        elif missing == "b":
            a = self.get_float_input("Enter side a:")
            if a is None: return
            c = self.get_float_input("Enter hypotenuse c:")
            if c is None: return
            if c <= a:
                messagebox.showerror("Error", "Hypotenuse must be the longest side")
                return
            b = math.sqrt(c**2 - a**2)
            self.log_output(f"Side b: b = √(c²-a²) = √({c}²-{a}²) = {b}")
        elif missing == "c":
            a = self.get_float_input("Enter side a:")
            if a is None: return
            b = self.get_float_input("Enter side b:")
            if b is None: return
            c = math.sqrt(a**2 + b**2)
            self.log_output(f"Hypotenuse c: c = √(a²+b²) = √({a}²+{b}²) = {c}")
        else:
            messagebox.showerror("Error", "Please enter 'a', 'b', or 'c'")
    
    # Advanced Math
    def factorial(self):
        n = self.get_int_input("Enter integer n:")
        if n is None: return
        if n < 0:
            messagebox.showerror("Error", "Factorial is not defined for negative numbers")
            return
        result = math.factorial(n)
        self.log_output(f"Factorial: {n}! = {result}")
    
    def comb(self):
        n = self.get_int_input("Enter n:")
        if n is None: return
        k = self.get_int_input("Enter k:")
        if k is None: return
        if k > n or k < 0:
            messagebox.showerror("Error", "k must be between 0 and n")
            return
        result = math.comb(n, k)
        self.log_output(f"Combination: C({n},{k}) = {result}")
    
    def gamma(self):
        a = self.get_float_input("Enter value:")
        if a is None: return
        try:
            result = math.gamma(a)
            self.log_output(f"Gamma function: Γ({a}) = {result}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input for gamma function: {e}")
    
    def erf(self):
        a = self.get_float_input("Enter value:")
        if a is None: return
        result = math.erf(a)
        self.log_output(f"Error function: erf({a}) = {result}")
    
    def erfc(self):
        a = self.get_float_input("Enter value:")
        if a is None: return
        result = math.erfc(a)
        self.log_output(f"Complementary error function: erfc({a}) = {result}")
    
    def equation(self):
        eq = self.get_string_input("Enter equation to solve (e.g., 2*x + 3 - 7):")
        if eq is None: return
        try:
            sol = solve(eq, x)
            self.log_output(f"Solution of '{eq} = 0': {sol}")
        except Exception as e:
            messagebox.showerror("Error", f"Error solving equation: {e}")
    
    def symbolic_derivative(self):
        expr = self.get_string_input("Enter function to derive (e.g., x**2 + sin(x)):")
        if expr is None: return
        try:
            d = diff(sympify(expr), x)
            self.log_output(f"Derivative of '{expr}': {d}")
        except Exception as e:
            messagebox.showerror("Error", f"Error computing derivative: {e}")
    
    def symbolic_integral(self):
        expr = self.get_string_input("Enter function to integrate (e.g., x**2):")
        if expr is None: return
        try:
            i = integrate(sympify(expr), x)
            self.log_output(f"Integral of '{expr}': {i}")
        except Exception as e:
            messagebox.showerror("Error", f"Error computing integral: {e}")
    
    def symbolic_simplify(self):
        expr = self.get_string_input("Enter expression to simplify:")
        if expr is None: return
        try:
            s = simplify(sympify(expr))
            self.log_output(f"Simplified '{expr}': {s}")
        except Exception as e:
            messagebox.showerror("Error", f"Error simplifying expression: {e}")
    
    # Geometry
    def circumference_of_circle(self):
        radius = self.get_float_input("Enter radius:")
        if radius is None: return
        if radius < 0:
            messagebox.showerror("Error", "Radius cannot be negative")
            return
        circumference = 2 * math.pi * radius
        self.log_output(f"Circumference: C = 2πr = 2×π×{radius} = {circumference}")
    
    def area(self):
        radius = self.get_float_input("Enter radius:")
        if radius is None: return
        if radius < 0:
            messagebox.showerror("Error", "Radius cannot be negative")
            return
        area = math.pi * radius ** 2  # Fixed the operator from ^ to **
        self.log_output(f"Area: A = πr² = π×{radius}² = {area}")
    
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
            gain = self.get_float_input("Enter total gain from investment:")
            if gain is None: return
            cost = self.get_float_input("Enter total cost of investment:")
            if cost is None: return
            
            if cost == 0:
                messagebox.showerror("Error", "Cost of investment cannot be zero")
                return
            
            roi = ((gain - cost) / cost) * 100
            self.log_output(f"ROI = ((gain - cost) / cost) × 100 = (({gain} - {cost}) / {cost}) × 100 = {roi:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating ROI: {e}")

# Import simpledialog after creating the class
import tkinter.simpledialog

def main():
    root = tk.Tk()
    app = MathCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()