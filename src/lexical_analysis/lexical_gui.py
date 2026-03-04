"""
Visual Interface for Lexical Analysis Phase

This module provides a comprehensive GUI for visualizing the lexical analysis process
with step-by-step token generation, syntax highlighting, and real-time feedback.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import sys
from pathlib import Path
from typing import List, Optional
import threading
import time

from .lexer import VisualLexicalAnalyzer
from .tokens import Token, TokenType, LexicalError


class LexicalAnalysisGUI:
    """
    Visual Interface for Lexical Analysis Phase
    
    Features:
    - Real-time syntax highlighting
    - Step-by-step token generation
    - Token table with detailed information
    - Error recovery interface
    - Animation controls
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Visual Compiler - Lexical Analysis Phase")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Analysis state
        self.analyzer = VisualLexicalAnalyzer(visual_mode=True)
        self.tokens = []
        self.errors = []
        self.current_token_index = 0
        self.is_analyzing = False
        self.step_mode = True
        
        # Visual elements
        self.setup_ui()
        self.setup_syntax_highlighting()
        
        # Set callbacks
        self.analyzer.set_visual_callback(self.on_token_found)
        self.analyzer.set_error_callback(self.on_error_found)
        
    def setup_ui(self):
        """Setup the main user interface."""
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🔍 LEXICAL ANALYSIS PHASE",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab 1: Source Code Editor
        self.setup_editor_tab()
        
        # Tab 2: Token Visualization
        self.setup_token_tab()
        
        # Tab 3: Analysis Results
        self.setup_results_tab()
        
        # Control Panel
        self.setup_control_panel(main_frame)
        
    def setup_editor_tab(self):
        """Setup the source code editor tab."""
        
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="📝 Source Code Editor")
        
        # Toolbar
        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(toolbar, text="📁 Load File", command=self.load_file).pack(side='left', padx=5)
        ttk.Button(toolbar, text="💾 Save File", command=self.save_file).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🗑️ Clear", command=self.clear_editor).pack(side='left', padx=5)
        ttk.Button(toolbar, text="📝 Sample Code", command=self.load_sample).pack(side='left', padx=5)
        
        # Source code editor
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Line numbers frame
        line_frame = ttk.Frame(editor_container)
        line_frame.pack(side='left', fill='y')
        
        self.line_numbers = tk.Text(
            line_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            state='disabled',
            wrap='none',
            font=('Consolas', 12),
            background='#404040',
            foreground='#888888'
        )
        self.line_numbers.pack(side='left', fill='y')
        
        # Source code text area
        self.source_text = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.WORD,
            font=('Consolas', 12),
            background='#1e1e1e',
            foreground='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#404040'
        )
        self.source_text.pack(side='left', fill='both', expand=True)
        self.source_text.bind('<KeyRelease>', self.update_line_numbers)
        self.source_text.bind('<Button-1>', self.update_line_numbers)
        self.source_text.bind('<MouseWheel>', self.update_line_numbers)
        
        # Initialize with sample code
        self.load_sample()
        
    def setup_token_tab(self):
        """Setup the token visualization tab."""
        
        token_frame = ttk.Frame(self.notebook)
        self.notebook.add(token_frame, text="🏷️ Token Visualization")
        
        # Token display area
        display_frame = ttk.LabelFrame(token_frame, text="Current Token Analysis")
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Current token info
        info_frame = ttk.Frame(display_frame)
        info_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(info_frame, text="Current Token:", font=('Arial', 12, 'bold')).pack(anchor='w')
        self.current_token_label = tk.Label(
            info_frame, 
            text="No token selected",
            font=('Consolas', 11),
            bg='#f0f0f0',
            relief='sunken',
            anchor='w'
        )
        self.current_token_label.pack(fill='x', pady=5)
        
        # Token table
        table_frame = ttk.LabelFrame(display_frame, text="Token Stream")
        table_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview for tokens
        columns = ('Index', 'Type', 'Lexeme', 'Value', 'Line', 'Column')
        self.token_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.token_tree.heading(col, text=col)
            self.token_tree.column(col, width=100)
            
        # Scrollbar for token table
        token_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=token_scrollbar.set)
        
        self.token_tree.pack(side='left', fill='both', expand=True)
        token_scrollbar.pack(side='right', fill='y')
        
        # Bind selection
        self.token_tree.bind('<<TreeviewSelect>>', self.on_token_select)
        
    def setup_results_tab(self):
        """Setup the analysis results tab."""
        
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Analysis Results")
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(results_frame, text="Analysis Statistics")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.stats_text = tk.Text(
            stats_frame,
            height=8,
            font=('Consolas', 10),
            background='#f8f8f8',
            state='disabled'
        )
        self.stats_text.pack(fill='x', padx=5, pady=5)
        
        # Errors frame
        errors_frame = ttk.LabelFrame(results_frame, text="Lexical Errors")
        errors_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.error_tree = ttk.Treeview(
            errors_frame, 
            columns=('Line', 'Column', 'Error', 'Suggestion'), 
            show='headings'
        )
        
        for col in ['Line', 'Column', 'Error', 'Suggestion']:
            self.error_tree.heading(col, text=col)
            self.error_tree.column(col, width=150)
            
        error_scrollbar = ttk.Scrollbar(errors_frame, orient="vertical", command=self.error_tree.yview)
        self.error_tree.configure(yscrollcommand=error_scrollbar.set)
        
        self.error_tree.pack(side='left', fill='both', expand=True)
        error_scrollbar.pack(side='right', fill='y')
        
    def setup_control_panel(self, parent):
        """Setup the control panel."""
        
        control_frame = ttk.LabelFrame(parent, text="Analysis Controls")
        control_frame.pack(fill='x', pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.analyze_btn = ttk.Button(
            button_frame, 
            text="🚀 Start Analysis", 
            command=self.start_analysis
        )
        self.analyze_btn.pack(side='left', padx=5)
        
        self.step_btn = ttk.Button(
            button_frame, 
            text="👆 Step Forward", 
            command=self.step_forward,
            state='disabled'
        )
        self.step_btn.pack(side='left', padx=5)
        
        self.reset_btn = ttk.Button(
            button_frame, 
            text="🔄 Reset", 
            command=self.reset_analysis
        )
        self.reset_btn.pack(side='left', padx=5)
        
        # Animation controls
        anim_frame = ttk.Frame(control_frame)
        anim_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(anim_frame, text="Analysis Mode:").pack(side='left', padx=5)
        
        self.mode_var = tk.StringVar(value="step")
        ttk.Radiobutton(anim_frame, text="Step Mode", variable=self.mode_var, 
                       value="step").pack(side='left', padx=5)
        ttk.Radiobutton(anim_frame, text="Auto Mode", variable=self.mode_var, 
                       value="auto").pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(control_frame, mode='determinate')
        self.progress.pack(fill='x', padx=5, pady=5)
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Ready for lexical analysis",
            bg='#2b2b2b',
            fg='#ffffff'
        )
        self.status_label.pack(pady=5)
        
    def setup_syntax_highlighting(self):
        """Setup syntax highlighting tags."""
        
        # Configure text tags for syntax highlighting
        self.source_text.tag_configure("keyword", foreground="#569cd6")
        self.source_text.tag_configure("string", foreground="#ce9178")
        self.source_text.tag_configure("number", foreground="#b5cea8")
        self.source_text.tag_configure("comment", foreground="#6a9955")
        self.source_text.tag_configure("operator", foreground="#d4d4d4")
        self.source_text.tag_configure("current_token", background="#404040")
        
    def load_file(self):
        """Load source code from file."""
        filename = filedialog.askopenfilename(
            title="Select source file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, content)
                self.update_line_numbers()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
                
    def save_file(self):
        """Save source code to file."""
        filename = filedialog.asksaveasfilename(
            title="Save source file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                content = self.source_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                
    def clear_editor(self):
        """Clear the source code editor."""
        self.source_text.delete(1.0, tk.END)
        self.update_line_numbers()
        
    def load_sample(self):
        """Load sample code into the editor."""
        sample_code = '''// Sample Program in NEXUS Programming Language
hold x: num = 42;
hold message: text = "Hello, NEXUS Compiler!";
hold pi: decimal = 3.14159;
hold isActive: flag = yes;

// Function with security validation
func calculateArea(radius: decimal) -> decimal {
    secure validate(radius > 0);
    return pi * radius ^ 2;
}

// Conditional with logical operators
when (x >= 10 && isActive) {
    show message;
    hold result: decimal = calculateArea(5.0);
} otherwise {
    show "Conditions not met";
}

// Loop example
cycle (hold i: num = 0; i < 5; i += 1) {
    show "Iteration: " + toString(i);
}

// Switch statement example
hold dayNumber: num = 3;
choose (dayNumber) {
    option 1: {
        show "Monday";
        stop;
    }
    option 2: {
        show "Tuesday"; 
        stop;
    }
    option 3: {
        show "Wednesday";
        stop;
    }
    default: {
        show "Other day";
    }
}'''
        
        self.source_text.delete(1.0, tk.END)
        self.source_text.insert(1.0, sample_code)
        self.update_line_numbers()
        
    def update_line_numbers(self, event=None):
        """Update line numbers display."""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        
        content = self.source_text.get(1.0, tk.END)
        lines = content.split('\n')
        
        line_nums = ""
        for i in range(1, len(lines)):
            line_nums += f"{i}\n"
            
        self.line_numbers.insert(1.0, line_nums)
        self.line_numbers.config(state='disabled')
        
    def start_analysis(self):
        """Start the lexical analysis process."""
        if self.is_analyzing:
            return
            
        source_code = self.source_text.get(1.0, tk.END).strip()
        if not source_code:
            messagebox.showwarning("Warning", "Please enter source code to analyze!")
            return
            
        self.is_analyzing = True
        self.reset_analysis(keep_source=True)
        
        self.analyze_btn.config(state='disabled')
        self.step_btn.config(state='normal' if self.mode_var.get() == 'step' else 'disabled')
        
        self.status_label.config(text="Starting lexical analysis...")
        
        # Run analysis in separate thread to keep GUI responsive
        if self.mode_var.get() == 'auto':
            threading.Thread(target=self.run_auto_analysis, args=(source_code,), daemon=True).start()
        else:
            threading.Thread(target=self.run_step_analysis, args=(source_code,), daemon=True).start()
            
    def run_auto_analysis(self, source_code):
        """Run automatic analysis with animation."""
        try:
            self.tokens, self.errors = self.analyzer.analyze(source_code)
            self.root.after(0, self.analysis_complete)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Analysis failed: {str(e)}"))
            
    def run_step_analysis(self, source_code):
        """Prepare for step-by-step analysis."""
        # This will be handled by the step_forward method
        self.step_mode = True
        self.current_token_index = 0
        try:
            self.tokens, self.errors = self.analyzer.analyze(source_code)
            self.root.after(0, self.analysis_complete)
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Analysis failed: {str(e)}"))
            
    def step_forward(self):
        """Move to the next token in step mode."""
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.highlight_token(token)
            self.current_token_index += 1
            self.progress['value'] = (self.current_token_index / len(self.tokens)) * 100
            
            if self.current_token_index >= len(self.tokens):
                self.step_btn.config(state='disabled')
                self.status_label.config(text="Analysis complete!")
                
    def on_token_found(self, token: Token, state):
        """Callback when a new token is found."""
        self.root.after(0, lambda: self.add_token_to_table(token))
        
    def on_error_found(self, error: LexicalError) -> Optional[str]:
        """Callback when an error is found."""
        self.root.after(0, lambda: self.add_error_to_table(error))
        return None  # No automatic suggestions for now
        
    def add_token_to_table(self, token: Token):
        """Add a token to the visualization table."""
        self.token_tree.insert('', 'end', values=(
            len(self.token_tree.get_children()),
            token.token_type.name,
            token.lexeme,
            str(token.value),
            token.line,
            token.column
        ))
        
    def add_error_to_table(self, error: LexicalError):
        """Add an error to the error table."""
        self.error_tree.insert('', 'end', values=(
            error.line,
            error.column,
            error.message,
            "Manual correction needed"
        ))
        
    def on_token_select(self, event):
        """Handle token selection in the table."""
        selection = self.token_tree.selection()
        if selection:
            item = self.token_tree.item(selection[0])
            values = item['values']
            if values:
                token_info = f"Type: {values[1]} | Lexeme: '{values[2]}' | Value: {values[3]} | Position: Line {values[4]}, Column {values[5]}"
                self.current_token_label.config(text=token_info)
                
    def highlight_token(self, token: Token):
        """Highlight the current token in the source code."""
        # Clear previous highlights
        self.source_text.tag_remove("current_token", 1.0, tk.END)
        
        # Calculate position
        start_pos = f"{token.line}.{token.column-1}"
        end_pos = f"{token.line}.{token.column-1+token.length}"
        
        # Highlight current token
        self.source_text.tag_add("current_token", start_pos, end_pos)
        self.source_text.see(start_pos)
        
    def analysis_complete(self):
        """Handle completion of analysis."""
        self.is_analyzing = False
        self.analyze_btn.config(state='normal')
        self.step_btn.config(state='disabled')
        
        self.update_statistics()
        self.status_label.config(text=f"Analysis complete! Found {len(self.tokens)} tokens, {len(self.errors)} errors.")
        
    def update_statistics(self):
        """Update the statistics display."""
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        # Calculate token statistics
        token_counts = {}
        for token in self.tokens:
            token_type = token.token_type.name
            token_counts[token_type] = token_counts.get(token_type, 0) + 1
            
        stats = f"📊 LEXICAL ANALYSIS STATISTICS\n"
        stats += "=" * 40 + "\n"
        stats += f"Total Tokens: {len(self.tokens)}\n"
        stats += f"Lexical Errors: {len(self.errors)}\n"
        stats += f"Lines Processed: {max([t.line for t in self.tokens]) if self.tokens else 0}\n\n"
        
        stats += "Token Distribution:\n"
        for token_type, count in sorted(token_counts.items()):
            stats += f"  {token_type}: {count}\n"
            
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state='disabled')
        
    def reset_analysis(self, keep_source=False):
        """Reset the analysis state."""
        self.is_analyzing = False
        self.tokens = []
        self.errors = []
        self.current_token_index = 0
        
        # Clear tables
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
            
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
            
        # Reset UI
        self.progress['value'] = 0
        self.current_token_label.config(text="No token selected")
        self.status_label.config(text="Ready for lexical analysis")
        
        self.analyze_btn.config(state='normal')
        self.step_btn.config(state='disabled')
        
        # Clear highlights
        self.source_text.tag_remove("current_token", 1.0, tk.END)
        
        if not keep_source:
            self.stats_text.config(state='normal')
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.config(state='disabled')
            
    def show_error(self, message):
        """Show error message."""
        messagebox.showerror("Error", message)
        self.analysis_complete()
        
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the visual lexical analyzer."""
    print("🚀 Starting Visual Lexical Analysis Interface...")
    app = LexicalAnalysisGUI()
    app.run()


if __name__ == "__main__":
    main()