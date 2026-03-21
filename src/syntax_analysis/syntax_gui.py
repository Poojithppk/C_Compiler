"""
Visual Syntax Analysis GUI for NEXUS Language

This module provides a graphical interface for visualizing the syntax analysis phase,
showing parse tree construction, AST generation, and error detection in real-time.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import List, Optional, Dict, Any
import threading
import time
import os

# Import the parsing components
from lexical_analysis.lexer import VisualLexicalAnalyzer
from lexical_analysis.tokens import Token, TokenType
from syntax_analysis.parser import Parser, ParseError
from syntax_analysis.ast_nodes import ASTNode, ProgramNode
from syntax_analysis.ast_printer import ASTPrinter  # We'll create this next
from semantic_analysis import SemanticAnalysisGUI


class SyntaxAnalysisGUI:
    """Visual interface for syntax analysis phase."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NEXUS Compiler - Syntax Analysis Phase")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Analysis components
        self.lexer = VisualLexicalAnalyzer(visual_mode=False)
        self.parser = None
        self.current_tokens = []
        self.current_ast = None
        self.parse_steps = []
        self.lexical_errors = []
        self.tokens_from_lexical = False
        
        # GUI state
        self.is_analyzing = False
        self.current_step = 0
        self.step_delay = 0.5
        self.auto_mode = True
        
        # Load sample code
        self.sample_code = self._get_sample_code()
        
        self._create_gui()
        self._bind_events()
        
        # Load sample code
        self.input_text.insert(1.0, self.sample_code)
    
    def _create_gui(self):
        """Create the main GUI layout."""
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self._create_editor_tab()
        self._create_parse_tree_tab()
        self._create_ast_tab()
        self._create_errors_tab()
        self._create_steps_tab()
        
        # Create bottom control panel
        self._create_control_panel(main_frame)
    
    def _create_editor_tab(self):
        """Create source code editor tab."""
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="📝 Source Code")
        
        # Toolbar
        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill='x', pady=(0, 5))
        
        ttk.Button(toolbar, text="📁 Load File", command=self._load_file).pack(side='left', padx=5)
        ttk.Button(toolbar, text="💾 Save File", command=self._save_file).pack(side='left', padx=5)
        ttk.Button(toolbar, text="🔄 Clear", command=self._clear_editor).pack(side='left', padx=5)
        ttk.Button(toolbar, text="📋 Load Sample", command=self._load_sample).pack(side='left', padx=5)
        
        # Code editor with line numbers
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill='both', expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(
            editor_container,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            wrap='none',
            state='disabled',
            bg='#3c3c3c',
            fg='#888888',
            font=('Consolas', 10)
        )
        self.line_numbers.pack(side='left', fill='y')
        
        # Main editor
        self.input_text = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.NONE,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white',
            selectbackground='#264f78'
        )
        self.input_text.pack(side='left', fill='both', expand=True)
        
        # Syntax highlighting
        self._setup_syntax_highlighting()
    
    def _create_parse_tree_tab(self):
        """Create parse tree visualization tab."""
        tree_frame = ttk.Frame(self.notebook)
        self.notebook.add(tree_frame, text="🌳 Parse Tree")
        
        # Toolbar
        tree_toolbar = ttk.Frame(tree_frame)
        tree_toolbar.pack(fill='x', pady=(0, 5))
        
        ttk.Button(tree_toolbar, text="🔍 Expand All", command=self._expand_tree).pack(side='left', padx=5)
        ttk.Button(tree_toolbar, text="📁 Collapse All", command=self._collapse_tree).pack(side='left', padx=5)
        
        # Tree view with scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Parse tree
        self.parse_tree = ttk.Treeview(
            tree_container,
            columns=('type', 'value', 'line'),
            show='tree headings'
        )
        self.parse_tree.heading('#0', text='Parse Tree')
        self.parse_tree.heading('type', text='Type')
        self.parse_tree.heading('value', text='Value')
        self.parse_tree.heading('line', text='Line')
        
        # Scrollbars
        tree_v_scroll = ttk.Scrollbar(tree_container, orient='vertical', command=self.parse_tree.yview)
        tree_h_scroll = ttk.Scrollbar(tree_container, orient='horizontal', command=self.parse_tree.xview)
        self.parse_tree.configure(yscrollcommand=tree_v_scroll.set, xscrollcommand=tree_h_scroll.set)
        
        # Pack tree and scrollbars
        self.parse_tree.pack(side='left', fill='both', expand=True)
        tree_v_scroll.pack(side='right', fill='y')
        tree_h_scroll.pack(side='bottom', fill='x')
    
    def _create_ast_tab(self):
        """Create AST visualization tab."""
        ast_frame = ttk.Frame(self.notebook)
        self.notebook.add(ast_frame, text="🔗 AST")
        
        # AST display
        self.ast_text = scrolledtext.ScrolledText(
            ast_frame,
            wrap=tk.NONE,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            state='disabled'
        )
        self.ast_text.pack(fill='both', expand=True)
    
    def _create_errors_tab(self):
        """Create errors and warnings tab."""
        errors_frame = ttk.Frame(self.notebook)
        self.notebook.add(errors_frame, text="❌ Errors & Warnings")
        
        # Error list
        error_container = ttk.Frame(errors_frame)
        error_container.pack(fill='both', expand=True)
        
        self.error_tree = ttk.Treeview(
            error_container,
            columns=('type', 'line', 'column', 'message'),
            show='headings'
        )
        self.error_tree.heading('type', text='Type')
        self.error_tree.heading('line', text='Line')
        self.error_tree.heading('column', text='Column')
        self.error_tree.heading('message', text='Message')
        
        # Error scrollbar
        error_scroll = ttk.Scrollbar(error_container, orient='vertical', command=self.error_tree.yview)
        self.error_tree.configure(yscrollcommand=error_scroll.set)
        
        self.error_tree.pack(side='left', fill='both', expand=True)
        error_scroll.pack(side='right', fill='y')
    
    def _create_steps_tab(self):
        """Create parsing steps tab."""
        steps_frame = ttk.Frame(self.notebook)
        self.notebook.add(steps_frame, text="👣 Parse Steps")
        
        # Steps controls
        steps_toolbar = ttk.Frame(steps_frame)
        steps_toolbar.pack(fill='x', pady=(0, 5))
        
        self.step_label = ttk.Label(steps_toolbar, text="Step: 0/0")
        self.step_label.pack(side='left', padx=5)
        
        ttk.Button(steps_toolbar, text="⏮️ First", command=self._first_step).pack(side='left', padx=2)
        ttk.Button(steps_toolbar, text="⏪ Previous", command=self._previous_step).pack(side='left', padx=2)
        ttk.Button(steps_toolbar, text="⏯️ Play/Pause", command=self._toggle_auto_step).pack(side='left', padx=2)
        ttk.Button(steps_toolbar, text="⏩ Next", command=self._next_step).pack(side='left', padx=2)
        ttk.Button(steps_toolbar, text="⏭️ Last", command=self._last_step).pack(side='left', padx=2)
        
        # Speed control
        ttk.Label(steps_toolbar, text="Speed:").pack(side='left', padx=(20, 5))
        self.speed_scale = tk.Scale(
            steps_toolbar,
            from_=0.1, to=2.0, resolution=0.1,
            orient='horizontal', length=100,
            command=self._update_speed
        )
        self.speed_scale.set(0.5)
        self.speed_scale.pack(side='left', padx=5)
        
        # Steps list
        steps_container = ttk.Frame(steps_frame)
        steps_container.pack(fill='both', expand=True)
        
        self.steps_tree = ttk.Treeview(
            steps_container,
            columns=('rule', 'position', 'token', 'description'),
            show='headings'
        )
        self.steps_tree.heading('rule', text='Grammar Rule')
        self.steps_tree.heading('position', text='Position')
        self.steps_tree.heading('token', text='Current Token')
        self.steps_tree.heading('description', text='Description')
        
        steps_scroll = ttk.Scrollbar(steps_container, orient='vertical', command=self.steps_tree.yview)
        self.steps_tree.configure(yscrollcommand=steps_scroll.set)
        
        self.steps_tree.pack(side='left', fill='both', expand=True)
        steps_scroll.pack(side='right', fill='y')
    
    def _create_control_panel(self, parent):
        """Create main control panel."""
        control_frame = ttk.LabelFrame(parent, text="Analysis Controls", padding=10)
        control_frame.pack(fill='x', pady=(10, 0))
        
        # Left side - Analysis buttons
        left_controls = ttk.Frame(control_frame)
        left_controls.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            left_controls, 
            text="🔬 Start Syntax Analysis", 
            command=self._start_analysis,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            left_controls,
            text="⏹️ Stop Analysis",
            command=self._stop_analysis
        ).pack(side='left', padx=5)
        
        ttk.Button(
            left_controls,
            text="🔄 Reset",
            command=self._reset_analysis
        ).pack(side='left', padx=5)
        
        # Semantic Analysis Transition Button
        ttk.Button(
            left_controls,
            text="🎯 Proceed to Semantic Analysis",
            command=self.launch_semantic_analysis
        ).pack(side='left', padx=15)
        
        # Mode controls
        mode_frame = ttk.LabelFrame(left_controls, text="Mode", padding=5)
        mode_frame.pack(side='left', padx=(20, 5))
        
        self.mode_var = tk.StringVar(value="auto")
        ttk.Radiobutton(mode_frame, text="Auto", variable=self.mode_var, value="auto").pack(side='top')
        ttk.Radiobutton(mode_frame, text="Step", variable=self.mode_var, value="step").pack(side='top')
        
        # Right side - Progress and status
        right_controls = ttk.Frame(control_frame)
        right_controls.pack(side='right')
        
        # Progress bar
        progress_frame = ttk.Frame(right_controls)
        progress_frame.pack(side='top', pady=5)
        
        ttk.Label(progress_frame, text="Progress:").pack(side='left')
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            length=200, 
            mode='determinate'
        )
        self.progress_bar.pack(side='left', padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            right_controls,
            text="Ready for syntax analysis",
            font=('Segoe UI', 9)
        )
        self.status_label.pack(side='top', pady=2)
    
    def _setup_syntax_highlighting(self):
        """Setup basic syntax highlighting."""
        # Define text tags for highlighting
        self.input_text.tag_configure("keyword", foreground="#569cd6")
        self.input_text.tag_configure("string", foreground="#ce9178")
        self.input_text.tag_configure("number", foreground="#b5cea8")
        self.input_text.tag_configure("comment", foreground="#6a9955")
        self.input_text.tag_configure("identifier", foreground="#9cdcfe")
        
        # Keywords to highlight
        keywords = [
            'hold', 'fixed', 'func', 'return', 'when', 'otherwise', 
            'repeat', 'cycle', 'stop', 'skip', 'choose', 'option',
            'yes', 'no', 'null', 'and', 'or', 'not', 'show', 'ask',
            'secure', 'validate', 'sanitize'
        ]
        
        def highlight_syntax():
            content = self.input_text.get(1.0, tk.END)
            lines = content.split('\n')
            
            # Clear existing tags
            for tag in ["keyword", "string", "number", "comment", "identifier"]:
                self.input_text.tag_delete(tag)
            
            for line_num, line in enumerate(lines, 1):
                # Highlight keywords
                for keyword in keywords:
                    start = 0
                    while True:
                        pos = line.find(keyword, start)
                        if pos == -1:
                            break
                        
                        # Check if it's a whole word
                        if (pos == 0 or not line[pos-1].isalnum()) and \
                           (pos + len(keyword) == len(line) or not line[pos + len(keyword)].isalnum()):
                            
                            start_pos = f"{line_num}.{pos}"
                            end_pos = f"{line_num}.{pos + len(keyword)}"
                            self.input_text.tag_add("keyword", start_pos, end_pos)
                        
                        start = pos + 1
        
        # Bind highlighting to text changes
        self.input_text.bind('<KeyRelease>', lambda e: self.root.after_idle(highlight_syntax))
    
    def _bind_events(self):
        """Bind GUI events."""
        # Line numbers update
        def update_line_numbers():
            content = self.input_text.get(1.0, tk.END)
            lines = content.split('\n')
            line_text = '\n'.join(str(i) for i in range(1, len(lines)))
            
            self.line_numbers.config(state='normal')
            self.line_numbers.delete(1.0, tk.END)
            self.line_numbers.insert(1.0, line_text)
            self.line_numbers.config(state='disabled')
        
        self.input_text.bind('<KeyRelease>', lambda e: self.root.after_idle(update_line_numbers))
        
        # Error tree click
        self.error_tree.bind('<Double-1>', self._on_error_click)
        
        # Parse tree click
        self.parse_tree.bind('<Double-1>', self._on_tree_click)
    
    def _get_sample_code(self) -> str:
        """Return sample NEXUS code for demonstration."""
        return '''// Simple Program - Sum of Two Numbers
hold num1 = 5;
hold num2 = 10;
hold total = num1 + num2;
show total;'''
    
    # =====================
    # FILE OPERATIONS
    # =====================
    
    def _load_file(self):
        """Load source code from file."""
        filename = filedialog.askopenfilename(
            title="Load NEXUS Source File",
            filetypes=[("NEXUS files", "*.nx"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(1.0, content)
                    self.status_label.config(text=f"Loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def _save_file(self):
        """Save source code to file."""
        content = self.input_text.get(1.0, tk.END)
        
        filename = filedialog.asksaveasfilename(
            title="Save NEXUS Source File",
            defaultextension=".nx",
            filetypes=[("NEXUS files", "*.nx"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(content)
                    self.status_label.config(text=f"Saved: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def _clear_editor(self):
        """Clear the editor."""
        self.input_text.delete(1.0, tk.END)
        self._reset_analysis()
    
    def _load_sample(self):
        """Load sample code."""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, self.sample_code)
    
    # =====================
    # ANALYSIS METHODS
    # =====================
    
    def _start_analysis(self):
        """Start syntax analysis."""
        if self.is_analyzing:
            return
        
        self.is_analyzing = True
        self.status_label.config(text="Starting syntax analysis...")
        self.progress_bar['value'] = 0
        
        # Get source code
        source_code = self.input_text.get(1.0, tk.END).strip()
        
        if not source_code:
            messagebox.showwarning("Warning", "No source code to analyze!")
            self.is_analyzing = False
            return
        
        # Start analysis in thread
        analysis_thread = threading.Thread(target=self._run_analysis, args=(source_code,))
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _run_analysis(self, source_code: str):
        """Run the actual syntax analysis."""
        try:
            # If tokens already loaded from lexical analysis, skip lexical phase
            if self.tokens_from_lexical:
                self._run_syntax_only_analysis()
                return
            
            # Step 1: Lexical Analysis
            self.root.after(0, lambda: self.status_label.config(text="Running lexical analysis..."))
            
            self.lexer = VisualLexicalAnalyzer(visual_mode=False)
            self.current_tokens, self.lexical_errors = self.lexer.analyze(source_code)
            
            self.root.after(0, lambda: self.progress_bar.config(value=33))
            
            # Step 2: Syntax Analysis
            self.root.after(0, lambda: self.status_label.config(text="Running syntax analysis..."))
            
            self.parser = Parser(self.current_tokens, debug_mode=True)
            
            if self.mode_var.get() == "step":
                self.parser.enable_step_mode(self._step_callback)
            
            self.current_ast = self.parser.parse()
            self.parse_steps = self.parser.get_parse_steps()
            
            self.root.after(0, lambda: self.progress_bar.config(value=66))
            
            # Step 3: Update GUI
            self.root.after(0, self._update_results)
            self.root.after(0, lambda: self.progress_bar.config(value=100))
            self.root.after(0, lambda: self.status_label.config(text="Syntax analysis completed!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"Analysis failed: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", str(e)))
        finally:
            self.is_analyzing = False
    
    def load_tokens_from_lexical(self, tokens: list, errors: list = None):
        """Load tokens from lexical analysis phase."""
        self.current_tokens = tokens
        self.lexical_errors = errors or []
        self.tokens_from_lexical = True
        
        # Update status
        status_msg = f"✅ Loaded {len(tokens)} tokens from Lexical Analysis"
        if self.lexical_errors:
            status_msg += f" ({len(self.lexical_errors)} lexical errors)"
        self.status_label.config(text=status_msg)
        
        # Show tokens in parse tree tab
        self._show_lexical_results()
        
        # Auto-start syntax analysis
        self.root.after(1000, self._start_syntax_only_analysis)
    
    def _show_lexical_results(self):
        """Show lexical analysis results in the interface."""
        # Update parse tree tab with token information
        self.notebook.select(1)  # Switch to parse tree tab
        
        # Clear existing tree
        for item in self.parse_tree.get_children():
            self.parse_tree.delete(item)
        
        # Add token summary
        token_summary = self.parse_tree.insert("", "end", text="📊 Lexical Analysis Results", 
                                             values=("", f"{len(self.current_tokens)} tokens", ""))
        
        # Add token details
        for i, token in enumerate(self.current_tokens[:20]):  # Show first 20 tokens
            token_item = self.parse_tree.insert(token_summary, "end", 
                                               text=f"Token {i+1}: {token.token_type.name}",
                                               values=(token.lexeme, f"Line {token.line}", f"Col {token.column}"))
        
        if len(self.current_tokens) > 20:
            self.parse_tree.insert(token_summary, "end", text=f"... and {len(self.current_tokens)-20} more tokens")
        
        # Show errors if any
        if self.lexical_errors:
            error_summary = self.parse_tree.insert("", "end", text="⚠️ Lexical Errors",
                                                  values=("", f"{len(self.lexical_errors)} errors", ""))
            for i, error in enumerate(self.lexical_errors[:10]):  # Show first 10 errors
                self.parse_tree.insert(error_summary, "end", 
                                     text=f"Error {i+1}", 
                                     values=(str(error), f"Line {getattr(error, 'line', 'Unknown')}", ""))
    
    def _start_syntax_only_analysis(self):
        """Start syntax analysis with pre-loaded tokens."""
        if not self.current_tokens:
            messagebox.showwarning("No Tokens", "No tokens available for syntax analysis.")
            return
        
        self.is_analyzing = True
        self.progress_bar.config(value=50)  # Start at 50% since lexical is done
        self.status_label.config(text="Starting syntax analysis with loaded tokens...")
        
        # Run syntax analysis in thread
        threading.Thread(target=self._run_syntax_only_analysis, daemon=True).start()
    
    def _run_syntax_only_analysis(self):
        """Run syntax analysis only (skip lexical analysis)."""
        try:
            # Step 1: Syntax Analysis
            self.root.after(0, lambda: self.status_label.config(text="Running syntax analysis..."))
            
            self.parser = Parser(self.current_tokens, debug_mode=True)
            
            if self.mode_var.get() == "step":
                self.parser.enable_step_mode(self._step_callback)
            
            self.current_ast = self.parser.parse()
            self.parse_steps = self.parser.get_parse_steps()
            
            self.root.after(0, lambda: self.progress_bar.config(value=90))
            
            # Step 2: Update GUI  
            self.root.after(0, self._update_results)
            self.root.after(0, lambda: self.progress_bar.config(value=100))
            self.root.after(0, lambda: self.status_label.config(text="✅ Syntax analysis completed!"))
            
        except Exception as e:
            error_msg = f"Syntax analysis failed: {str(e)}"
            self.root.after(0, lambda: self.status_label.config(text=error_msg))
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Syntax Analysis Error", msg))
        finally:
            self.is_analyzing = False
    
    def _step_callback(self, step_info: dict):
        """Callback for step-by-step parsing."""
        if self.mode_var.get() == "step" and self.auto_mode:
            time.sleep(self.step_delay)
            self.root.after(0, self._update_step_display, step_info)
    
    def _stop_analysis(self):
        """Stop the analysis."""
        self.is_analyzing = False
        self.status_label.config(text="Analysis stopped")
    
    def _reset_analysis(self):
        """Reset analysis results."""
        self.is_analyzing = False
        self.current_tokens = []
        self.current_ast = None
        self.parse_steps = []
        self.current_step = 0
        self.lexical_errors = []
        self.tokens_from_lexical = False
        
        # Clear displays
        self.parse_tree.delete(*self.parse_tree.get_children())
        self.error_tree.delete(*self.error_tree.get_children())
        self.steps_tree.delete(*self.steps_tree.get_children())
        
        self.ast_text.config(state='normal')
        self.ast_text.delete(1.0, tk.END)
        self.ast_text.config(state='disabled')
        
        self.progress_bar['value'] = 0
        self.status_label.config(text="Ready for syntax analysis")
    
    # =====================
    # DISPLAY UPDATE METHODS
    # =====================
    
    def _update_results(self):
        """Update all result displays."""
        self._update_parse_tree()
        self._update_ast_display()
        self._update_errors_display()
        self._update_steps_display()
    
    def _update_parse_tree(self):
        """Update parse tree display."""
        self.parse_tree.delete(*self.parse_tree.get_children())
        
        if not self.current_ast:
            self.parse_tree.insert("", "end", text="❌ No AST available", values=("N/A", "", ""))
            return
        
        # Show summary info
        summary_id = self.parse_tree.insert("", "end", text="📊 Parse Summary", values=("Metadata", "", ""))
        
        self.parse_tree.insert(summary_id, "end", text=f"✅ Parser Status: Success", values=("Info", "", ""))
        self.parse_tree.insert(summary_id, "end", text=f"❌ Parse Errors: {len(self.parser.errors) if self.parser else 0}", values=("Info", "", ""))
        self.parse_tree.insert(summary_id, "end", text=f"⚠️ Warnings: {len(self.parser.warnings) if self.parser else 0}", values=("Info", "", ""))
        
        # Add the AST
        ast_id = self.parse_tree.insert("", "end", text="🌳 Abstract Syntax Tree", values=("AST", "", ""))
        self._add_tree_node(ast_id, self.current_ast, self.current_ast.__class__.__name__)
    
    def _add_tree_node(self, parent: str, node: ASTNode, text: str) -> str:
        """Recursively add AST node to tree view."""
        node_type = node.__class__.__name__
        value = ""
        line = getattr(node, 'line', 0)
        
        # Get node-specific value
        if hasattr(node, 'name'):
            value = node.name
        elif hasattr(node, 'value'):
            value = str(node.value)
        elif hasattr(node, 'lexeme'):
            value = node.lexeme
        
        # Insert the node
        item_id = self.parse_tree.insert(
            parent, 'end', 
            text=text,
            values=(node_type, value, line)
        )
        
        # Add children
        if hasattr(node, 'children') and node.children:
            for i, child in enumerate(node.children):
                child_text = f"Child_{i}"
                self._add_tree_node(item_id, child, child_text)
        elif hasattr(node, 'statements') and node.statements:
            for i, stmt in enumerate(node.statements):
                self._add_tree_node(item_id, stmt, f"Statement_{i}")
        elif hasattr(node, 'body') and node.body:
            self._add_tree_node(item_id, node.body, "Body")
        elif hasattr(node, 'expression') and node.expression:
            self._add_tree_node(item_id, node.expression, "Expression")
        
        return item_id
    
    def _update_ast_display(self):
        """Update AST text display."""
        self.ast_text.config(state='normal')
        self.ast_text.delete(1.0, tk.END)
        
        if self.current_ast:
            try:
                from syntax_analysis.ast_printer import ASTPrinter
                printer = ASTPrinter()
                ast_str = printer.print_ast(self.current_ast)
                self.ast_text.insert(1.0, ast_str)
            except Exception as e:
                # Fallback if ASTPrinter not available
                self.ast_text.insert(1.0, f"Error loading AST printer: {str(e)}\n\n")
                ast_str = self._simple_ast_print(self.current_ast)
                self.ast_text.insert(tk.END, ast_str)
        else:
            self.ast_text.insert(1.0, "No AST available. Run syntax analysis first.")
        
        self.ast_text.config(state='disabled')
    
    def _simple_ast_print(self, node: ASTNode, indent: int = 0) -> str:
        """Simple AST printing fallback."""
        if node is None:
            return ""
        
        result = "  " * indent + "📍 " + node.__class__.__name__
        
        # Add node-specific info
        if hasattr(node, 'name') and node.name:
            result += f" (name: {node.name})"
        elif hasattr(node, 'value') and node.value is not None:
            result += f" (value: {node.value})"
        elif hasattr(node, 'lexeme') and node.lexeme:
            result += f" (lexeme: {node.lexeme})"
        elif hasattr(node, 'operator') and node.operator:
            result += f" (op: {node.operator})"
        
        # Add line/column info
        if hasattr(node, 'line') and node.line:
            result += f" [L{node.line}:C{node.column}]" if hasattr(node, 'column') else f" [L{node.line}]"
        
        result += "\n"
        
        # Add children recursively
        if hasattr(node, 'statements') and node.statements:
            for i, stmt in enumerate(node.statements):
                result += "  " * (indent + 1) + f"├─ Statement[{i}]:\n"
                result += self._simple_ast_print(stmt, indent + 2)
        
        if hasattr(node, 'body') and node.body:
            result += "  " * (indent + 1) + "├─ Body:\n"
            result += self._simple_ast_print(node.body, indent + 2)
        
        if hasattr(node, 'expression') and node.expression:
            result += "  " * (indent + 1) + "├─ Expression:\n"
            result += self._simple_ast_print(node.expression, indent + 2)
        
        if hasattr(node, 'left') and node.left:
            result += "  " * (indent + 1) + "├─ Left:\n"
            result += self._simple_ast_print(node.left, indent + 2)
        
        if hasattr(node, 'right') and node.right:
            result += "  " * (indent + 1) + "├─ Right:\n"
            result += self._simple_ast_print(node.right, indent + 2)
        
        if hasattr(node, 'initializer') and node.initializer:
            result += "  " * (indent + 1) + "├─ Initializer:\n"
            result += self._simple_ast_print(node.initializer, indent + 2)
        
        if hasattr(node, 'parameters') and node.parameters:
            result += "  " * (indent + 1) + f"├─ Parameters: {len(node.parameters)}\n"
            for i, param in enumerate(node.parameters):
                result += self._simple_ast_print(param, indent + 2)
        
        if hasattr(node, 'arguments') and node.arguments:
            result += "  " * (indent + 1) + f"├─ Arguments: {len(node.arguments)}\n"
            for i, arg in enumerate(node.arguments):
                result += self._simple_ast_print(arg, indent + 2)
        
        if hasattr(node, 'callee') and node.callee:
            result += "  " * (indent + 1) + "├─ Callee:\n"
            result += self._simple_ast_print(node.callee, indent + 2)
        
        return result
    
    def _update_errors_display(self):
        """Update errors and warnings display."""
        self.error_tree.delete(*self.error_tree.get_children())
        
        if not self.parser:
            self.error_tree.insert('', 'end', values=('Info', '0', '0', 'No parser available'))
            return
        
        errors = self.parser.get_errors() if hasattr(self.parser, 'get_errors') else self.parser.errors
        warnings = self.parser.get_warnings() if hasattr(self.parser, 'get_warnings') else self.parser.warnings
        
        if not errors and not warnings:
            self.error_tree.insert('', 'end', 
                values=('✅ Success', '0', '0', 'No errors or warnings found!'),
                tags=('success',))
            return
        
        # Add errors
        for error in errors:
            error_msg = str(error.message) if hasattr(error, 'message') else str(error)
            line = str(error.token.line) if hasattr(error, 'token') else '0'
            col = str(error.token.column) if hasattr(error, 'token') else '0'
            
            self.error_tree.insert(
                '', 'end',
                values=('❌ Error', line, col, error_msg),
                tags=('error',)
            )
        
        # Add warnings
        for warning in warnings:
            self.error_tree.insert(
                '', 'end',
                values=('⚠️ Warning', '', '', str(warning)),
                tags=('warning',)
            )
        
        # Configure tags
        self.error_tree.tag_configure('error', foreground='red')
        self.error_tree.tag_configure('warning', foreground='orange')
        self.error_tree.tag_configure('success', foreground='green')
    
    def _update_steps_display(self):
        """Update parsing steps display."""
        self.steps_tree.delete(*self.steps_tree.get_children())
        
        if not self.parse_steps:
            self.steps_tree.insert('', 'end', 
                values=('', '', '', 'No parsing steps available'),
                tags=('info',))
        else:
            # Add header with step count
            header = self.steps_tree.insert('', 'end',
                values=('', '', '', f'Total Parsing Steps: {len(self.parse_steps)}'),
                tags=('header',))
            
            # Add each step
            for i, step in enumerate(self.parse_steps):
                step_num = f"Step {i+1}/{len(self.parse_steps)}"
                rule = step.get('rule', 'unknown')
                token = step.get('token', 'EOF')
                description = step.get('description', '')
                line = step.get('line', '')
                col = step.get('column', '')
                pos = step.get('position', '')
                
                # Format the display
                display_token = f"{token}" + (f" @L{line}:C{col}" if line else "")
                display_desc = f"{description[:50]}" + ("..." if len(description) > 50 else "")
                
                self.steps_tree.insert('', 'end',
                    values=(rule, display_token, pos, display_desc),
                    tags=('step',))
        
        self._update_step_label()
    
    def _update_step_label(self):
        """Update step counter label."""
        total_steps = len(self.parse_steps)
        self.step_label.config(text=f"Steps: {total_steps} | Current: {self.current_step}")
        
        if total_steps > 0 and self.current_step <= total_steps:
            # Highlight current step
            for item in self.steps_tree.get_children():
                self.steps_tree.item(item, tags=())
            
            if self.current_step > 0:
                items = list(self.steps_tree.get_children())
                # Skip the header (first item)
                if len(items) > 1 and self.current_step <= len(items) - 1:
                    self.steps_tree.item(items[self.current_step], tags=('current',))
                    self.steps_tree.see(items[self.current_step])
        
        # Configure tags
        self.steps_tree.tag_configure('header', background='#366aa3', foreground='white')
        self.steps_tree.tag_configure('step', background='#1e1e1e', foreground='#d4d4d4')
        self.steps_tree.tag_configure('current', background='#264f78', foreground='#ffffff')
        self.steps_tree.tag_configure('info', foreground='#888888')
    
    def _update_step_display(self, step_info: dict):
        """Update display for current step."""
        # This would be called during step-by-step parsing
        # Update the current step highlight, etc.
        pass
    
    # =====================
    # STEP CONTROL METHODS
    # =====================
    
    def _first_step(self):
        """Go to first step."""
        self.current_step = 0
        self._update_step_label()
    
    def _previous_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self._update_step_label()
    
    def _next_step(self):
        """Go to next step."""
        if self.current_step < len(self.parse_steps):
            self.current_step += 1
            self._update_step_label()
    
    def _last_step(self):
        """Go to last step."""
        self.current_step = len(self.parse_steps)
        self._update_step_label()
    
    def _toggle_auto_step(self):
        """Toggle auto-stepping."""
        self.auto_mode = not self.auto_mode
        status = "enabled" if self.auto_mode else "disabled"
        self.status_label.config(text=f"Auto-stepping {status}")
    
    def _update_speed(self, value):
        """Update step delay speed."""
        self.step_delay = float(value)
    
    # =====================
    # EVENT HANDLERS
    # =====================
    
    def _expand_tree(self):
        """Expand all tree items."""
        def expand_children(item):
            self.parse_tree.item(item, open=True)
            children = self.parse_tree.get_children(item)
            for child in children:
                expand_children(child)
        
        for item in self.parse_tree.get_children():
            expand_children(item)
    
    def _collapse_tree(self):
        """Collapse all tree items."""
        def collapse_children(item):
            self.parse_tree.item(item, open=False)
            children = self.parse_tree.get_children(item)
            for child in children:
                collapse_children(child)
        
        for item in self.parse_tree.get_children():
            collapse_children(item)
    
    def _on_error_click(self, event):
        """Handle error tree click."""
        item = self.error_tree.selection()[0]
        values = self.error_tree.item(item, 'values')
        
        if len(values) >= 3 and values[1]:  # Line number available
            try:
                line = int(values[1])
                self.input_text.mark_set('insert', f"{line}.0")
                self.input_text.see(f"{line}.0")
                self.notebook.select(0)  # Switch to editor tab
            except ValueError:
                pass
    
    def _on_tree_click(self, event):
        """Handle parse tree click."""
        item = self.parse_tree.selection()[0]
        values = self.parse_tree.item(item, 'values')
        
        if len(values) >= 3 and values[2]:  # Line number available
            try:
                line = int(values[2])
                self.input_text.mark_set('insert', f"{line}.0")
                self.input_text.see(f"{line}.0")
                self.notebook.select(0)  # Switch to editor tab
            except ValueError:
                pass
    
    def launch_semantic_analysis(self):
        """Launch semantic analysis with current AST."""
        if not self.current_ast:
            messagebox.showwarning(
                "Semantic Analysis",
                "Please complete syntax analysis first!"
            )
            return
        
        errors = self.parser.get_errors() if hasattr(self.parser, 'get_errors') else (self.parser.errors if hasattr(self.parser, 'errors') else [])
        
        if errors:
            proceed = messagebox.askyesno(
                "Syntax Errors Detected",
                f"Found {len(errors)} syntax errors.\n\nProceed to semantic analysis anyway?\n\nNote: Semantic analysis may fail with syntax errors."
            )
            if not proceed:
                return
        
        # Show transition message
        messagebox.showinfo(
            "🎯 Semantic Analysis",
            f"✅ Syntax Analysis Results:\n\n🌳 AST generated successfully\n⚠️ {len(errors)} syntax errors\n\n🚀 Launching Semantic Analysis Phase...\n\nAST will be passed to semantic analysis for type checking and scope validation."
        )
        
        try:
            # Close syntax analysis window
            self.root.withdraw()
            
            # Create new window for semantic analysis
            semantic_root = tk.Tk()
            semantic_app = SemanticAnalysisGUI(semantic_root)
            
            # Pass AST to semantic analysis
            semantic_app.load_ast_from_syntax(self.current_ast, errors)
            
            # Run semantic analysis
            semantic_root.mainloop()
            
            # Show syntax analysis again after semantic analysis closes
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Semantic Analysis: {str(e)}")
            self.root.deiconify()


# Main function to run the syntax analysis GUI
def main():
    """Main function to run the syntax analysis interface."""
    root = tk.Tk()
    
    # Configure ttk style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create and run the application
    app = SyntaxAnalysisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()