% script_calibracao_eletrostatica.m
% Plota a curva de calibração de Força vs Tensão Aplicada
close all; clear; clc;

% 1. Inicialização dos dados da tabela originais
V_aplicada = [0.0; 0.1; 0.2; 0.3; 0.4; 0.5; 0.6; 0.7; 0.8; 0.9; 1.0]; % [kV]
Force_mag = [0.0; 0.037196; 0.148784; 0.334765; 0.595137; ...
             0.929902; 1.339059; 1.822608; 2.380550; 3.012883; 3.719609]; % [mN]

% 2. Ajuste da Curva (Polinômio de 2º grau: F = a*V^2 + b*V + c)
p = polyfit(V_aplicada, Force_mag, 2);

% ========================================================
% MODIFICAÇÃO 1: Geração de pontos até 3.0 kV (3000 V)
V_curva = linspace(0, 2.0, 100); % Extrapolação até 3 kV
% ========================================================
F_curva = polyval(p, V_curva);

% 4. Criação e formatação da figura (Padrão Acadêmico)
figure;
hold on;
grid on;
box on;

% Plota os pontos reais (marcadores) e a curva de ajuste (linha contínua)
plot(V_curva, F_curva, 'k-', 'LineWidth', 1, 'DisplayName', 'Ajuste Quadratico (Extrapolado)');
plot(V_aplicada, Force_mag, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 5, 'DisplayName', 'Dados Simulados');

% Formatação de rótulos e título
title('Simulação DCE: Força vs Tensão Aplicada', 'FontSize', 12, 'FontWeight', 'bold');
xlabel('Tensão Aplicada (V) [kV]', 'FontSize', 11);
ylabel('Magnitude da Força Elestrostática [mN]', 'FontSize', 11);

% ========================================================
% MODIFICAÇÃO 2: Novo ajuste do eixo Y (Força) para caber os 33.5 mN
ylim([0.0 10]);
xlim([0 2.0]); % Adicionado um limite extra no eixo X para a curva respirar
% ========================================================

% Adiciona a legenda e ajusta a fonte dos eixos
legend('Location', 'northwest', 'Interpreter', 'latex', 'FontSize', 10);
set(gca, 'FontSize', 10, 'TickDir', 'out');

% 5. Exibição da equação governante no console
fprintf('Equação do ajuste metrológico:\n');
fprintf('F = %.6f * V^2 + (%.6f) * V + (%.6f)\n', p(1), p(2), p(3));
fprintf('\nForça projetada para 3000V (3.0 kV): %.4f mN\n', polyval(p, 3.0));
