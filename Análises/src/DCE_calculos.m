clear all; clc; close all;

%% 1. DEFINIÇÃO DE PARÂMETROS FIXOS
% Constante dielétrica do vácuo
e0 = 8.85418781 * 10^(-12); % F/m

% Distâncias (em metros)
DE = 0.0005; % Distância longitudinal entre os eletrodos (gap de separação)
g  = 0.0005; % Gap radial entre o eletrodo menor e o anel de guarda 

% Faixa de força alvo para calibração (em N)
FE_min = 0.00002; % 20 uN
FE_max = 0.020;   % 20 mN

% Vetor de tensões a serem aplicadas (de 0 a 1000 V)
% Aumentado para 100 pontos para garantir curvas suaves no plot
U = linspace(0, 1200, 100); 

%% 2. PARÂMETROS DE ANÁLISE (DIÂMETROS)
% Definindo um vetor de diâmetros para testar (ex: de 20 mm a 60 mm)
% d_testes contém os valores em metros
d_testes = 0.0318 : 0.005 : 0.060;

%% 3. PREPARAÇÃO DA FIGURA
figure('Name', 'Análise Paramétrica do DCE', 'Position', [100, 100, 800, 600]);
hold on; grid on;

%% 4. LOOP DE CÁLCULO E PLOTAGEM
for i = 1:length(d_testes)
    d = d_testes(i); % Seleciona o diâmetro da iteração atual
    
    % Cálculo da área efetiva do eletrodo menor (m^2)
    AE = (pi / 4) * (d)^2; 
    
    % Calculo da força gerada (N)
    % Nota: Uso de './' e '.^' para operações element-wise no vetor U
    FE = 0.5 * e0 * (U ./ DE).^2 * AE;
    
    % Plot da curva para o diâmetro atual
    % Convertendo d para mm apenas para o texto da legenda
    plot(U, FE, 'LineWidth', 1.5, 'DisplayName', sprintf('D = %.2f mm', d * 1000));
end

%% 5. MARCAÇÃO DOS LIMITES DE PROJETO
% Desenha linhas horizontais vermelhas tracejadas para mostrar a janela de operação
yline(FE_min, '--r', 'F_{min} (20 \muN)', 'LineWidth', 1.5, 'LabelHorizontalAlignment', 'left');
yline(FE_max, '--r', 'F_{max} (20 mN)', 'LineWidth', 1.5, 'LabelHorizontalAlignment', 'left');

%% 6. FORMATAÇÃO DO GRÁFICO
xlabel('Tensão Aplicada U (V)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Força Eletrostática F_E (N)', 'FontSize', 12, 'FontWeight', 'bold');
title('Dimensionamento do DCE: Força vs Tensão para Diferentes Diâmetros', 'FontSize', 14);
legend('Location', 'northwest', 'FontSize', 11);

% Ajuste dos eixos para focar na região de interesse
xlim([0, 1200]); 
ylim([0, 0.04]); 
hold off;
