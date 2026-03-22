"""
Visual Semantic Analysis GUI for NEXUS Language

This module provides a graphical interface for visualizing the semantic analysis phase,
showing symbol table construction, type checking, scope analysis, and error detection.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import List, Optional, Dict, Any
import threading
import time
import os

# Import semantic analysis components
from .semantic import SemanticAnalyzer
from .semantic_symbols import SymbolTable, Symbol, DataType

# Import lexical and syntax components
try:
    from lexical_analysis.lexer import VisualLexicalAnalyzer
    from lexical_analysis.tokens import Token, TokenType
    from syntax_analysis.parser import Parser, ParseError
    from syntax_analysis.ast_nodes import ASTNode
    from syntax_analysis.ast_printer import ASTPrinter
    from intermediate_code.intermediate_gui import IntermediateCodeGUI
except ImportError as e:
    print(f"Warning: Could not import dependencies: {e}")


class SemanticAnalysisGUI:
    """Visual interface for semantic analysis phase."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NEXUS Compiler - Semantic Analysis Phase")
        self.root.geometry("1400x950")
        self.root.configure(bg='#2b2b2b')
        
        # Analysis components
        self.lexer = VisualLexicalAnalyzer(visual_mode=False)
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer(visual_mode=True)
        
        self.current_tokens = []
        self.current_ast = None
        self.analysis_steps = []
        self.current_step = 0
        
        # State
        self.is_analyzing = False
        self.step_delay = 0.5
        self.auto_mode = True
        self.tokens_from_previous = None
        
        # Load sample code
        self.sample_code = self._get_sample_code()
        
        self._create_gui()
        self._bind_events()
        
        # Load sample code
        if hasattr(self, 'input_text'):
            self.input_text.insert(1.0, self.sample_code)
    
    def load_ast_from_syntax(self, ast, syntax_errors=None):
        """Load AST from syntax analysis phase."""
        self.current_ast = ast
        syntax_errors = syntax_errors or []
        
        # Update status
        status_msg = f"✅ Loaded AST from Syntax Analysis"
        if syntax_errors:
            status_msg += f" ({len(syntax_errors)} syntax errors)"
        self._update_status(status_msg)
        
        # Auto-start semantic analysis after a short delay
        self.root.after(500, self._start_analysis)
    
    def _create_gui(self):
        """Create the main GUI layout."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🎯 SEMANTIC ANALYSIS PHASE",
            font=('Arial', 16, 'bold'),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self._create_editor_tab()
        self._create_symbol_table_tab()
        self._create_scope_tab()
        self._create_type_analysis_tab()
        self._create_errors_tab()
        self._create_analysis_tab()
        
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
        
        # Code editor
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill='both', expand=True)
        
        # Line numbers (simplified)
        scrollbar = ttk.Scrollbar(editor_container)
        scrollbar.pack(side='right', fill='y')
        
        self.input_text = scrolledtext.ScrolledText(
            editor_container,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='white',
            yscrollcommand=scrollbar.set
        )
        self.input_text.pack(fill='both', expand=True)
        scrollbar.config(command=self.input_text.yview)
    
    def _create_symbol_table_tab(self):
        """Create symbol table view tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📋 Symbol Table")
        
        # Scrollable text for symbol table
        scrollbar = ttk.Scrollbar(tab_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.symbol_table_text = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#1e1e1e',
            fg='#00ff00',
            yscrollcommand=scrollbar.set
        )
        self.symbol_table_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.symbol_table_text.yview)
        
        # Header
        self.symbol_table_text.insert(1.0, "Symbol Table (will update after analysis)\n\n")
        self.symbol_table_text.config(state='disabled')
    
    def _create_scope_tab(self):
        """Create scope hierarchy view tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔍 Scope Hierarchy")
        
        # Scrollable text for scopes
        scrollbar = ttk.Scrollbar(tab_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.scope_text = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#1e1e1e',
            fg='#00ddff',
            yscrollcommand=scrollbar.set
        )
        self.scope_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.scope_text.yview)
        
        self.scope_text.insert(1.0, "Scope Hierarchy (will update after analysis)\n\n")
        self.scope_text.config(state='disabled')
    
    def _create_type_analysis_tab(self):
        """Create type checking results tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔷 Type Analysis")
        
        # Scrollable text for type analysis
        scrollbar = ttk.Scrollbar(tab_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.type_text = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#1e1e1e',
            fg='#ffff00',
            yscrollcommand=scrollbar.set
        )
        self.type_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.type_text.yview)
        
        self.type_text.insert(1.0, "Type Analysis Results (will update after analysis)\n\n")
        self.type_text.config(state='disabled')
    
    def _create_errors_tab(self):
        """Create errors and warnings tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚠️ Errors & Warnings")
        
        # Scrollable text for errors
        scrollbar = ttk.Scrollbar(tab_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.errors_text = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#1e1e1e',
            fg='#ff6b6b',
            yscrollcommand=scrollbar.set
        )
        self.errors_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.errors_text.yview)
        
        self.errors_text.insert(1.0, "Semantic Errors and Warnings\n\n")
        self.errors_text.config(state='disabled')
    
    def _create_analysis_tab(self):
        """Create analysis steps tab."""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Analysis Steps")
        
        # Scrollable text for steps
        scrollbar = ttk.Scrollbar(tab_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.steps_text = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#1e1e1e',
            fg='#00ff88',
            yscrollcommand=scrollbar.set
        )
        self.steps_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar.config(command=self.steps_text.yview)
        
        self.steps_text.insert(1.0, "Analysis Steps (will update during analysis)\n\n")
        self.steps_text.config(state='disabled')
    
    def _create_control_panel(self, parent):
        """Create the control panel with buttons and settings."""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Analysis Controls", padding=10)
        control_frame.pack(fill='x', padx=0, pady=(10, 0))
        
        # Left side - main buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side='left', padx=5)
        
        self.analyze_btn = ttk.Button(
            button_frame,
            text="🔍 Analyze",
            command=self._start_analysis
        )
        self.analyze_btn.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="⏮️ Reset", command=self._reset_analysis).pack(side='left', padx=5)
        
        # Next phase button
        ttk.Button(button_frame, text="▶️ Next Phase (Intermediate Code)", 
                  command=self._launch_intermediate_code).pack(side='left', padx=5)
        
        # Middle - settings
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(side='left', padx=20)
        
        ttk.Label(settings_frame, text="Animation Speed:").pack(side='left', padx=5)
        self.speed_var = tk.StringVar(value="Medium")
        speed_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.speed_var,
            values=["Slow", "Medium", "Fast", "Instant"],
            state='readonly',
            width=10
        )
        speed_combo.pack(side='left', padx=5)
        speed_combo.bind('<<ComboboxSelected>>', self._on_speed_changed)
        
        # Auto mode checkbox
        self.auto_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Auto Mode", variable=self.auto_mode_var).pack(side='left', padx=5)
        
        # Status label
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side='right', padx=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=('Arial', 10),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        self.status_label.pack()
    
    def _start_analysis(self):
        """Start semantic analysis."""
        # Check if AST was loaded from syntax phase
        if self.current_ast:
            # Skip to semantic analysis directly
            thread = threading.Thread(target=self._run_semantic_only_analysis, daemon=True)
            thread.start()
        else:
            # Full analysis from code
            code = self.input_text.get(1.0, tk.END).strip()
            if not code:
                messagebox.showwarning("Empty Code", "Please enter some code to analyze.")
                return
            
            # Run analysis in background thread
            thread = threading.Thread(target=self._run_analysis_thread, args=(code,), daemon=True)
            thread.start()
    
    def _run_semantic_only_analysis(self):
        """Run only semantic analysis on already-parsed AST."""
        try:
            self.is_analyzing = True
            self.analyze_btn.config(state='disabled')
            self._update_status("Analyzing semantics...")
            self.analysis_steps = []
            self.current_step = 0
            
            # Set callbacks
            self.semantic_analyzer.set_visual_callback(self._on_analysis_step)
            self.semantic_analyzer.set_error_callback(self._on_semantic_error)
            
            # Perform semantic analysis on loaded AST
            success, errors, warnings = self.semantic_analyzer.analyze(self.current_ast)
            
            # Display results
            self._display_results(success, errors, warnings)
            
            self._update_status(f"✅ Analysis Complete - Errors: {len(errors)}, Warnings: {len(warnings)}")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during analysis: {str(e)}")
        finally:
            self.is_analyzing = False
            self.analyze_btn.config(state='normal')
    
    def _run_analysis_thread(self, code: str):
        """Run semantic analysis in background thread."""
        try:
            self.is_analyzing = True
            self.analyze_btn.config(state='disabled')
            self._update_status("Performing lexical analysis...")
            
            # Phase 1: Lexical Analysis
            tokens, lexical_errors = self.lexer.analyze(code)
            self.current_tokens = tokens
            self._update_status("Tokens generated: " + str(len(self.current_tokens)))
            
            # Phase 2: Syntax Analysis
            self._update_status("Performing syntax analysis...")
            try:
                self.parser = Parser(tokens)
                self.current_ast = self.parser.parse()
                self._update_status("AST generated successfully")
            except Exception as e:
                messagebox.showerror("Syntax Error", f"Syntax analysis failed: {str(e)}")
                self.analyze_btn.config(state='normal')
                self.is_analyzing = False
                return
            
            # Phase 3: Semantic Analysis
            self._update_status("Analyzing semantics...")
            self.analysis_steps = []
            self.current_step = 0
            
            # Set callbacks
            self.semantic_analyzer.set_visual_callback(self._on_analysis_step)
            self.semantic_analyzer.set_error_callback(self._on_semantic_error)
            
            # Perform semantic analysis
            success, errors, warnings = self.semantic_analyzer.analyze(self.current_ast)
            
            # Display results
            self._display_results(success, errors, warnings)
            
            self._update_status(f"✅ Analysis Complete - Errors: {len(errors)}, Warnings: {len(warnings)}")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during analysis: {str(e)}")
        finally:
            self.is_analyzing = False
            self.analyze_btn.config(state='normal')
    
    def _on_analysis_step(self, step: Dict[str, Any]):
        """Callback when an analysis step occurs."""
        self.analysis_steps.append(step)
        self._update_steps_display(step)
        
        if not self.auto_mode_var.get():
            self.root.after(int(self.step_delay * 1000), lambda: None)
    
    def _on_semantic_error(self, error: str):
        """Callback when a semantic error is found."""
        self._update_errors_display(error, "error")
    
    def _display_results(self, success: bool, errors: List[str], warnings: List[str]):
        """Display analysis results in the GUI."""
        symbol_table = self.semantic_analyzer.get_symbol_table()
        stats = self.semantic_analyzer.get_statistics()
        
        # Display symbol table
        self._update_symbol_table_display(symbol_table)
        
        # Display scope information
        self._update_scope_display(symbol_table)
        
        # Display type information
        self._update_type_display(symbol_table)
        
        # Display errors and warnings
        self._update_all_errors_display(errors, warnings)
        
        # Display summary
        self._update_summary(success, stats, errors, warnings)
    
    def _update_status(self, msg: str):
        """Update status label."""
        self.status_label.config(text=msg)
        self.root.update()
    
    def _update_symbol_table_display(self, symbol_table: SymbolTable):
        """Update symbol table display."""
        self.symbol_table_text.config(state='normal')
        self.symbol_table_text.delete(1.0, tk.END)
        
        content = str(symbol_table)
        self.symbol_table_text.insert(1.0, content)
        self.symbol_table_text.config(state='disabled')
    
    def _update_scope_display(self, symbol_table: SymbolTable):
        """Update scope hierarchy display."""
        self.scope_text.config(state='normal')
        self.scope_text.delete(1.0, tk.END)
        
        content = "SCOPE HIERARCHY\n" + "=" * 60 + "\n\n"
        for i, scope in enumerate(symbol_table.scopes):
            content += f"Level {i}: {scope.scope_type}\n"
            content += f"  Symbols: {len(scope.symbols)}\n"
            for symbol in scope.get_all_symbols():
                content += f"    - {symbol.name}: {symbol.type_info}\n"
            content += "\n"
        
        self.scope_text.insert(1.0, content)
        self.scope_text.config(state='disabled')
    
    def _update_type_display(self, symbol_table: SymbolTable):
        """Update type analysis display."""
        self.type_text.config(state='normal')
        self.type_text.delete(1.0, tk.END)
        
        content = "TYPE ANALYSIS RESULTS\n" + "=" * 60 + "\n\n"
        
        # Collect all symbols
        all_symbols = []
        for scope in symbol_table.scopes:
            all_symbols.extend(scope.get_all_symbols())
        
        # Group by type
        types_dict = {}
        for symbol in all_symbols:
            type_str = str(symbol.type_info)
            if type_str not in types_dict:
                types_dict[type_str] = []
            types_dict[type_str].append(symbol.name)
        
        for type_str, names in sorted(types_dict.items()):
            content += f"{type_str}:\n"
            for name in names:
                content += f"  - {name}\n"
            content += "\n"
        
        self.type_text.insert(1.0, content)
        self.type_text.config(state='disabled')
    
    def _update_errors_display(self, error: str, error_type: str = "error"):
        """Update errors display with new error."""
        self.errors_text.config(state='normal')
        current = self.errors_text.get(1.0, tk.END)
        if "will update" in current:
            self.errors_text.delete(1.0, tk.END)
        
        prefix = "❌" if error_type == "error" else "⚠️"
        self.errors_text.insert(tk.END, f"{prefix} {error}\n")
        self.errors_text.see(tk.END)
        self.errors_text.config(state='disabled')
    
    def _update_all_errors_display(self, errors: List[str], warnings: List[str]):
        """Update all errors and warnings."""
        self.errors_text.config(state='normal')
        self.errors_text.delete(1.0, tk.END)
        
        content = "SEMANTIC ERRORS AND WARNINGS\n" + "=" * 60 + "\n\n"
        
        if errors:
            content += "ERRORS:\n"
            for error in errors:
                content += f"  ❌ {error}\n"
            content += "\n"
        else:
            content += "✅ No errors found!\n\n"
        
        if warnings:
            content += "WARNINGS:\n"
            for warning in warnings:
                content += f"  ⚠️ {warning}\n"
        else:
            content += "✅ No warnings found!\n"
        
        self.errors_text.insert(1.0, content)
        self.errors_text.config(state='disabled')
    
    def _update_steps_display(self, step: Dict[str, Any]):
        """Update analysis steps display."""
        self.steps_text.config(state='normal')
        current = self.steps_text.get(1.0, tk.END)
        if "will update" in current:
            self.steps_text.delete(1.0, tk.END)
        
        step_text = f"[{step['type']}] {step['description']}\n"
        step_text += f"    Symbols: {step['symbol_count']}, Errors: {step['error_count']}, "
        step_text += f"Warnings: {step['warning_count']}\n\n"
        
        self.steps_text.insert(tk.END, step_text)
        self.steps_text.see(tk.END)
        self.steps_text.config(state='disabled')
    
    def _update_summary(self, success: bool, stats: Dict[str, int], 
                       errors: List[str], warnings: List[str]):
        """Display summary dialog."""
        status = "✅ PASSED" if success else "❌ FAILED"
        summary = f"""
Semantic Analysis Summary
{'=' * 50}

Status: {status}

Statistics:
  • Total Symbols: {stats['total_symbols']}
  • Total Scopes: {stats['scopes']}
  • Errors: {len(errors)}
  • Warnings: {len(warnings)}

{'=' * 50}
"""
        messagebox.showinfo("Analysis Complete", summary)
    
    def _reset_analysis(self):
        """Reset analysis results."""
        self.current_tokens = []
        self.current_ast = None
        self.analysis_steps = []
        self.current_step = 0
        
        self.steps_text.config(state='normal')
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.insert(1.0, "Analysis Steps (will update during analysis)\n\n")
        self.steps_text.config(state='disabled')
        
        self.errors_text.config(state='normal')
        self.errors_text.delete(1.0, tk.END)
        self.errors_text.insert(1.0, "Semantic Errors and Warnings\n\n")
        self.errors_text.config(state='disabled')
        
        self.status_label.config(text="Ready")
    
    def _launch_intermediate_code(self):
        """Launch the intermediate code generation phase."""
        try:
            # Close this window temporarily
            self.root.withdraw()
            
            # Create a new root window for intermediate code generation
            intermediate_root = tk.Tk()
            
            # Create and run intermediate code generator
            intermediate_app = IntermediateCodeGUI(intermediate_root)
            intermediate_root.mainloop()
            
            # Show this window again
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Intermediate Code Generation: {str(e)}")
            self.root.deiconify()
    
    def _load_file(self):
        """Load code from file."""
        files = [('Python Files', '*.py'), ('Text Files', '*.txt'), ('All Files', '*.*')]
        filename = filedialog.askopenfilename(filetypes=files)
        if filename:
            try:
                with open(filename, 'r') as f:
                    code = f.read()
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(1.0, code)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def _save_file(self):
        """Save code to file."""
        code = self.input_text.get(1.0, tk.END)
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(code)
                messagebox.showinfo("Success", "Code saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def _clear_editor(self):
        """Clear the editor."""
        self.input_text.delete(1.0, tk.END)
    
    def _load_sample(self):
        """Load sample code."""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, self.sample_code)
    
    def _on_speed_changed(self, event=None):
        """Handle animation speed change."""
        speed = self.speed_var.get()
        if speed == "Slow":
            self.step_delay = 1.0
        elif speed == "Medium":
            self.step_delay = 0.5
        elif speed == "Fast":
            self.step_delay = 0.2
        else:  # Instant
            self.step_delay = 0
    
    def _bind_events(self):
        """Bind keyboard events."""
        self.root.bind('<Control-a>', lambda e: self._start_analysis())
        self.root.bind('<Control-r>', lambda e: self._reset_analysis())
    
    def _get_sample_code(self) -> str:
        """Get sample code for demonstration."""
        return """
// Simple Program - Sum of Two Numbers
hold num1 = 5;
hold num2 = 10;
hold total = num1 + num2;
show total;
"""

def run():
    """Run the semantic analysis GUI."""
    root = tk.Tk()
    app = SemanticAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run()
