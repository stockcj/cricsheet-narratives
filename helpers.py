'''
Helper functions
'''

def break_string(text: str, max_length: int, names: bool = False):
    lines = []
    current_line = ""
    if names:
        words = text.split(", ")
        for i, word in enumerate(words):
            if i == 0:
                current_line += word
            elif len(current_line) + len(", ") + len(word) <= max_length:
                current_line += ", " + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    else:
        words = text.split()
        for word in words:
            if len(current_line) + len(word) <= max_length:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())
    return "\n".join(lines)