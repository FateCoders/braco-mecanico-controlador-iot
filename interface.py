# interface_view.py
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext # Para o Log
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def criar_interface(root, callbacks):
    """
    Cria e posiciona todos os widgets da GUI com um layout moderno.
    'root' é a janela principal do Tkinter.
    'callbacks' é um dicionário de funções de lógica do main.py
    """
    
    widgets = {} # Dicionário para retornar widgets que precisam ser lidos/atualizados

    # --- Configuração do Grid Principal ---
    # Coluna 0 (Plot) será 3x mais larga que a Coluna 1 (Controles)
    root.grid_columnconfigure(0, weight=3) 
    root.grid_columnconfigure(1, weight=1)
    # Linha 0 (Principal) vai expandir, Linha 1 (Log) terá tamanho fixo
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)

    # --- Frame do Plot 3D (Esquerda) ---
    frame_plot = ttk.Frame(root, padding=10)
    frame_plot.grid(row=0, column=0, sticky="nsew") # nsew = preenche tudo
    frame_plot.grid_rowconfigure(0, weight=1)
    frame_plot.grid_columnconfigure(0, weight=1)

    fig = plt.figure(figsize=(9, 7)) # Tamanho ajustado
    ax = fig.add_subplot(111, projection='3d')
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    widgets["canvas"] = canvas
    widgets["ax"] = ax

    # --- Frame Principal de Controles (Direita) ---
    # Este frame usará .pack() para empilhar os controles verticalmente
    main_control_frame = ttk.Frame(root, padding=10)
    main_control_frame.grid(row=0, column=1, sticky="nsew")

    # --- Frame de Conexão ---
    frame_conexao = ttk.LabelFrame(main_control_frame, text="Conexão", padding=10)
    frame_conexao.pack(fill='x', pady=5) # Empilha verticalmente

    # Frame interno para Porta COM
    frame_porta = ttk.Frame(frame_conexao)
    frame_porta.pack(fill='x')
    ttk.Label(frame_porta, text="Porta COM:").pack(side='left', padx=(0, 5))
    entry_porta_com = ttk.Entry(frame_porta, width=12)
    entry_porta_com.insert(0, "COM7")
    entry_porta_com.pack(side='left', fill='x', expand=True)
    widgets["entry_porta_com"] = entry_porta_com

    # Frame interno para Botões de Conexão
    frame_botoes = ttk.Frame(frame_conexao)
    frame_botoes.pack(fill='x', pady=(5,0))
    btn_conectar = ttk.Button(frame_botoes, text="Conectar", command=callbacks["conectar"])
    btn_conectar.pack(side='left', fill='x', expand=True, padx=(0, 2))
    btn_desconectar = ttk.Button(frame_botoes, text="Desconectar", command=callbacks["desconectar"])
    btn_desconectar.pack(side='left', fill='x', expand=True, padx=(2, 0))

    label_status = ttk.Label(frame_conexao, text="Desconectado", anchor='center')
    label_status.pack(fill='x', pady=(5,0))
    widgets["label_status"] = label_status

    # --- Frame de Posição Atual ---
    frame_posicao = ttk.LabelFrame(main_control_frame, text="Posição Atual (cm)", padding=10)
    frame_posicao.pack(fill='x', pady=5)
    label_coord = ttk.Label(frame_posicao, text="X=0.0, Y=0.0, Z=0.0", anchor='center', font=("Segoe UI", 10))
    label_coord.pack(fill='x')
    widgets["label_coord"] = label_coord

    # --- Frame de Controle Manual (com os 4 motores) ---
    frame_manual = ttk.LabelFrame(main_control_frame, text="Controle Manual (Passos)", padding=10)
    frame_manual.pack(fill='x', pady=5)

    sentido_var_list = []
    passos_entry_list = []
    delay_entry_list = []
    
    # Labels para os motores, como na imagem
    labels = ["J1: Base", "J2: Ombro", "J3: Cotovelo", "J4: Punho"]
    
    for i in range(4):
        # Frame individual para cada motor
        frame = ttk.LabelFrame(frame_manual, text=labels[i], padding=5)
        # Organiza os 4 frames em uma grade 2x2
        frame.grid(row=i//2, column=i%2, padx=2, pady=2, sticky="nsew") 
        
        sentido_var = tk.StringVar(value='H')
        
        # Frame para os Rádios (Horario/Antihorario)
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(fill='x')
        ttk.Radiobutton(radio_frame, text="Horário", variable=sentido_var, value='H').pack(side='left', expand=True)
        ttk.Radiobutton(radio_frame, text="Anti-H", variable=sentido_var, value='A').pack(side='left', expand=True)
        sentido_var_list.append(sentido_var)
        
        # Frame para Passos
        passos_frame = ttk.Frame(frame)
        passos_frame.pack(fill='x', pady=2)
        ttk.Label(passos_frame, text="Passos:").pack(side='left')
        e_passos = ttk.Entry(passos_frame, width=6)
        e_passos.pack(side='right', fill='x', expand=True)
        passos_entry_list.append(e_passos)
        
        # Frame para Delay
        delay_frame = ttk.Frame(frame)
        delay_frame.pack(fill='x', pady=2)
        ttk.Label(delay_frame, text="Delay(ms):").pack(side='left')
        e_delay = ttk.Entry(delay_frame, width=6)
        e_delay.insert(0, '10')
        e_delay.pack(side='right', fill='x', expand=True)
        delay_entry_list.append(e_delay)
        
        # Frame para Botões de Ação
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', pady=2)
        ttk.Button(action_frame, text="Enviar", command=lambda m=i: callbacks["comando_motor"](m)).pack(side='left', fill='x', expand=True, padx=(0,1))
        ttk.Button(action_frame, text="Parar", command=lambda m=i: callbacks["parar_motor"](m)).pack(side='left', fill='x', expand=True, padx=(1,0))

    widgets["sentido_var_list"] = sentido_var_list
    widgets["passos_entry_list"] = passos_entry_list
    widgets["delay_entry_list"] = delay_entry_list

    # --- Controle por Coordenada (Absoluto) ---
    frame_coord = ttk.LabelFrame(main_control_frame, text="Mover para Coordenada (cm)", padding=10)
    frame_coord.pack(fill='x', pady=5)
    
    # Frame para as Entradas X, Y, Z
    entry_coord_frame = ttk.Frame(frame_coord)
    entry_coord_frame.pack(fill='x')
    
    ttk.Label(entry_coord_frame, text="X:").pack(side='left')
    entry_x = ttk.Entry(entry_coord_frame, width=6); entry_x.pack(side='left', fill='x', expand=True, padx=2)
    widgets["entry_x"] = entry_x
    
    ttk.Label(entry_coord_frame, text="Y:").pack(side='left')
    entry_y = ttk.Entry(entry_coord_frame, width=6); entry_y.pack(side='left', fill='x', expand=True, padx=2)
    widgets["entry_y"] = entry_y
    
    ttk.Label(entry_coord_frame, text="Z:").pack(side='left')
    entry_z = ttk.Entry(entry_coord_frame, width=6); entry_z.pack(side='left', fill='x', expand=True, padx=2)
    widgets["entry_z"] = entry_z
    
    # Botões de movimento
    ttk.Button(frame_coord, text="Mover Absoluto (fsolve)", command=callbacks["mover_absoluto"]).pack(fill='x', pady=(5,2))
    ttk.Button(frame_coord, text="Mover Incremental (Seguro)", command=callbacks["mover_incremental"]).pack(fill='x', pady=2)

    # --- Frame de Predefinições (antigo "Testes") ---
    frame_testes = ttk.LabelFrame(main_control_frame, text="Predefinições e Testes", padding=10)
    frame_testes.pack(fill='x', pady=5)
    
    # Frame para os botões de teste
    testes_btn_frame = ttk.Frame(frame_testes)
    testes_btn_frame.pack(fill='x')
    
    ttk.Label(testes_btn_frame, text="Testar 5°:").pack(side='left', padx=(0,5))
    for i in range(4):
        ttk.Button(testes_btn_frame, text=f"J{i+1}", width=4, command=lambda j=i: callbacks["mover_junta_temp"](j)).pack(side='left', fill='x', expand=True, padx=1)

    # --- Frame do Log (Inferior) ---
    frame_log = ttk.LabelFrame(root, text="Log de Comandos", padding=5)
    frame_log.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
    
    log_widget = scrolledtext.ScrolledText(frame_log, height=8, wrap=tk.WORD, state='disabled')
    log_widget.pack(fill='both', expand=True)
    widgets["log_widget"] = log_widget
    
    return widgets