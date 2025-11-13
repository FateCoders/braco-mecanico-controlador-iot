# main.py
import tkinter as tk
import numpy as np
import time

# Importa dos nossos módulos separados
import interface
import cinematic as C # Usamos 'C' como apelido
import comunication as COM # Usamos 'COM' como apelido

# =========================
# Variáveis de Estado (Posição Atual)
# =========================
theta1_atual = 0.0
theta2_atual = 0.0
theta3_atual = 0.0
theta4_atual = 0.0

# ===============================================
# Funções de Lógica / Callbacks
# (São as funções que os botões da interface irão chamar)
# ===============================================

def conectar_callback():
    porta = widgets["entry_porta_com"].get()
    sucesso, status_msg, _ = COM.conectar_arduino(porta)
    
    if sucesso:
        widgets["label_status"].config(text=status_msg, foreground="green")
    else:
        widgets["label_status"].config(text=status_msg, foreground="red")

def desconectar_callback():
    COM.desconectar_arduino()
    widgets["label_status"].config(text="Desconectado", foreground="black")

def comando_motor_callback(motor_num):
    direcao = widgets["sentido_var_list"][motor_num].get()
    passos = widgets["passos_entry_list"][motor_num].get()
    delay = widgets["delay_entry_list"][motor_num].get()
    
    if passos == '': passos = '0'
    if delay == '': delay = '10'
    
    COM.enviar_comando(motor_num + 1, direcao, int(passos), int(delay))
    # Nota: A atualização de 'theta_atual' não está implementada
    # para comandos manuais. Isso precisaria ser adicionado.

def parar_motor_callback(motor_num):
    COM.enviar_comando(motor_num + 1, 'P', 0, 10)

def mover_para_coordenada_seguro():
    global theta1_atual, theta2_atual, theta3_atual, theta4_atual
    
    # --- INÍCIO DA MODIFICAÇÃO (Lógica Relativa) ---
    # 1. Pega a posição X, Y, Z atual
    xs_atuais, ys_atuais, zs_atuais = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    x_atual = xs_atuais[-1]
    y_atual = ys_atuais[-1]
    z_atual = zs_atuais[-1]
    pos_atual = np.array([x_atual, y_atual, z_atual])
            
    try:
        # 2. Lê os valores DELTA (quanto mover) dos campos
        x_delta = float(widgets["entry_x"].get())
        y_delta = float(widgets["entry_y"].get())
        z_delta = float(widgets["entry_z"].get())
    except Exception as e:
        print(f"Coordenadas inválidas: {e}")
        return

    # 3. Calcula o novo destino SOMANDO
    x_dest = x_atual + x_delta
    y_dest = y_atual + y_delta
    z_dest = z_atual + z_delta
    # --- FIM DA MODIFICAÇÃO ---

    # O código original continua daqui, usando os x_dest, y_dest, z_dest recém-calculados
    dpos_total = np.array([x_dest, y_dest, z_dest]) - pos_atual
    distancia = np.linalg.norm(dpos_total)
    passo_max = 1.0 # Move 1.0 cm por passo
    
    # Previne divisão por zero
    n_passos = int(np.ceil(distancia / passo_max))
    if n_passos == 0: 
        print("Já está no destino (ou delta é zero).")
        return
        
    dpos_step = dpos_total / n_passos

    print(f"Movendo {distancia:.2f}cm em {n_passos} passos.")

    for i in range(n_passos):
        J = C.calcular_jacobiano(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
        try:
            dtheta = np.linalg.pinv(J) @ dpos_step
        except Exception as e:
            print(f"Erro na Jacobiana: {e}")
            return
            
        dif_passos = [int(round(np.degrees(dtheta[i]) / C.graus_por_passo[i])) for i in range(4)]
        
        for i, p in enumerate(dif_passos):
            if p == 0: continue
            direcao = 'H' if p < 0 else 'A'
            COM.enviar_comando(i+1, direcao, abs(p), 10)
            
        theta1_atual += dtheta[0]
        theta2_atual += dtheta[1]
        theta3_atual += dtheta[2]
        theta4_atual += dtheta[3]
        
        atualizar_plot()
        root.update_idletasks() # Força a GUI a atualizar
        
    print("Movimento incremental concluído.")
    widgets["label_coord"].config(text=f"Pos atual: X={x_dest:.1f}, Y={y_dest:.1f}, Z={z_dest:.1f}")

def mover_para_absoluto_fsolve():
    global theta1_atual, theta2_atual, theta3_atual, theta4_atual
    try:
        x_abs = float(widgets["entry_x"].get())
        y_abs = float(widgets["entry_y"].get())
        z_abs = float(widgets["entry_z"].get())
    except Exception as e:
        print(f"Coordenadas inválidas: {e}")
        return

    chute_inicial = [theta1_atual, theta2_atual, theta3_atual, theta4_atual]
    t1, t2, t3, t4 = C.inversa_fsolve(x_abs, y_abs, z_abs, chute_inicial)
    
    deltas = [C.delta_theta(t1, theta1_atual),
              C.delta_theta(t2, theta2_atual),
              C.delta_theta(t3, theta3_atual),
              C.delta_theta(t4, theta4_atual)]
              
    dif_passos = [C.angulo_para_passos(deltas[i], i) for i in range(4)]
    
    print(f"Movendo para {x_abs}, {y_abs}, {z_abs}. Passos: {dif_passos}")
    
    for i, p in enumerate(dif_passos):
        if p == 0: continue
        # Atenção: verifique se H e A estão corretos para sua montagem
        direcao = 'H' if p > 0 else 'A' 
        COM.enviar_comando(i+1, direcao, abs(p), 10)
        
    theta1_atual, theta2_atual, theta3_atual, theta4_atual = t1, t2, t3, t4
    
    atualizar_plot()
    widgets["label_coord"].config(text=f"Pos atual: X={x_abs:.1f}, Y={y_abs:.1f}, Z={z_abs:.1f}")

def mover_junta_temp(junta_idx):
    delta_graus=5
    delay_ms=10
    espera_s=2 # Reduzido para testes
    
    passos = int(round(delta_graus / C.graus_por_passo[junta_idx]))
    print(f"Testando Junta {junta_idx+1} ({passos} passos)")
    
    COM.enviar_comando(junta_idx+1, 'H', passos, delay_ms)
    time.sleep(espera_s)
    COM.enviar_comando(junta_idx+1, 'A', passos, delay_ms)
    time.sleep(espera_s)
    print(f"Teste Junta {junta_idx+1} concluído.")

def atualizar_plot():
    xs, ys, zs = C.direta(theta1_atual, theta2_atual, theta3_atual, theta4_atual)
    
    ax = widgets["ax"] # Pega o eixo do plot (criado na view)
    ax.clear()
    
    # Desenha a base
    base_size, base_height = 5, C.Lbase
    xx = [-base_size, base_size, base_size, -base_size, -base_size]
    yy = [-base_size, -base_size, base_size, base_size, -base_size]
    ax.plot3D(xx, yy, np.zeros_like(xx), color='gray')
    ax.plot3D(xx, yy, np.full_like(xx, base_height), color='gray')
    for i in range(4):
        ax.plot3D([xx[i], xx[i]], [yy[i], yy[i]], [0, base_height], color='gray')
        
    # Desenha o braço
    ax.plot(xs, ys, zs, '-o', linewidth=3, markersize=6)
    ax.scatter(xs[-2], ys[-2], zs[-2], color='blue', s=80) # Base da garra
    ax.scatter(xs[-1], ys[-1], zs[-1], color='red', s=100) # Ponta da garra
    
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    ax.set_title('Braço Robótico 4R')
    ax.view_init(elev=30, azim=60)
    
    # Define limites fixos
    max_L = C.L2 + C.L3 + C.L4 + C.Lpen
    ax.set_xlim(-max_L, max_L)
    ax.set_ylim(-max_L, max_L)
    ax.set_zlim(0, C.Lbase + max_L)
    
    widgets["canvas"].draw() # Atualiza o canvas (criado na view)
    
    # Atualiza a posição no label
    x_atual, y_atual, z_atual = xs[-1], ys[-1], zs[-1]
    widgets["label_coord"].config(text=f"Pos atual: X={x_atual:.1f}, Y={y_atual:.1f}, Z={z_atual:.1f}")


def on_closing_callback():
    print("Fechando a aplicação...")
    desconectar_callback()
    root.destroy()

# =========================
# Execução Principal
# =========================
if __name__ == "__main__":
    
    root = tk.Tk()
    root.title("Controle Braço Robótico IoT")

    # Cria um dicionário com todas as funções de lógica
    # que a interface precisa saber
    callbacks = {
        "conectar": conectar_callback,
        "desconectar": desconectar_callback,
        "comando_motor": comando_motor_callback,
        "parar_motor": parar_motor_callback,
        "mover_incremental": mover_para_coordenada_seguro,
        "mover_absoluto": mover_para_absoluto_fsolve,
        "mover_junta_temp": mover_junta_temp,
    }

    # Chama a função para criar a interface
    # Ela retorna os widgets que precisamos acessar (labels, entries, etc.)
    widgets = interface.criar_interface(root, callbacks)

    # Configura o plot inicial
    atualizar_plot()

    # Configura a função de fechamento
    root.protocol("WM_DELETE_WINDOW", on_closing_callback)
    
    # Inicia a aplicação
    root.mainloop()