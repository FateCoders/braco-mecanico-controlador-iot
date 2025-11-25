# interface.py
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def criar_interface(root, callbacks):
    widgets = {} 
    
    # Validação de números
    def validar_numero(P):
        if P == "" or P == "-": return True
        try:
            float(P); return True 
        except ValueError: return False 
    vcmd = (root.register(validar_numero), '%P')

    # --- Layout Principal ---
    root.grid_columnconfigure(0, weight=3) 
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # === ESQUERDA: Plot 3D ===
    frame_plot = ttk.Frame(root, padding=10)
    frame_plot.grid(row=0, column=0, sticky="nsew") 
    
    fig = plt.figure(figsize=(5, 5)) 
    ax = fig.add_subplot(111, projection='3d')
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    widgets["canvas"] = canvas
    widgets["ax"] = ax

    # === DIREITA: Controles ===
    main_control_frame = ttk.Frame(root, padding=10)
    main_control_frame.grid(row=0, column=1, sticky="nsew")

    # 1. Conexão
    frame_conexao = ttk.LabelFrame(main_control_frame, text="Conexão", padding=5)
    frame_conexao.pack(fill='x', pady=5)
    
    frame_line1 = ttk.Frame(frame_conexao)
    frame_line1.pack(fill='x')
    ttk.Label(frame_line1, text="Porta:").pack(side='left')
    entry_porta = ttk.Entry(frame_line1, width=10)
    entry_porta.insert(0, "COM3")
    entry_porta.pack(side='left', padx=5)
    widgets["entry_porta_com"] = entry_porta
    
    btn_con = ttk.Button(frame_line1, text="Conectar", command=callbacks["toggle_conexao"])
    btn_con.pack(side='left', fill='x', expand=True)
    widgets["btn_toggle_conexao"] = btn_con
    
    lbl_status = ttk.Label(frame_conexao, text="Desconectado", foreground="red")
    lbl_status.pack()
    widgets["label_status"] = lbl_status

    # 2. Posição Atual e Calibração Z
    frame_pos = ttk.LabelFrame(main_control_frame, text="Posição / Calibração", padding=5)
    frame_pos.pack(fill='x', pady=5)
    
    lbl_coord = ttk.Label(frame_pos, text="X=0.0, Y=0.0, Z=0.0")
    lbl_coord.pack()
    widgets["label_coord"] = lbl_coord
    
    btn_calib_z = ttk.Button(frame_pos, text="Definir Z Atual como Papel", command=callbacks["calibrar_z"])
    btn_calib_z.pack(fill='x', pady=2)

    # 3. Mover por Coordenadas
    frame_move = ttk.LabelFrame(main_control_frame, text="Mover (cm)", padding=5)
    frame_move.pack(fill='x', pady=5)
    
    f_xyz = ttk.Frame(frame_move)
    f_xyz.pack(fill='x')
    
    widgets["entry_x"] = ttk.Entry(f_xyz, width=5, validate="key", validatecommand=vcmd)
    widgets["entry_y"] = ttk.Entry(f_xyz, width=5, validate="key", validatecommand=vcmd)
    widgets["entry_z"] = ttk.Entry(f_xyz, width=5, validate="key", validatecommand=vcmd)
    
    ttk.Label(f_xyz, text="X:").pack(side='left'); widgets["entry_x"].pack(side='left', padx=2)
    ttk.Label(f_xyz, text="Y:").pack(side='left'); widgets["entry_y"].pack(side='left', padx=2)
    ttk.Label(f_xyz, text="Z:").pack(side='left'); widgets["entry_z"].pack(side='left', padx=2)
    
    btn_inc = ttk.Button(frame_move, text="Mover Incremental", command=callbacks["mover_incremental"])
    btn_inc.pack(fill='x', pady=2)

    # 4. MODO ESCRITA (NOVO!)
    frame_escrita = ttk.LabelFrame(main_control_frame, text="Modo Escrita", padding=5)
    frame_escrita.pack(fill='x', pady=5)
    
    f_text = ttk.Frame(frame_escrita)
    f_text.pack(fill='x', pady=2)
    ttk.Label(f_text, text="Texto:").pack(side='left')
    ent_texto = ttk.Entry(f_text)
    ent_texto.pack(side='left', fill='x', expand=True, padx=5)
    widgets["entry_texto"] = ent_texto
    
    f_scale = ttk.Frame(frame_escrita)
    f_scale.pack(fill='x', pady=2)
    ttk.Label(f_scale, text="Tam (cm):").pack(side='left')
    ent_scale = ttk.Entry(f_scale, width=5)
    ent_scale.insert(0, "3.0")
    ent_scale.pack(side='left', padx=5)
    widgets["entry_scale"] = ent_scale
    
    btn_write = ttk.Button(frame_escrita, text="Escrever Texto", command=callbacks["escrever_texto"])
    btn_write.pack(fill='x', pady=2)

    # 5. Log
    frame_log = ttk.LabelFrame(root, text="Log", padding=5)
    frame_log.grid(row=1, column=0, columnspan=2, sticky="ew")
    log = scrolledtext.ScrolledText(frame_log, height=5, state='disabled')
    log.pack(fill='both')
    widgets["log_widget"] = log

    return widgets