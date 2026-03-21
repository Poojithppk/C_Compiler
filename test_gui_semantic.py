#!/usr/bin/env python3
"""
Test semantic analysis GUI
"""
import sys
import os
import tkinter as tk

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from semantic_analysis.semantic_gui import SemanticAnalysisGUI

def main():
    root = tk.Tk()
    app = SemanticAnalysisGUI(root)
    
    # Simulate clicking analyze
    print("Starting GUI...")
    print("Click 'Analyze' button to test semantic analysis")
    root.mainloop()

if __name__ == "__main__":
    main()
