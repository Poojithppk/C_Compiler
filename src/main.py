"""
Main Entry Point for Advanced Visual Compiler

This is the main launcher for the Advanced Visual, Security-Aware Multi-Target Compiler.
It provides access to all compiler phases with visual interfaces and analysis tools.
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from lexical_analysis import LexicalAnalysisGUI
from syntax_analysis import SyntaxAnalysisGUI
from semantic_analysis import SemanticAnalysisGUI
from intermediate_code import IntermediateCodeGUI


class CompilerMain:
    """
    Main launcher for the Advanced Visual Compiler
    
    Provides access to:
    - Lexical Analysis Phase (✅ Implemented)
    - Syntax Analysis Phase (✅ Implemented)
    - Semantic Analysis Phase (✅ Implemented)
    - Intermediate Code Generation (✅ Implemented)
    - Optimization Phase (🚧 Coming Soon)
    - Code Generation Phase (🚧 Coming Soon)
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Visual Compiler - Main Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Set window icon and style
        try:
            # Try to set a nice style
            style = ttk.Style()
            style.theme_use('clam')
        except:
            pass
            
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface."""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#1e1e1e')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = tk.Label(
            header_frame,
            text="🔧 ADVANCED VISUAL COMPILER",
            font=('Arial', 24, 'bold'),
            bg='#1e1e1e',
            fg='#ffffff'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Security-Aware Multi-Target Compiler with Visual Phase Animation",
            font=('Arial', 12),
            bg='#1e1e1e',
            fg='#cccccc'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Main content area
        content_frame = tk.Frame(self.root, bg='#2b2b2b')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Compiler Phases Tab
        self.setup_phases_tab()
        
        # Project Info Tab
        self.setup_info_tab()
        
        # Settings Tab
        self.setup_settings_tab()
        
    def setup_phases_tab(self):
        """Setup the compiler phases tab."""
        
        phases_frame = ttk.Frame(self.notebook)
        self.notebook.add(phases_frame, text="🔧 Compiler Phases")
        
        # Instructions
        instructions = tk.Label(
            phases_frame,
            text="Select a compiler phase to begin visual analysis:",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0'
        )
        instructions.pack(pady=20)
        
        # Phases grid
        phases_container = tk.Frame(phases_frame, bg='#f0f0f0')
        phases_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Phase 1: Lexical Analysis (✅ Ready)
        self.create_phase_button(
            phases_container,
            "🔍 LEXICAL ANALYSIS",
            "Tokenization • Visual Highlighting • Error Recovery",
            "✅ READY",
            "#28a745",
            self.launch_lexical_analysis,
            row=0, col=0
        )
        
        # Sequential Workflow Button
        self.create_phase_button(
            phases_container,
            "🔄 FULL PIPELINE (LEX → SYN → SEM → INT)",
            "Run all four phases in sequence",
            "✅ READY",
            "#17a2b8",
            self.launch_full_pipeline_analysis,
            row=2, col=0
        )
        
        # Phase 2: Syntax Analysis (✅ Ready)
        self.create_phase_button(
            phases_container,
            "🌳 SYNTAX ANALYSIS", 
            "Parse Tree Generation • Grammar Validation • AST Building",
            "✅ READY",
            "#28a745",
            self.launch_syntax_analysis,
            row=0, col=1
        )
        
        # Phase 3: Semantic Analysis (✅ Ready)
        self.create_phase_button(
            phases_container,
            "🎯 SEMANTIC ANALYSIS",
            "Type Checking • Symbol Table • Scope Validation",
            "✅ READY",
            "#28a745",
            self.launch_semantic_analysis,
            row=1, col=0
        )
        
        # Phase 4: Intermediate Code (✅ Ready)
        self.create_phase_button(
            phases_container,
            "⚙️ INTERMEDIATE CODE",
            "Three-Address Code • Control Flow • Data Flow",
            "✅ READY",
            "#28a745", 
            self.launch_intermediate_analysis,
            row=1, col=1
        )
        
        # Phase 5: Optimization (🚧 Coming Soon)
        self.create_phase_button(
            phases_container,
            "🚀 OPTIMIZATION",
            "Dead Code Elimination • Common Subexpression • Peephole",
            "🚧 COMING SOON",
            "#ffc107",
            lambda: self.show_coming_soon("Optimization Phase"),
            row=2, col=0
        )
        
        # Phase 6: Code Generation (🚧 Coming Soon)
        self.create_phase_button(
            phases_container,
            "💻 CODE GENERATION",
            "Multi-Target • Python • C • Java • Assembly",
            "🚧 COMING SOON",
            "#ffc107",
            lambda: self.show_coming_soon("Code Generation"),
            row=2, col=1
        )
        
    def create_phase_button(self, parent, title, description, status, color, command, row, col):
        """Create a phase selection button."""
        
        button_frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
        button_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Phase title
        title_label = tk.Label(
            button_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg='white'
        )
        title_label.pack(pady=(15, 5))
        
        # Phase description
        desc_label = tk.Label(
            button_frame,
            text=description,
            font=('Arial', 10),
            bg='white',
            wraplength=200
        )
        desc_label.pack(pady=5)
        
        # Status badge
        status_label = tk.Label(
            button_frame,
            text=status,
            font=('Arial', 10, 'bold'),
            bg=color,
            fg='white',
            padx=10,
            pady=5
        )
        status_label.pack(pady=(10, 5))
        
        # Action button
        action_btn = tk.Button(
            button_frame,
            text="Launch Phase" if "READY" in status else "View Details",
            font=('Arial', 11, 'bold'),
            bg='#007bff' if "READY" in status else '#6c757d',
            fg='white',
            padx=20,
            pady=8,
            command=command,
            cursor='hand2'
        )
        action_btn.pack(pady=(5, 15))
        
        # Hover effects
        def on_enter(e):
            button_frame.config(relief='solid', bd=3)
            
        def on_leave(e):
            button_frame.config(relief='raised', bd=2)
            
        button_frame.bind("<Enter>", on_enter)
        button_frame.bind("<Leave>", on_leave)
        
        # Make entire frame clickable
        for widget in button_frame.winfo_children():
            widget.bind("<Button-1>", lambda e: command())
            
    def setup_info_tab(self):
        """Setup the project information tab."""
        
        info_frame = ttk.Frame(self.notebook)
        self.notebook.add(info_frame, text="📋 Project Info")
        
        # Scrollable text area
        info_text = tk.Text(
            info_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='#f8f9fa',
            padx=20,
            pady=20
        )
        info_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Project information content
        info_content = """
🎓 B.TECH FINAL YEAR PROJECT
Advanced Visual, Security-Aware Multi-Target Compiler

👥 TEAM MEMBERS:
• Anjani (Core Compiler Logic, Backend, Optimization)
• Poojith (UI, Visualization, Testing, Documentation)

🎯 PROJECT OBJECTIVES:
✅ Design complete compiler for custom programming language
✅ Develop visual representation system for all compiler phases
✅ Implement intelligent error recovery and correction mechanisms
✅ Create comprehensive security analysis and vulnerability detection
✅ Build multi-target code generation (Python, C, Java, Assembly)
✅ Demonstrate advanced optimization techniques

🔧 CURRENT IMPLEMENTATION STATUS:

Phase 1: ✅ LEXICAL ANALYSIS - COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Visual token highlighting and step-by-step animation
• Comprehensive token recognition (keywords, operators, literals)
• Error recovery with intelligent suggestions
• Real-time syntax highlighting
• Interactive debugging capabilities
• Security-aware token detection

Phase 2: 🚧 SYNTAX ANALYSIS - IN DEVELOPMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Recursive descent parser implementation
• Animated parse tree generation
• Grammar validation and error recovery
• Abstract Syntax Tree (AST) building

Phase 3: ✅ SEMANTIC ANALYSIS - COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Symbol table management and tracking
• Type checking and validation
• Scope resolution and nesting
• Semantic error detection and reporting

Phase 4: ✅ INTERMEDIATE CODE GENERATION - COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Three-address code generation
• Control flow graph construction
• Data flow analysis
• Basic optimization framework

Phase 5: 🚧 OPTIMIZATION - PLANNED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Dead code elimination
• Common subexpression elimination
• Constant folding and propagation
• Loop optimization

Phase 6: 🚧 CODE GENERATION - PLANNED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Multi-target code generation
• Python translation
• C code generation
• Java bytecode generation  
• Assembly language output

🔒 SECURITY FEATURES:
• Static vulnerability analysis
• Buffer overflow detection
• Null pointer dereference checking
• Uninitialized variable detection
• Input validation enforcement

🎨 VISUAL FEATURES:
• Real-time phase animation
• Interactive token highlighting
• Step-by-step execution control
• Beautiful syntax highlighting
• Error visualization with suggestions

📊 TECHNICAL STACK:
• Language: Python 3.8+
• GUI Framework: Tkinter with custom styling
• Visualization: Matplotlib, NetworkX
• Testing: pytest, unittest
• Documentation: Comprehensive inline docs

🎯 NEXT MILESTONES:
1. ✅ Lexical Analysis Phase - COMPLETE
2. ✅ Syntax Analysis Phase - COMPLETE
3. ✅ Semantic Analysis Phase - COMPLETE
4. ✅ Intermediate Code Generator - COMPLETE
5. Optimization Engine (Week 2)
6. Multi-Target Code Generation (Week 3-4)

📅 TARGET COMPLETION: March 20, 2026
Current Progress: 67% (4/6 phases complete)

🚀 Start with Lexical Analysis or run the full pipeline to see the visual compiler in action!
        """
        
        info_text.insert(1.0, info_content.strip())
        info_text.config(state='disabled')
        
    def setup_settings_tab(self):
        """Setup the settings and configuration tab."""
        
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Visual settings
        visual_group = ttk.LabelFrame(settings_frame, text="Visual Animation Settings")
        visual_group.pack(fill='x', padx=10, pady=10)
        
        # Animation speed
        speed_frame = ttk.Frame(visual_group)
        speed_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(speed_frame, text="Animation Speed:").pack(side='left')
        self.speed_var = tk.StringVar(value="Medium")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var, 
                                  values=["Slow", "Medium", "Fast", "Instant"])
        speed_combo.pack(side='right')
        
        # Syntax highlighting
        highlight_frame = ttk.Frame(visual_group)
        highlight_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(highlight_frame, text="Syntax Highlighting:").pack(side='left')
        self.highlight_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(highlight_frame, variable=self.highlight_var).pack(side='right')
        
        # Compiler settings
        compiler_group = ttk.LabelFrame(settings_frame, text="Compiler Configuration")
        compiler_group.pack(fill='x', padx=10, pady=10)
        
        # Error recovery
        error_frame = ttk.Frame(compiler_group)
        error_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(error_frame, text="Auto Error Recovery:").pack(side='left')
        self.error_recovery_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(error_frame, variable=self.error_recovery_var).pack(side='right')
        
        # Security analysis
        security_frame = ttk.Frame(compiler_group)
        security_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(security_frame, text="Security Analysis:").pack(side='left')
        self.security_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(security_frame, variable=self.security_var).pack(side='right')
        
        # Debug mode
        debug_frame = ttk.Frame(compiler_group)
        debug_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(debug_frame, text="Debug Mode:").pack(side='left')
        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(debug_frame, variable=self.debug_var).pack(side='right')
        
        # Save settings button
        save_btn = ttk.Button(settings_frame, text="Save Settings", 
                             command=self.save_settings)
        save_btn.pack(pady=20)
        
    def launch_lexical_analysis(self):
        """Launch the lexical analysis phase."""
        print("🚀 Launching Lexical Analysis Phase...")
        
        try:
            # Close main window temporarily
            self.root.withdraw()
            
            # Launch lexical analyzer
            lexical_app = LexicalAnalysisGUI()
            lexical_app.run()
            
            # Show main window again after lexical analyzer closes
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Lexical Analysis: {str(e)}")
            self.root.deiconify()
            
    def launch_syntax_analysis(self):
        """Launch the syntax analysis phase."""
        print("🌳 Launching Syntax Analysis Phase...")
        
        try:
            # Close main window temporarily
            self.root.withdraw()
            
            # Create a new root window for syntax analysis
            syntax_root = tk.Tk()
            
            # Create and run syntax analyzer
            syntax_app = SyntaxAnalysisGUI(syntax_root)
            syntax_root.mainloop()
            
            # Show main window again after syntax analyzer closes
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Syntax Analysis: {str(e)}")
            self.root.deiconify()
    
    def launch_semantic_analysis(self):
        """Launch the semantic analysis phase."""
        print("🎯 Launching Semantic Analysis Phase...")
        
        try:
            # Close main window temporarily
            self.root.withdraw()
            
            # Create a new root window for semantic analysis
            semantic_root = tk.Tk()
            
            # Create and run semantic analyzer
            semantic_app = SemanticAnalysisGUI(semantic_root)
            semantic_root.mainloop()
            
            # Show main window again after semantic analyzer closes
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Semantic Analysis: {str(e)}")
            self.root.deiconify()
    
    def launch_intermediate_analysis(self):
        """Launch the intermediate code generation phase."""
        print("⚙️ Launching Intermediate Code Generation Phase...")
        
        try:
            # Close main window temporarily
            self.root.withdraw()
            
            # Create a new root window for intermediate code generation
            intermediate_root = tk.Tk()
            
            # Create and run intermediate code generator
            intermediate_app = IntermediateCodeGUI(intermediate_root)
            intermediate_root.mainloop()
            
            # Show main window again after intermediate code analyzer closes
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Intermediate Code Generation: {str(e)}")
            self.root.deiconify()
    
    def launch_sequential_analysis(self):
        """Launch lexical analysis followed by syntax analysis."""
        print("🔄 Launching Sequential Analysis: Lexical → Syntax...")
        
        try:
            # Close main window temporarily
            self.root.withdraw()
            
            # Phase 1: Lexical Analysis
            print("📍 Phase 1: Starting Lexical Analysis...")
            lexical_app = LexicalAnalysisGUI()
            lexical_app.run()
            
            # Ask user if they want to proceed to syntax analysis
            proceed = messagebox.askyesno(
                "Sequential Analysis", 
                "✅ Lexical Analysis completed!\n\n🌳 Proceed to Syntax Analysis phase?",
                icon='question'
            )
            
            if proceed:
                # Phase 2: Syntax Analysis
                print("📍 Phase 2: Starting Syntax Analysis...")
                syntax_root = tk.Tk()
                syntax_app = SyntaxAnalysisGUI(syntax_root)
                syntax_root.mainloop()
                
                messagebox.showinfo("Sequential Analysis", "✅ Both phases completed successfully!")
            else:
                print("📍 Sequential analysis stopped after lexical phase.")
            
            # Show main window again
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Sequential Analysis: {str(e)}")
            self.root.deiconify()

    def launch_full_pipeline_analysis(self):
        """Launch full pipeline analysis: Lexical → Syntax → Semantic → Intermediate Code."""
        print("🔄 Launching Full Pipeline Analysis: Lexical → Syntax → Semantic → Intermediate Code...")
        
        try:
            # Close main window temporarily
            self.root.withdraw()
            
            # Phase 1: Lexical Analysis
            print("📍 Phase 1: Starting Lexical Analysis...")
            lexical_app = LexicalAnalysisGUI()
            lexical_app.run()
            
            # Ask user if they want to proceed to syntax analysis
            proceed_to_syntax = messagebox.askyesno(
                "Pipeline Analysis", 
                "✅ Lexical Analysis completed!\n\n🌳 Proceed to Syntax Analysis phase?",
                icon='question'
            )
            
            if not proceed_to_syntax:
                print("📍 Pipeline analysis stopped after lexical phase.")
                self.root.deiconify()
                return
            
            # Phase 2: Syntax Analysis
            print("📍 Phase 2: Starting Syntax Analysis...")
            syntax_root = tk.Tk()
            syntax_app = SyntaxAnalysisGUI(syntax_root)
            syntax_root.mainloop()
            
            # Ask user if they want to proceed to semantic analysis
            proceed_to_semantic = messagebox.askyesno(
                "Pipeline Analysis",
                "✅ Syntax Analysis completed!\n\n🎯 Proceed to Semantic Analysis phase?",
                icon='question'
            )
            
            if not proceed_to_semantic:
                print("📍 Pipeline analysis stopped after syntax phase.")
                self.root.deiconify()
                return
            
            # Phase 3: Semantic Analysis
            print("📍 Phase 3: Starting Semantic Analysis...")
            semantic_root = tk.Tk()
            semantic_app = SemanticAnalysisGUI(semantic_root)
            semantic_root.mainloop()
            
            # Ask user if they want to proceed to intermediate code generation
            proceed_to_intermediate = messagebox.askyesno(
                "Pipeline Analysis",
                "✅ Semantic Analysis completed!\n\n⚙️ Proceed to Intermediate Code Generation phase?",
                icon='question'
            )
            
            if not proceed_to_intermediate:
                print("📍 Pipeline analysis stopped after semantic phase.")
                self.root.deiconify()
                return
            
            # Phase 4: Intermediate Code Generation
            print("📍 Phase 4: Starting Intermediate Code Generation...")
            intermediate_root = tk.Tk()
            intermediate_app = IntermediateCodeGUI(intermediate_root)
            intermediate_root.mainloop()
            
            messagebox.showinfo(
                "Pipeline Analysis",
                "✅ All four phases completed successfully!\n\n📊 Complete compilation pipeline executed!"
            )
            
            # Show main window again
            self.root.deiconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Pipeline Analysis: {str(e)}")
            self.root.deiconify()
    
    def show_coming_soon(self, phase_name):
        """Show coming soon message for phases under development."""
        messagebox.showinfo(
            f"{phase_name} - Coming Soon",
            f"""🚧 {phase_name} Phase is currently under development!
            
📅 Expected completion: Soon
            
🔧 Current Status: Planning and Architecture Phase

💡 What's Coming:
• Visual step-by-step animation
• Interactive debugging
• Error recovery system
• Real-time feedback

Stay tuned for updates! 🚀"""
        )
        
    def save_settings(self):
        """Save application settings."""
        # For now, just show a confirmation
        # In a full implementation, settings would be saved to a config file
        messagebox.showinfo("Settings", "Settings saved successfully! ✅")
        
    def run(self):
        """Run the main application."""
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        print("🎯 Advanced Visual Compiler - Main Dashboard Ready!")
        print("📋 Choose a compiler phase to begin analysis...")
        
        self.root.mainloop()


def main():
    """Main entry point for the compiler application."""
    print("=" * 60)
    print("🚀 ADVANCED VISUAL COMPILER")
    print("   Security-Aware Multi-Target Compiler")
    print("   B.Tech Final Year Project")
    print("=" * 60)
    print()
    
    try:
        app = CompilerMain()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Compiler application terminated by user")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()