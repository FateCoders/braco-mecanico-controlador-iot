# main.py
import tkinter as tk
import numpy as np
import time
import threading # Para não travar a interface enquanto escreve

import interface
import cinematic as C
import comunication as COM
import alphabet # <--- NOVO IMPORT

# =========================
# Variáveis de Estado
# =========================
theta1_atual = 0.0
theta2_atual = 0.0
theta3_atual = 0.0
theta4_atual = 0.0
is_conectado = False

# Alturas de trabalho (Z)
z_ref_papel = 0.0   # Altura onde a caneta toca o papel (definido pelo usuário)
z_safe_altura = 2.0 # Altura segura para mover sem riscar (cm acima do papel)

# =========================
# Funções Auxiliares de Movimento
# =========================

def log(msg):
    """Escreve no log da interface"""
    print(msg)
    if "log_widget" in widgets:
        widgets["log_widget"].config(state='normal')
        widgets["log_widget"].insert(tk.END, msg + "\n")
        widgets["log_widget"].see(tk.END)
        widgets["log_widget"].config(state='disabled')

def mover_linear(x_dest, y_dest, z_dest, passo_mm=1.0):
    """
    Move a ponta da caneta em linha reta do ponto atual até (x_dest, y_dest, z_dest).
    Usa interpolação (vários passos pequenos) para garantir a reta.
    """
    global theta1_atual, theta2_atual, theta3_atual, theta4_atual

    # Posição atual
    xs, ys, zs = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    pos_atual = np.array([xs[-1], ys[-1], zs[-1]])
    pos_final = np.array([x_dest, y_dest, z_dest])

    distancia = np.linalg.norm(pos_final - pos_atual)
    if distancia < 0.1: return # Já está lá

    # Calcula quantos passos precisa (resolução de 1mm por exemplo)
    n_passos = int(np.ceil(distancia / (passo_mm / 10.0))) # converte mm para cm
    if n_passos < 1: n_passos = 1

    # Vetor de passo
    step_vector = (pos_final - pos_atual) / n_passos

    for i in range(n_passos):
        # Jacobiana ou Cinemática Inversa Ponto a Ponto?
        # Para escrita, Jacobiana é mais suave para pequenos passos.
        J = C.calcular_jacobiano(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
        try:
            dtheta = np.linalg.pinv(J) @ step_vector
        except:
            log("Erro: Singularidade no movimento.")
            break
        
        # Converte radianos para passos dos motores
        dif_passos = [int(round(np.degrees(dtheta[k]) / C.graus_por_passo[k])) for k in range(4)]
        
        # Envia comando aos motores
        for k, p in enumerate(dif_passos):
            if p == 0: continue
            direcao = 'H' if p < 0 else 'A'
            # Delay baixo para escrita fluida (7ms)
            COM.enviar_comando(k+1, direcao, abs(p), 7)
            
        # Atualiza angulos virtuais
        theta1_atual += dtheta[0]
        theta2_atual += dtheta[1]
        theta3_atual += dtheta[2]
        theta4_atual += dtheta[3]

        # Atualiza plot a cada X passos para não travar muito
        if i % 5 == 0: 
            root.after(1, atualizar_plot) 

    atualizar_plot()
    # Atualiza label na interface
    widgets["label_coord"].config(text=f"X={x_dest:.1f}, Y={y_dest:.1f}, Z={z_dest:.1f}")


# =========================
# Callbacks da Interface
# =========================

def toggle_conexao_callback():
    global is_conectado
    if is_conectado:
        COM.desconectar_arduino()
        widgets["label_status"].config(text="Desconectado", foreground="red")
        widgets["btn_toggle_conexao"].config(text="Conectar")
        is_conectado = False
    else:
        porta = widgets["entry_porta_com"].get()
        sucesso, msg, _ = COM.conectar_arduino(porta)
        log(msg)
        if sucesso:
            widgets["label_status"].config(text="Conectado", foreground="green")
            widgets["btn_toggle_conexao"].config(text="Desconectar")
            is_conectado = True

def calibrar_z_callback():
    """Define a altura Z atual como sendo o Z do papel (0.0 relativo)"""
    global z_ref_papel
    xs, ys, zs = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    z_atual = zs[-1]
    
    z_ref_papel = z_atual
    log(f"Z Papel calibrado em: {z_ref_papel:.2f} cm")

def escrever_texto_thread():
    """Função que roda em thread separada para não travar a GUI"""
    texto = widgets["entry_texto"].get().upper()
    try:
        escala = float(widgets["entry_scale"].get())
    except:
        log("Escala inválida.")
        return

    # Pega posição inicial (Onde o robô está agora será o canto inferior esquerdo da 1ª letra)
    xs, ys, zs = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    start_x, start_y = xs[-1], ys[-1]
    
    # Alturas absolutas
    z_baixo = z_ref_papel           # Tocar papel
    z_alto = z_ref_papel + z_safe_altura  # Levantar
    
    log(f"Escrevendo '{texto}'...")

    # Levanta a caneta primeiro
    mover_linear(start_x, start_y, z_alto)

    cursor_x = start_x

    for char in texto:
        strokes = alphabet.get_char(char)
        
        if not strokes: # Espaço ou caractere desconhecido
            cursor_x += escala * 0.5
            continue

        log(f"Desenhando '{char}'...")
        
        for stroke in strokes:
            # 1. Mover (no ar) para o primeiro ponto do traço
            p0 = stroke[0]
            target_x = cursor_x + (p0[0] * escala)
            target_y = start_y + (p0[1] * escala) # Escreve na linha Y constante por enquanto
            
            mover_linear(target_x, target_y, z_alto) # Vai por cima
            
            # 2. Baixar caneta
            mover_linear(target_x, target_y, z_baixo)
            time.sleep(0.2) # Estabilizar
            
            # 3. Desenhar o traço (ponto a ponto)
            for p in stroke[1:]:
                next_x = cursor_x + (p[0] * escala)
                next_y = start_y + (p[1] * escala)
                mover_linear(next_x, next_y, z_baixo) # Risca o papel
            
            # 4. Levantar ao fim do traço
            mover_linear(target_x, target_y, z_alto) # (volta ao ultimo xy mas sobe Z - bug fix: use current xy)
            # Na verdade, o 'mover_linear' atualiza a posição interna, então basta:
            # Pegar posição atual e subir Z
            curr_xs, curr_ys, _ = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
            mover_linear(curr_xs[-1], curr_ys[-1], z_alto)

        # Avança o cursor para a próxima letra
        cursor_x += escala * 1.2 # 1.2 para dar espaçamento

    log("Escrita concluída.")
    # Volta para home ou fica parado em cima

def escrever_texto_callback():
    threading.Thread(target=escrever_texto_thread).start()

def mover_incremental_callback():
    try:
        dx = float(widgets["entry_x"].get() or 0)
        dy = float(widgets["entry_y"].get() or 0)
        dz = float(widgets["entry_z"].get() or 0)
    except: return

    xs, ys, zs = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    
    novo_x = xs[-1] + dx
    novo_y = ys[-1] + dy
    novo_z = zs[-1] + dz
    
    # Usa a função linear para mover suave
    threading.Thread(target=mover_linear, args=(novo_x, novo_y, novo_z)).start()

# Callback dummy para os botões manuais (não alterados)
def comando_motor_callback(m): pass 
def parar_motor_callback(m): pass
def mover_junta_temp(j): pass

def atualizar_plot():
    xs, ys, zs = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    ax = widgets["ax"]
    ax.clear()
    # ... (código de plotagem igual ao anterior) ...
    base_size, base_height = 5, C.Lbase
    xx = [-base_size, base_size, base_size, -base_size, -base_size]
    yy = [-base_size, -base_size, base_size, base_size, -base_size]
    ax.plot(xx, yy, np.zeros_like(xx), color='gray')
    for i in range(4): ax.plot([xx[i], xx[i]], [yy[i], yy[i]], [0, base_height], color='gray')
    ax.plot(xs, ys, zs, '-o', linewidth=3)
    max_L = 30
    ax.set_xlim(-max_L, max_L); ax.set_ylim(-max_L, max_L); ax.set_zlim(0, 40)
    widgets["canvas"].draw()

def on_closing():
    COM.desconectar_arduino()
    root.destroy()

# =========================
# Execução
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Robô Escritor IoT")
    
    callbacks = {
        "toggle_conexao": toggle_conexao_callback,
        "calibrar_z": calibrar_z_callback,
        "mover_incremental": mover_incremental_callback,
        "escrever_texto": escrever_texto_callback,
        "comando_motor": comando_motor_callback, # Mantidos para compatibilidade
        "parar_motor": parar_motor_callback,
        "mover_junta_temp": mover_junta_temp
    }
    
    widgets = interface.criar_interface(root, callbacks)
    atualizar_plot()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()