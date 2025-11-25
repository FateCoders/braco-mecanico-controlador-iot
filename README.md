# **Controlador de Braço Robótico 4-DOF (Python \+ Arduino)**

Este projeto consiste num sistema completo de controlo para um braço robótico de 4 graus de liberdade (4-DOF), utilizando motores de passo 28BYJ-48. O sistema integra um firmware em **Arduino** (Escravo) e uma interface de controlo avançada em **Python** (Mestre).

O projeto aplica conceitos de **Cinemática Direta e Inversa**, comunicação Serial e processamento vetorial para escrita automática.

## **🚀 Funcionalidades**

* **Cinemática Inversa (IK):** Move o efetuador para coordenadas (X, Y, Z) calculando automaticamente os ângulos das juntas.  
* **Visualização 3D em Tempo Real:** Simulação do braço usando matplotlib integrada à interface.  
* **Modo de Escrita (Novo\!):** Capacidade de escrever textos (letras e números) em papel usando uma fonte vetorial personalizada.  
* **Controlo Manual:** Ajuste fino de cada junta individualmente.  
* **Movimento Incremental:** Algoritmo baseado no Jacobiano para movimentos suaves e lineares.  
* **Conexão Hot-Swap:** Conecte e desconecte a porta Serial sem fechar o programa.

## **🛠️ Hardware Necessário**

* 1x Placa Arduino (Uno, Nano ou Mega).  
* 4x Motores de Passo **28BYJ-48** (5V).  
* 4x Drivers **ULN2003**.  
* 1x Fonte de Alimentação Externa 5V (Mínimo 2A) \- **Crucial\!** Não alimente os motores pelo USB do Arduino.  
* Estrutura mecânica do braço (Impressão 3D ou corte a laser).  
* Caneta e suporte (para o modo de escrita).

### **Esquema de Ligação (Padrão)**

| Motor | Articulação | Pinos Arduino (IN1, IN2, IN3, IN4) |
| :---- | :---- | :---- |
| **1** | Base | 16 (A2), 17 (A3), 14 (A0), 15 (A1) |
| **2** | Ombro | 4, 5, 2, 3 |
| **3** | Cotovelo | 8, 9, 6, 7 |
| **4** | Punho/Garra | 12, 13, 10, 11 |

**Nota:** Verifique o arquivo .ino para confirmar a pinagem exata utilizada no seu firmware.

## **📂 Estrutura do Projeto**

O código Python foi modularizado para facilitar a manutenção:

* main.py: **Arquivo principal**. Gerencia a lógica, threads de movimento e callbacks. Execute este arquivo.  
* interface.py: Responsável apenas pelo layout visual (Janelas, Botões, Gráficos).  
* cinematic.py: Contém a matemática pesada (Cinemática Direta, Inversa, Jacobiano).  
* comunication.py: Gerencia a conexão Serial (envio e recebimento de dados).  
* alphabet.py: Banco de dados vetorial com as coordenadas para desenhar letras e números.

## **📦 Instalação e Dependências**

### **1\. Python (Computador)**

Certifique-se de ter o **Python 3.x** instalado. Instale as bibliotecas necessárias:

pip install pyserial numpy matplotlib scipy

*(Nota: O tkinter geralmente já vem instalado com o Python).*

### **2\. Arduino (Firmware)**

1. Abra o código do Arduino (o arquivo .ino gerado no projeto).  
2. Selecione a placa e a porta correta na Arduino IDE.  
3. Carregue o código para a placa.

## **🎮 Como Usar**

1. Conecte o Arduino ao PC via USB.  
2. Execute o controlador:  
   python main.py

3. Na interface:  
   * Digite a porta COM (ex: COM3 ou COM10) e clique em **Conectar**.  
   * Use os controlos manuais para testar os motores.

### **✍️ Utilizando o Modo de Escrita**

Para que o robô escreva corretamente, siga este procedimento de calibração:

1. Coloque uma folha de papel na base do robô.  
2. Use o **"Mover Incremental"** (Z negativo) para baixar a caneta até que ela toque levemente o papel.  
3. Clique no botão **"Definir Z Atual como Papel"**. (Isso salva a altura de referência).  
4. Levante a caneta (Z positivo) para uma altura segura.  
5. No quadro "Modo Escrita", digite o texto (ex: OLA) e o tamanho da letra (ex: 3.0).  
6. Clique em **"Escrever Texto"**.

## **⚠️ Avisos Importantes**

* **Alimentação:** Se os LEDs dos drivers piscarem mas o motor não girar, ou se o Arduino reiniciar, a sua fonte de energia é fraca. Use uma fonte externa de 5V/2A.  
* **Limites Físicos:** O software não conhece os limites físicos do seu braço impresso. Cuidado para não colidir as peças.

## **🤝 Créditos**

Desenvolvido como parte do projeto de Robótica Articulada IoT.

* Modelagem Cinemática baseada na literatura RRR/RRRR.  
* Interface desenvolvida com Tkinter e Matplotlib.