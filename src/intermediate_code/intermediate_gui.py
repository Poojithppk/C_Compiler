"""
Visual Intermediate Code Generation GUI for NEXUS Language

This module provides a graphical interface for visualizing the intermediate code generation phase,
showing three-address code generation, control flow graphs, and optimization analysis.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import List, Optional, Dict, Any
import threading
import time
import os

# Import intermediate code components
from .intermediate_code_generator import IntermediateCodeGenerator
from .intermediate_symbols import TACCode, ControlFlowGraph, InstructionType

# Import lexical, syntax, and semantic components
try:
    from lexical_analysis.lexer import VisualLexicalAnalyzer
    from lexical_analysis.tokens import Token, TokenType
    from syntax_analysis.parser import Parser, ParseError
    from syntax_analysis.ast_nodes import ASTNode
    from syntax_analysis.ast_printer import ASTPrinter
    from semantic_analysis.semantic import SemanticAnalyzer
except ImportError as e:
    print(f"Warning: Could not import dependencies: {e}")


class IntermediateCodeGUI:
    """Visual interface for intermediate code generation phase."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NEXUS Compiler - Intermediate Code Generation Phase")
        self.root.geometry("1500x1000")
        self.root.configure(bg='#2b2b2b')
        
        # Analysis components
        self.lexer = VisualLexicalAnalyzer(visual_mode=False)
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer(visual_mode=False)
        self.intermediate_generator = IntermediateCodeGenerator(visual_mode=True)
        
        self.current_tokens = []
        self.current_ast = None
        self.semantic_result = None
        self.tac_code: Optional[TACCode] = None
        self.cfg: Optional[ControlFlowGraph] = None
        self.generation_steps = []
        self.current_step = 0
        
        # State
        self.is_analyzing = False
        self.is_running_sequential = False
        self.input_from_semantic = None
        
        # Setup UI
        self.setup_ui()
        self.load_sample_code()
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Header
        header_frame = tk.Frame(self.root, bg='#1e1e1e')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = tk.Label(
            header_frame,
            text="⚙️ INTERMEDIATE CODE GENERATION",
            font=('Arial', 18, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        title_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Input
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Code input
        code_label = ttk.Label(left_frame, text="📄 Source Code")
        code_label.pack()
        
        self.code_input = scrolledtext.ScrolledText(
            left_frame,
            height=15,
            width=50,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#00ff00',
            insertbackground='white'
        )
        self.code_input.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📂 Open File", command=self.open_file).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="🔄 Clear", command=self.clear_code).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="▶️ Generate", command=self.generate_intermediate_code).pack(side='left', padx=2)
        
        # Right panel - Output and Analysis
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Notebook for different views
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # TAC Code tab
        tac_frame = ttk.Frame(self.notebook)
        self.notebook.add(tac_frame, text="📝 3-Address Code")
        
        self.tac_output = scrolledtext.ScrolledText(
            tac_frame,
            height=20,
            width=60,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        self.tac_output.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Control Flow Graph tab
        cfg_frame = ttk.Frame(self.notebook)
        self.notebook.add(cfg_frame, text="🌳 Control Flow Graph")
        
        self.cfg_output = scrolledtext.ScrolledText(
            cfg_frame,
            height=20,
            width=60,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        self.cfg_output.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Analysis Steps tab
        steps_frame = ttk.Frame(self.notebook)
        self.notebook.add(steps_frame, text="📊 Generation Steps")
        
        self.steps_output = scrolledtext.ScrolledText(
            steps_frame,
            height=20,
            width=60,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        self.steps_output.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Statistics tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 Statistics")
        
        self.stats_output = scrolledtext.ScrolledText(
            stats_frame,
            height=20,
            width=60,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#ffff00'
        )
        self.stats_output.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Errors/Warnings tab
        errors_frame = ttk.Frame(self.notebook)
        self.notebook.add(errors_frame, text="⚠️ Errors & Warnings")
        
        self.errors_output = scrolledtext.ScrolledText(
            errors_frame,
            height=20,
            width=60,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#ff6b6b'
        )
        self.errors_output.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#1e1e1e', height=30)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            status_frame,
            text="✅ Ready",
            font=('Arial', 10),
            bg='#1e1e1e',
            fg='#00ff00',
            padx=10
        )
        self.status_label.pack(side='left')
        
        self.progress_label = tk.Label(
            status_frame,
            text="",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#cccccc'
        )
        self.progress_label.pack(side='right', padx=10)
    
    def load_sample_code(self):
        """Load sample code into editor."""
        sample_code = '''hold num1 = 5;
hold num2 = 10;
hold total = num1 + num2;
show total;
'''
        self.code_input.insert(1.0, sample_code)
    
    def open_file(self):
        """Open source file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("NEXUS files", "*.nxs"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                self.code_input.delete(1.0, tk.END)
                self.code_input.insert(1.0, code)
                self.update_status(f"✅ Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def clear_code(self):
        """Clear all text."""
        self.code_input.delete(1.0, tk.END)
        self.update_status("✅ Cleared")
    
    def generate_intermediate_code(self):
        """Generate intermediate code from source."""
        code = self.code_input.get(1.0, tk.END).strip()
        
        if not code:
            messagebox.showwarning("Warning", "Please enter source code first")
            return
        
        # Run in background thread
        thread = threading.Thread(target=self._generate_thread, args=(code,))
        thread.daemon = True
        thread.start()
    
    def _generate_thread(self, code: str):
        """Background thread for generation."""
        try:
            self.is_analyzing = True
            self.update_status("⏳ Analyzing: Lexical...")
            
            # Phase 1: Lexical Analysis
            self.lexer = VisualLexicalAnalyzer(visual_mode=False)
            self.current_tokens, lex_errors = self.lexer.analyze(code)
            
            if lex_errors:
                self.show_errors("Lexical Analysis Errors", lex_errors)
                self.is_analyzing = False
                return
            
            self.update_status("⏳ Analyzing: Syntax...")
            
            # Phase 2: Syntax Analysis
            try:
                self.parser = Parser(self.current_tokens, debug_mode=False)
                self.current_ast = self.parser.parse()
            except Exception as e:
                self.show_errors("Syntax Analysis Error", [str(e)])
                self.is_analyzing = False
                return
            
            self.update_status("⏳ Analyzing: Semantic...")
            
            # Phase 3: Semantic Analysis
            self.semantic_analyzer = SemanticAnalyzer(visual_mode=False)
            sem_success, sem_errors, sem_warnings = self.semantic_analyzer.analyze(self.current_ast)
            
            if not sem_success:
                self.show_errors("Semantic Analysis Errors", sem_errors)
                self.is_analyzing = False
                return
            
            self.update_status("⏳ Generating: Intermediate Code...")
            
            # Phase 4: Intermediate Code Generation
            self.intermediate_generator.set_visual_callback(self.on_generation_step)
            gen_success, self.tac_code, gen_errors = self.intermediate_generator.generate(self.current_ast)
            
            if not gen_success:
                self.show_errors("Generation Errors", gen_errors)
                self.is_analyzing = False
                return
            
            # Get CFG
            self.cfg = self.intermediate_generator.cfg
            
            # Display results
            self.display_tac_code()
            self.display_cfg()
            self.display_steps()
            self.display_statistics()
            self.display_errors_warnings()
            
            self.update_status("✅ Generation Complete")
            self.is_analyzing = False
            
        except Exception as e:
            self.show_errors("Fatal Error", [str(e)])
            self.is_analyzing = False
    
    def display_tac_code(self):
        """Display generated three-address code."""
        self.tac_output.delete(1.0, tk.END)
        
        content = "THREE-ADDRESS CODE GENERATION\n"
        content += "=" * 50 + "\n\n"
        content += self.tac_code.get_instructions_text()
        
        self.tac_output.insert(1.0, content)
    
    def display_cfg(self):
        """Display control flow graph."""
        self.cfg_output.delete(1.0, tk.END)
        
        content = "CONTROL FLOW GRAPH\n"
        content += "=" * 50 + "\n\n"
        
        for block in self.cfg.get_blocks_list():
            content += f"\nBlock: {block.id}\n"
            content += "-" * 30 + "\n"
            content += block.get_instructions_text() + "\n"
            content += f"Successors: {[s.id for s in block.successors]}\n"
        
        self.cfg_output.insert(1.0, content)
    
    def display_steps(self):
        """Display generation steps."""
        self.steps_output.delete(1.0, tk.END)
        
        content = "GENERATION STEPS\n"
        content += "=" * 50 + "\n\n"
        
        for i, step in enumerate(self.generation_steps, 1):
            content += f"{i}. {step['type']}\n"
            content += f"   {step['description']}\n"
            content += f"   Instructions: {step['instruction_count']}\n"
            content += f"   Errors: {step['error_count']}, Warnings: {step['warning_count']}\n\n"
        
        self.steps_output.insert(1.0, content)
    
    def display_statistics(self):
        """Display statistics."""
        self.stats_output.delete(1.0, tk.END)
        
        stats = self.intermediate_generator.get_statistics()
        
        content = "STATISTICS\n"
        content += "=" * 50 + "\n\n"
        content += f"Generated Instructions: {stats['instructions']}\n"
        content += f"Temporary Variables: {stats['temporaries']}\n"
        content += f"Labels Created: {stats['labels']}\n"
        content += f"Basic Blocks: {stats['blocks']}\n"
        content += f"Errors: {stats['errors']}\n"
        content += f"Warnings: {stats['warnings']}\n"
        
        self.stats_output.insert(1.0, content)
    
    def display_errors_warnings(self):
        """Display errors and warnings."""
        self.errors_output.delete(1.0, tk.END)
        
        content = "ERRORS & WARNINGS\n"
        content += "=" * 50 + "\n\n"
        
        if self.tac_code.errors:
            content += "ERRORS:\n"
            for error in self.tac_code.errors:
                content += f"  ❌ {error}\n"
            content += "\n"
        
        if self.tac_code.warnings:
            content += "WARNINGS:\n"
            for warning in self.tac_code.warnings:
                content += f"  ⚠️ {warning}\n"
        
        if not self.tac_code.errors and not self.tac_code.warnings:
            content += "✅ No errors or warnings\n"
        
        self.errors_output.insert(1.0, content)
    
    def on_generation_step(self, step: Dict[str, Any]):
        """Callback for generation steps."""
        self.generation_steps.append(step)
        progress = f"Step {len(self.generation_steps)}: {step['type']}"
        self.progress_label.config(text=progress)
        self.root.update()
    
    def show_errors(self, title: str, errors: List[str]):
        """Show error dialog."""
        error_msg = "\n".join(errors)
        messagebox.showerror(title, error_msg)
    
    def update_status(self, message: str):
        """Update status bar."""
        self.status_label.config(text=message)
        self.root.update()
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def main():
    """Run the intermediate code generation GUI."""
    root = tk.Tk()
    app = IntermediateCodeGUI(root)
    app.run()


if __name__ == "__main__":
    main()
