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

    # --- 1. MELHORIA: Aplicando um tema TTK mais moderno ---
    try:
        s = ttk.Style()
        s.theme_use('clam')
    except tk.TclError:
        print("Tema 'clam' não disponível, usando padrão.")


    # --- 2. MELHORIA: Função de Validação para Entradas Numéricas ---
    def validar_numero(P):
        """Valida se a entrada é um número flutuante válido ou vazia."""
        if P == "" or P == "-": 
            return True
        try:
            float(P) 
            return True 
        except ValueError:
            return False 

    vcmd = (root.register(validar_numero), '%P')

    # --- Configuração do Grid Principal ---
    root.grid_columnconfigure(0, weight=3) 
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)

    # --- Frame do Plot 3D (Esquerda) ---
    frame_plot = ttk.Frame(root, padding=10)
    frame_plot.grid(row=0, column=0, sticky="nsew") 
    frame_plot.grid_rowconfigure(0, weight=1)
    frame_plot.grid_columnconfigure(0, weight=1)

    fig = plt.figure(figsize=(9, 7)) 
    ax = fig.add_subplot(111, projection='3d')
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    widgets["canvas"] = canvas
    widgets["ax"] = ax

    # --- Frame Principal de Controles (Direita) ---
    main_control_frame = ttk.Frame(root, padding=10)
    main_control_frame.grid(row=0, column=1, sticky="nsew")

    # --- Frame de Conexão ---
    frame_conexao = ttk.LabelFrame(main_control_frame, text="Conexão", padding=10)
    frame_conexao.pack(fill='x', pady=5) 

    # Frame para agrupar porta e botão horizontalmente
    frame_linha_superior = ttk.Frame(frame_conexao)
    frame_linha_superior.pack(fill='x')
    
    # Frame interno para Porta COM (agora dentro da linha_superior)
    frame_porta = ttk.Frame(frame_linha_superior)
    frame_porta.pack(side='left', fill='x', expand=True, padx=(0, 10)) 
    
    ttk.Label(frame_porta, text="Porta COM:").pack(side='left', padx=(0, 5))
    entry_porta_com = ttk.Entry(frame_porta, width=12)
    entry_porta_com.insert(0, "COM7")
    entry_porta_com.pack(side='left', fill='x', expand=True)
    widgets["entry_porta_com"] = entry_porta_com

    # Frame interno para Botão de Conexão (agora dentro da linha_superior)
    frame_botoes = ttk.Frame(frame_linha_superior)
    frame_botoes.pack(side='left') 
    
    btn_toggle_conexao = ttk.Button(frame_botoes, text="Conectar", command=callbacks["toggle_conexao"])
    btn_toggle_conexao.pack(fill='x', expand=True) 
    
    widgets["btn_toggle_conexao"] = btn_toggle_conexao

    label_status = ttk.Label(frame_conexao, text="Desconectado", anchor='center')
    label_status.pack(fill='x', pady=(10,0)) 
    widgets["label_status"] = label_status

    # --- Frame de Posição Atual ---
    frame_posicao = ttk.LabelFrame(main_control_frame, text="Posição Atual (cm)", padding=10)
    frame_posicao.pack(fill='x', pady=5)
    label_coord = ttk.Label(frame_posicao, text="X=0.0, Y=0.0, Z=0.0", anchor='center', font=("Segoe UI", 11))
    label_coord.pack(fill='x', pady=2) 
    widgets["label_coord"] = label_coord

    # --- Frame de Controle Manual (com os 4 motores) ---
    frame_manual = ttk.LabelFrame(main_control_frame, text="Controle Manual (Passos)", padding=10)
    frame_manual.pack(fill='x', pady=5)
    
    frame_manual.grid_columnconfigure(0, weight=1)
    frame_manual.grid_columnconfigure(1, weight=1)

    sentido_var_list = []
    passos_entry_list = []
    delay_entry_list = []
    
    labels = ["J1: Base", "J2: Ombro", "J3: Cotovelo", "J4: Punho"]
    
    for i in range(4):
        frame = ttk.LabelFrame(frame_manual, text=labels[i], padding=5)
        frame.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew") 
        
        sentido_var = tk.StringVar(value='H')
        
        radio_frame = ttk.Frame(frame)
        radio_frame.pack(fill='x')
        ttk.Radiobutton(radio_frame, text="Horário", variable=sentido_var, value='H').pack(side='left', expand=True)
        ttk.Radiobutton(radio_frame, text="Anti-H", variable=sentido_var, value='A').pack(side='left', expand=True)
        sentido_var_list.append(sentido_var)
        
        passos_frame = ttk.Frame(frame)
        passos_frame.pack(fill='x', pady=3) 
        ttk.Label(passos_frame, text="Passos:").pack(side='left', padx=(0, 3))
        e_passos = ttk.Entry(passos_frame, width=6)
        e_passos.pack(side='right', fill='x', expand=True)
        passos_entry_list.append(e_passos)
        
        delay_frame = ttk.Frame(frame)
        delay_frame.pack(fill='x', pady=3) 
        ttk.Label(delay_frame, text="Delay(ms):").pack(side='left', padx=(0, 3))
        e_delay = ttk.Entry(delay_frame, width=6)
        e_delay.insert(0, '10')
        e_delay.pack(side='right', fill='x', expand=True)
        delay_entry_list.append(e_delay)
        
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill='x', pady=(5,0)) 
        ttk.Button(action_frame, text="Enviar", command=lambda m=i: callbacks["comando_motor"](m)).pack(side='left', fill='x', expand=True, padx=(0,2))
        ttk.Button(action_frame, text="Parar", command=lambda m=i: callbacks["parar_motor"](m)).pack(side='left', fill='x', expand=True, padx=(2,0))

    widgets["sentido_var_list"] = sentido_var_list
    widgets["passos_entry_list"] = passos_entry_list
    widgets["delay_entry_list"] = delay_entry_list

    # --- Controle por Coordenada (Layout Vertical + Validação) ---
    frame_coord = ttk.LabelFrame(main_control_frame, text="Mover para Coordenada (cm)", padding=10)
    frame_coord.pack(fill='x', pady=5)
    
    frame_x = ttk.Frame(frame_coord)
    frame_x.pack(fill='x', pady=2) 
    ttk.Label(frame_x, text="X:", width=3).pack(side='left') 
    entry_x = ttk.Entry(frame_x, validate="key", validatecommand=vcmd) 
    entry_x.pack(side='left', fill='x', expand=True, padx=2)
    widgets["entry_x"] = entry_x
    
    frame_y = ttk.Frame(frame_coord)
    frame_y.pack(fill='x', pady=2) 
    ttk.Label(frame_y, text="Y:", width=3).pack(side='left')
    entry_y = ttk.Entry(frame_y, validate="key", validatecommand=vcmd)
    entry_y.pack(side='left', fill='x', expand=True, padx=2)
    widgets["entry_y"] = entry_y
    
    frame_z = ttk.Frame(frame_coord)
    frame_z.pack(fill='x', pady=2) 
    ttk.Label(frame_z, text="Z:", width=3).pack(side='left')
    entry_z = ttk.Entry(frame_z, validate="key", validatecommand=vcmd)
    entry_z.pack(side='left', fill='x', expand=True, padx=2)
    widgets["entry_z"] = entry_z
    
    # --- 5. ALTERAÇÃO: Agrupando os botões "Mover" lado a lado ---
    frame_botoes_mover = ttk.Frame(frame_coord)
    frame_botoes_mover.pack(fill='x', pady=(8,2)) # Espaçamento acima
    
    ttk.Button(frame_botoes_mover, text="Mover Absoluto (fsolve)", command=callbacks["mover_absoluto"]).pack(side='left', fill='x', expand=True, padx=(0,2))
    ttk.Button(frame_botoes_mover, text="Mover Incremental (Seguro)", command=callbacks["mover_incremental"]).pack(side='left', fill='x', expand=True, padx=(2,0))
    # --- Fim da Alteração ---
    
    # --- Frame de Predefinições (antigo "Testes") ---
    frame_testes = ttk.LabelFrame(main_control_frame, text="Predefinições e Testes", padding=10)
    frame_testes.pack(fill='x', pady=5)
    
    testes_btn_frame = ttk.Frame(frame_testes)
    testes_btn_frame.pack(fill='x')
    
    ttk.Label(testes_btn_frame, text="Testar 5°:").pack(side='left', padx=(0,10))
    for i in range(4):
        ttk.Button(testes_btn_frame, text=f"J{i+1}", width=4, command=lambda j=i: callbacks["mover_junta_temp"](j)).pack(side='left', fill='x', expand=True, padx=2)

    # --- Frame do Log (Inferior) ---
    frame_log = ttk.LabelFrame(root, text="Log de Comandos", padding=5)
    frame_log.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
    
    log_widget = scrolledtext.ScrolledText(frame_log, height=8, wrap=tk.WORD, state='disabled')
    log_widget.pack(fill='both', expand=True)
    widgets["log_widget"] = log_widget
    
    return widgets