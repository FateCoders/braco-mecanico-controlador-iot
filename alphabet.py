# alphabet.py

# Dicionário de letras.
# Cada letra é uma lista de "traços" (strokes).
# Cada traço é uma lista de coordenadas (x, y) normalizadas entre 0.0 e 1.0.

font = {
    'A': [
        [(0.0, 0.0), (0.5, 1.0), (1.0, 0.0)], # Traço 1: O "V" invertido
        [(0.2, 0.4), (0.8, 0.4)]              # Traço 2: O corte no meio
    ],
    'B': [
        [(0.0, 0.0), (0.0, 1.0), (0.8, 1.0), (0.8, 0.5), (0.0, 0.5)], # Parte de cima
        [(0.0, 0.5), (0.8, 0.5), (0.8, 0.0), (0.0, 0.0)]              # Parte de baixo
    ],
    'C': [
        [(1.0, 0.8), (0.8, 1.0), (0.2, 1.0), (0.0, 0.8), (0.0, 0.2), (0.2, 0.0), (0.8, 0.0), (1.0, 0.2)]
    ],
    'L': [
        [(0.0, 1.0), (0.0, 0.0), (0.8, 0.0)]
    ],
    'O': [
        [(0.5, 1.0), (0.1, 0.8), (0.0, 0.5), (0.1, 0.2), (0.5, 0.0), (0.9, 0.2), (1.0, 0.5), (0.9, 0.8), (0.5, 1.0)]
    ],
    'X': [
        [(0.0, 1.0), (1.0, 0.0)],
        [(1.0, 1.0), (0.0, 0.0)]
    ],
    ' ': [] # Espaço em branco
}

def get_char(char):
    return font.get(char.upper(), []) # Retorna vazio se não achar a letra