% =========================================================================
% Simulação Dinâmica da Balança: Oscilação Livre e Amortecimento Magnético
% =========================================================================
clear; clc; close all;

%% 1. Definição de Parâmetros Iniciais
fn = 0.8154;                 % Frequência natural em Hz
wn = 2 * pi * fn;         % Frequência natural em rad/s
t_excitacao = 20;         % Instante do pulso de excitação (s)
t_ativacao = 86;          % Instante de ativação do eletroímã (s)
t_final = 400;            % Tempo total de simulação (s)
limite_amplitude = 0.2;   % Amplitude da oscilação em repouso dinâmico e alvo final (µm)

% Amortecimento selenoide LASE
zeta_LASE = 0.002045;

% Amortecimento proposto
c_proposto = 0.1397;
k_eq = 86.78;
m_eq = wn^2/k_eq;
zeta_proposto = c_proposto/(2*sqrt(k_eq*m_eq))

% Níveis de amortecimento
zeta_livre = 0.00068;     % Amortecimento estrutural quase nulo (amplitude constante)
zetas_teste = [zeta_livre, zeta_LASE, zeta_proposto]; % Baixo, Médio e Alto amortecimento
titulos = {'Sem Amortecimento Ativo', ...
           'Amortecimento Atual com Ativação em t = 86 s', ...
           'Amortecimento Proposto com Ativação em t = 86 s'};
cores = {'#D95319', '#0072BD', '#77AC30'}; 

% Opções do solucionador de equações diferenciais
opcoes = odeset('RelTol', 1e-6, 'AbsTol', 1e-8);

%% 2. Simulação da Fase 0 e Fase 1
% Fase 0: Oscilação inicial contínua (0 a 20s)
t0 = linspace(0, t_excitacao, 200)';
y0_x = limite_amplitude * sin(wn * t0); 

% Fase 1: Oscilação Livre (20s a 86s) com amortecimento desprezível
x_excitacao = 40; % Pulo instantâneo no deslocamento para simular a excitação
v_excitacao = 0;
sis_livre = @(t, y) [y(2); -2*zeta_livre*wn*y(2) - wn^2*y(1)];
[t1, y1] = ode45(sis_livre, [t_excitacao t_ativacao], [x_excitacao v_excitacao], opcoes);

% Condições de contorno (último estado da oscilação livre passa para o amortecedor)
x_ativacao = y1(end, 1);
v_ativacao = y1(end, 2);

%% 3. Criação da Figura e Plotagem dos Subplots
figure('Name', 'Análise de Amortecimento Empilhada', 'Color', 'w', 'Position', [100, 50, 900, 900]);

for i = 1:3
    subplot(3, 1, i);
    hold on; grid on;
    
    % Fase 2: Amortecedor Ativado (86s a 400s)
    zeta_atual = zetas_teste(i);
    sis_amortecido = @(t, y) [y(2); -2*zeta_atual*wn*y(2) - wn^2*y(1)];
    [t2, y2] = ode45(sis_amortecido, [t_ativacao t_final], [x_ativacao v_ativacao], opcoes);
    
    % Plotando as 3 fases sequencialmente
    plot(t0, y0_x, 'Color', [0.4 0.4 0.4], 'LineWidth', 1); % Fase 0
    plot(t1, y1(:,1), 'Color', [0.6 0.6 0.6], 'LineWidth', 0.5); % Fase 1
    plot(t2, y2(:,1), 'Color', cores{i}, 'LineWidth', 1.2); % Fase 2

    
    % Linhas da envoltória de amplitude alvo
    %yline(limite_amplitude, '--m', 'LineWidth', 1);
    %yline(-limite_amplitude, '--m', 'LineWidth', 1);
    
    % Formatação do subplot
    title(titulos{i}, 'FontSize', 11);
    ylabel('d (\mum)', 'FontWeight', 'bold');
    xlim([0 t_final]);
    ylim([-50 50]);
    
    % Legenda apenas no primeiro gráfico
    if i == 1
        legend('Oscilação Inicial', 'Oscilação Livre', 'Location', 'northeast');
    end
    
    % Eixo X apenas no último gráfico
    if i == 3
        xlabel('Tempo (s)', 'FontWeight', 'bold');
    end
    
    hold off;
end
