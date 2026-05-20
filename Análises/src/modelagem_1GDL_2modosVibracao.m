clear all; close all; clc;

% MODELAGEM DO SISTEMA DA BALANÇA PENDULAR (1 GDL)
% Eventos ocorrendo aos 20 segundos de simulação

% 1. Parâmetros físicos do pêndulo
g = 9.81;
m_p = 1.5;   L_p = 0.3;
m_c = 0.5;   L_c = 0.15;
k_t = 0.5;   L_s = 0.2;
zeta = 0.005;

% 2. Parâmetros equivalentes translacionais
J0 = m_p*(L_p^2) + m_c*(L_c^2);
K_eq_theta = k_t + (m_p*L_p - m_c*L_c)*g;

m = J0 / (L_s^2);
k = K_eq_theta / (L_s^2);
c = 2 * zeta * sqrt(k * m);

% 3. Matrizes de Estado (x_ponto = A*x + B*F)
A = [ 0 1; -k/m -c/m ];
B = [ 0; 1/m ];

% --- CÁLCULO DA OSCILAÇÃO PRÉ-EVENTO ---
wn = sqrt(k/m);          % Frequência natural do sistema (rad/s)
amp_pre = 0.2e-6;        % Amplitude prévia de 0.2 micrometros

% 4. Configurações de Força e Tempo
F0 = 167.196e-6;    % Força de 167.196 microN
t_pulse = 10e-6;    % Duração de 10 microsegundos

t_evento = 20;      % Instante em que a perturbação ocorre (Alterado para 20s)
t_total = 150;      % Tempo total de simulação estendido
dt = 0.001;         % Passo de tempo para extração de dados

% Vetores de tempo (Pré-evento e Pós-evento)
t_pre = 0:dt:t_evento;

% Criando o histórico de oscilação para t < 20s (Regime permanente)
pos_pre = amp_pre * sin(wn * t_pre)';       % Deslocamento
vel_pre = amp_pre * wn * cos(wn * t_pre)';  % Velocidade

% Extraindo o estado exato no instante t = 20s para alimentar o ode45
x_init_20 = [pos_pre(end); vel_pre(end)];

t_post = t_evento:dt:t_total;

%% --- CASO 1: VIBRAÇÃO LIVRE APÓS 20s ---
% Aos 20s, injetamos uma perturbação adicional de 1 micrometro na posição
x_init_livre = x_init_20 + [1e-6; 0]; 
[~, x1_post] = ode45(@(t,x) A*x, t_post, x_init_livre);

% Concatenação (removendo o último ponto do pre para não duplicar t=20)
t_plot = [t_pre(1:end-1)'; t_post'];
pos_livre = [pos_pre(1:end-1); x1_post(:, 1)] * 1e6;

%% --- CASO 2: CARREGAMENTO CONTÍNUO APÓS 20s ---
% Aos 20s, aplicamos a força constante partindo do estado oscilatório atual
[~, x2_post] = ode45(@(t,x) A*x + B*F0, t_post, x_init_20);

pos_continuo = [pos_pre(1:end-1); x2_post(:, 1)] * 1e6;

%% --- CASO 3: PULSO DE 10 MICROSEGUNDOS NO INSTANTE 20s ---
% Passo A: Ação da força entre 20s e (20s + 10 us)
[~, x3_a] = ode45(@(t,x) A*x + B*F0, [t_evento, t_evento + t_pulse], x_init_20);
estado_pos_pulso = x3_a(end, :)'; % Estado exato no fim do pulso

% Passo B: Vibração livre do fim do pulso até 150s
[~, x3_post] = ode45(@(t,x) A*x, t_post, estado_pos_pulso);

pos_pulso = [pos_pre(1:end-1); x3_post(:, 1)] * 1e6;

%% --- PLOTAGEM DOS 3 GRÁFICOS ---
figure('Position', [100, 100, 800, 900]);

% Gráfico 1
subplot(3, 1, 1);
plot(t_plot, pos_livre, 'k', 'LineWidth', 1);
grid on;
ylabel({'Deslocamento', '(\mu m)'});
title('1. Vibração Livre (+1 \mu m de perturbação no sistema em t=20s)');
xlim([0 t_total]);

% Gráfico 2
subplot(3, 1, 2);
plot(t_plot, pos_continuo,'k', 'LineWidth', 1);
grid on;
ylabel({'Deslocamento', '(\mu m)'});
title('2. Força Contínua (Degrau de 167.196 \mu N aplicado em t=20s)');
xlim([0 t_total]);

% Gráfico 3
subplot(3, 1, 3);
plot(t_plot, pos_pulso, 'k', 'LineWidth', 1);
grid on;
xlabel('Tempo (s)');
ylabel({'Deslocamento', '(\mu m)'});
title('3. Pulso Único (167.196 \mu N por 10 \mu s em t=20s)');
xlim([0 t_total]);
