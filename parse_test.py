#!/usr/bin/env python3
"""Test parser to understand file structure"""

with open('02/03/2026.txt', 'r', encoding='utf-8') as f:
    # Read first few lines to understand structure
    lines = []
    for i in range(15):
        line = f.readline()
        if not line:
            break
        lines.append(line)
    
    print("First 15 lines:")
    for i, line in enumerate(lines):
        print(f"\nLine {i}:")
        print(f"  Raw: {repr(line[:150])}")
        print(f"  Tabs: {line.count(chr(9))}")
        print(f"  Starts with tab: {line.startswith(chr(9))}")
        if '"' in line:
            print(f"  Has quotes: Yes")
            quote_pos = [j for j, c in enumerate(line) if c == '"']
            print(f"  Quote positions: {quote_pos}")
