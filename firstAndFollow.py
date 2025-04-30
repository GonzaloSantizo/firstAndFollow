import tkinter as tk
from tkinter import scrolledtext

# Global variables to store grammar, terminals, non-terminals, and FIRST/FOLLOW sets
grammar = {}
non_terminals = set()
terminals = set()
first_sets = {}
follow_sets = {}
entries = []

# Parse the grammar rules entered by the user
def parse_grammar():
    global grammar, non_terminals, terminals
    grammar = {}
    non_terminals = set()
    terminals = set()
    first_sets.clear()
    follow_sets.clear()
    for entry in entries:
        head = entry[0].get().strip()
        symbols = [e.get().strip() for e in entry[1:] if e.get().strip()]
        if head:
            non_terminals.add(head)
            grammar.setdefault(head, []).append(symbols)
            for symbol in symbols:
                if symbol and not symbol.isupper() and symbol != 'ε' and symbol not in terminals:
                    terminals.add(symbol)

# Compute the FIRST sets for all non-terminals
def compute_first():
    global first_sets
    first_sets = {}

    # Initialize FIRST sets for terminals and non-terminals
    for t in terminals:
        first_sets[t] = {t}
    for nt in non_terminals:
        first_sets[nt] = set()

    # Iteratively compute FIRST sets until no changes occur
    changed = True
    while changed:
        changed = False
        for head, productions in grammar.items():
            for production in productions:
                if not production or production == ['ε']:
                    if 'ε' not in first_sets[head]:
                        first_sets[head].add('ε')
                        changed = True
                    continue
                for i, symbol in enumerate(production):
                    symbol_first = set()
                    if symbol in terminals:
                        symbol_first = {symbol}
                    elif symbol in non_terminals:
                        symbol_first = first_sets.get(symbol, set()).copy()
                    else:
                        continue
                    original_size = len(first_sets[head])
                    first_sets[head].update(symbol_first - {'ε'})
                    if len(first_sets[head]) > original_size:
                        changed = True
                    if 'ε' not in symbol_first:
                        break
                else:
                    if 'ε' not in first_sets[head]:
                        first_sets[head].add('ε')
                        changed = True
    for nt in non_terminals:
        if nt not in first_sets:
            first_sets[nt] = set()

# Compute the FOLLOW sets for all non-terminals
def compute_follow():
    global follow_sets
    follow_sets = {nt: set() for nt in non_terminals}

    # Add '$' to the FOLLOW set of the start symbol
    start_symbol = None
    if entries:
        start_symbol = entries[0][0].get().strip()

    if start_symbol and start_symbol in follow_sets:
        follow_sets[start_symbol].add('$')

    # Iteratively compute FOLLOW sets until no changes occur
    changed = True
    while changed:
        changed = False
        for head, productions in grammar.items():
            for production in productions:
                trailer = follow_sets[head].copy()
                for i in range(len(production) - 1, -1, -1):
                    symbol = production[i]
                    if symbol in non_terminals:
                        original_size = len(follow_sets[symbol])
                        follow_sets[symbol].update(trailer)
                        if len(follow_sets[symbol]) > original_size:
                            changed = True
                        symbol_first = first_sets.get(symbol, set())
                        if 'ε' in symbol_first:
                            trailer.update(symbol_first - {'ε'})
                        else:
                            trailer = symbol_first.copy()
                    elif symbol in terminals:
                        trailer = {symbol}
                    else:
                        trailer = set()

# Calculate and display the FIRST sets
def calculate_first():
    parse_grammar()
    if not grammar:
        result_output.delete("1.0", tk.END)
        result_output.insert(tk.END, "Error: La gramática no está definida. Añade reglas.")
        return
    if not non_terminals:
       result_output.delete("1.0", tk.END)
       result_output.insert(tk.END, "Error: No se encontraron no terminales.")
       return

    compute_first()

    result_output.delete("1.0", tk.END)
    result_output.insert(tk.END, "--- Conjuntos FIRST ---\n")
    for non_terminal in sorted(list(non_terminals)):
        current_first_set = first_sets.get(non_terminal, set())
        sorted_first_set = sorted(list(current_first_set))
        result_output.insert(tk.END, f"FIRST({non_terminal}) = {{{', '.join(sorted_first_set)}}}\n")

# Calculate and display the FOLLOW sets
def calculate_follow():
    parse_grammar()
    if not grammar:
        result_output.delete("1.0", tk.END)
        result_output.insert(tk.END, "Error: La gramática no está definida. Añade reglas.")
        return
    if not non_terminals:
       result_output.delete("1.0", tk.END)
       result_output.insert(tk.END, "Error: No se encontraron no terminales.")
       return

    compute_first()
    compute_follow()

    result_output.delete("1.0", tk.END)
    result_output.insert(tk.END, "--- Conjuntos FOLLOW ---\n")
    for non_terminal in sorted(list(non_terminals)):
        current_follow_set = follow_sets.get(non_terminal, set())
        sorted_follow_set = sorted(list(current_follow_set))
        result_output.insert(tk.END, f"FOLLOW({non_terminal}) = {{{', '.join(sorted_follow_set)}}}\n")

# Add a new grammar rule input row
def add_rule():
    row = tk.Frame(rules_frame)
    row.pack(fill='x', pady=2)

    left_entry = tk.Entry(row, width=10)
    left_entry.pack(side='left', padx=5)
    left_entry.insert(0, "S" if not entries else "")

    tk.Label(row, text="→").pack(side='left')

    symbol_entries = []
    for i in range(5):
        entry = tk.Entry(row, width=8)
        entry.pack(side='left', padx=2)
        symbol_entries.append(entry)

    entries.append([left_entry] + symbol_entries)

# Initialize the GUI
root = tk.Tk()
root.title("Calculadora de FIRST y FOLLOW")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

instructions = tk.Label(frame, text="Define la gramática (No terminales en MAYÚSCULAS, 'ε' para epsilon):")
instructions.pack(pady=(0, 5))

rules_frame = tk.Frame(frame)
rules_frame.pack(fill='x', pady=5)

buttons_frame = tk.Frame(frame)
buttons_frame.pack(pady=10)

tk.Button(buttons_frame, text="Añadir regla", command=add_rule).pack(side='left', padx=5)

calculate_first_button = tk.Button(buttons_frame, text="Calcular FIRST", command=calculate_first)
calculate_first_button.pack(side='left', padx=5)

calculate_follow_button = tk.Button(buttons_frame, text="Calcular FOLLOW", command=calculate_follow)
calculate_follow_button.pack(side='left', padx=5)

add_rule()

tk.Label(frame, text="Resultados:").pack()

result_output = scrolledtext.ScrolledText(frame, height=15, width=60, wrap=tk.WORD)
result_output.pack()

root.mainloop()