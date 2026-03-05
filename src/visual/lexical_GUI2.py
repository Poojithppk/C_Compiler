"""
Advanced Visual Compiler – Lexical Analysis Phase
"""

import tkinter as tk
from tkinter import ttk, filedialog
import re


class LexicalAnalysisGUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Advanced Visual Compiler - Lexical Analysis Phase")
        self.root.geometry("1400x850")

        self.setup_ui()
        self.setup_syntax_highlighting()

    # ================= UI =================

    def setup_ui(self):

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = tk.Label(
            main_frame,
            text="LEXICAL ANALYSIS PHASE",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=5)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.setup_editor_tab()
        self.setup_token_tab()
        self.setup_results_tab()

        self.setup_control_panel(main_frame)

    # ================= EDITOR =================

    def setup_editor_tab(self):

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Source Code Editor")

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Load File", command=self.load_file).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Save File", command=self.save_file).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Clear", command=self.clear_editor).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Sample Code", command=self.load_sample).pack(side="left", padx=5)

        editor_frame = ttk.Frame(frame)
        editor_frame.pack(fill="both", expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=5,
            takefocus=0,
            border=0,
            background="#404040",
            foreground="#aaaaaa",
            state="disabled",
            font=("Consolas", 12)
        )
        self.line_numbers.pack(side="left", fill="y")

        # Editor
        self.source_text = tk.Text(
            editor_frame,
            wrap="none",
            font=("Consolas", 12),
            background="#1e1e1e",
            foreground="white",
            insertbackground="white"
        )
        self.source_text.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(editor_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.source_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.source_text.yview)

        # Events
        self.source_text.bind("<KeyRelease>", self.on_text_change)
        self.source_text.bind("<MouseWheel>", self.on_scroll)
        self.source_text.bind("<ButtonRelease>", self.highlight_current_line)

        self.load_sample()

    # ================= SCROLL =================

    def on_scroll(self, event=None):

        self.update_line_numbers()

    # ================= TOKEN TAB =================

    def setup_token_tab(self):

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Token Visualization")

        columns = ("Index", "Type", "Lexeme", "Line", "Column")

        self.token_table = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.token_table.heading(col, text=col)
            self.token_table.column(col, width=120)

        self.token_table.pack(fill="both", expand=True)

    # ================= RESULTS =================

    def setup_results_tab(self):

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Analysis Results")

        self.result_text = tk.Text(frame, height=10)
        self.result_text.pack(fill="both", expand=True)

    # ================= CONTROLS =================

    def setup_control_panel(self, parent):

        frame = ttk.LabelFrame(parent, text="Analysis Controls")
        frame.pack(fill="x", pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ttk.Button(button_frame, text="Start Analysis",
                   command=self.start_analysis).pack(side="left", padx=5)

        ttk.Button(button_frame, text="Reset",
                   command=self.reset_table).pack(side="left", padx=5)

    # ================= SYNTAX =================

    def setup_syntax_highlighting(self):

        self.source_text.tag_configure("keyword", foreground="#569CD6")
        self.source_text.tag_configure("string", foreground="#CE9178")
        self.source_text.tag_configure("number", foreground="#B5CEA8")
        self.source_text.tag_configure("comment", foreground="#6A9955")
        self.source_text.tag_configure("current_line", background="#2a2d2e")

    def highlight_syntax(self):

        code = self.source_text.get("1.0", tk.END)

        for tag in ["keyword", "string", "number", "comment"]:
            self.source_text.tag_remove(tag, "1.0", tk.END)

        keywords = ["var", "func", "if", "else", "for", "return",
                    "int", "float", "string", "bool", "print"]

        for word in keywords:
            start = "1.0"
            while True:
                pos = self.source_text.search(r"\m"+word+r"\M", start,
                                              stopindex=tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(word)}c"
                self.source_text.tag_add("keyword", pos, end)
                start = end

        for match in re.finditer(r'"[^"]*"', code):
            self.source_text.tag_add("string",
                                     f"1.0+{match.start()}c",
                                     f"1.0+{match.end()}c")

        for match in re.finditer(r"//.*", code):
            self.source_text.tag_add("comment",
                                     f"1.0+{match.start()}c",
                                     f"1.0+{match.end()}c")

        for match in re.finditer(r"\b\d+\b", code):
            self.source_text.tag_add("number",
                                     f"1.0+{match.start()}c",
                                     f"1.0+{match.end()}c")

    # ================= CURRENT LINE =================

    def highlight_current_line(self, event=None):

        self.source_text.tag_remove("current_line", "1.0", "end")
        self.source_text.tag_add("current_line",
                                 "insert linestart",
                                 "insert lineend+1c")

    # ================= LINE NUMBERS =================

    def update_line_numbers(self):

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)

        lines = self.source_text.get("1.0", tk.END).split("\n")

        for i in range(1, len(lines)):
            self.line_numbers.insert(tk.END, str(i) + "\n")

        self.line_numbers.config(state="disabled")

    # ================= EVENTS =================

    def on_text_change(self, event=None):

        self.update_line_numbers()
        self.highlight_syntax()
        self.highlight_current_line()

    # ================= LEXER =================

    def simple_lexer(self, code):

        token_specification = [
            ("COMMENT", r"//.*"),
            ("STRING", r'"[^"]*"'),
            ("NUMBER", r"\b\d+(\.\d+)?\b"),
            ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
        ]

        tok_regex = "|".join(
            f"(?P<{name}>{regex})" for name, regex in token_specification
        )

        tokens = []
        line = 1

        for match in re.finditer(tok_regex, code):

            kind = match.lastgroup
            value = match.group()

            tokens.append((kind, value, line, match.start()))

        return tokens

    # ================= ANALYSIS =================

    def start_analysis(self):

        code = self.source_text.get("1.0", tk.END)

        self.token_table.delete(*self.token_table.get_children())

        tokens = self.simple_lexer(code)

        for i, token in enumerate(tokens):

            self.token_table.insert(
                "",
                "end",
                values=(i, token[0], token[1], token[2], token[3])
            )

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", f"Total Tokens: {len(tokens)}")

    # ================= RESET =================

    def reset_table(self):

        self.token_table.delete(*self.token_table.get_children())
        self.result_text.delete("1.0", tk.END)

    # ================= FILE =================

    def load_file(self):

        file = filedialog.askopenfilename()

        if file:
            with open(file) as f:
                content = f.read()

            self.source_text.delete("1.0", tk.END)
            self.source_text.insert("1.0", content)

            self.update_line_numbers()
            self.highlight_syntax()

    def save_file(self):

        file = filedialog.asksaveasfilename(defaultextension=".txt")

        if file:
            content = self.source_text.get("1.0", tk.END)

            with open(file, "w") as f:
                f.write(content)

    def clear_editor(self):

        self.source_text.delete("1.0", tk.END)

    # ================= SAMPLE =================

    def load_sample(self):

        sample = """
// Sample Program
var x: int = 42;
var message: string = "Hello Compiler";

func square(n: int) -> int {
    return n * n;
}

if (x > 10) {
    print(message);
}
"""

        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", sample)

        self.update_line_numbers()
        self.highlight_syntax()

    # ================= RUN =================

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    app = LexicalAnalysisGUI()
    app.run()