clear all; clc;

% 1. DADOS DE ENTRADA CONHECIDOS
% Posições do CG [m]
CG_inter = -0.3131; 
CG_menor = -0.3369; 
CG_maior = -0.0672; 

% Sensibilidades correspondentes [m/N]
S = 0.0582; 
S_menor = 0.0179; 
S_maior = 0.0939; 

% Vetores de Deslocamento e Força para cada caso
d_inter = [1.8039, 3.9369, 5.8372, 9.7834];
f_inter = [167.1960, 324.3694, 486.3337, 808.3664];

d_menor = [1.4982, 4.3618];
f_menor = [167.1960, 618.1822];

d_maior = [3.3523, 6.7382, 9.5474, 14.2316];
f_maior = [167.1960, 418.8246, 618.1822, 918.3950];

% 2. EXTRAÇÃO DOS COEFICIENTES DAS CURVAS REAIS (F = a*d + b)
p_inter = polyfit(d_inter, f_inter, 1);
p_menor = polyfit(d_menor, f_menor, 1);
p_maior = polyfit(d_maior, f_maior, 1);

% Agrupando os dados na mesma ordem (Menor CG, Intermediário, Maior CG)
CG_conhecidos = [CG_menor, CG_inter, CG_maior];
S_conhecidos = [S_menor, S, S_maior]; % Vetor auxiliar para os rótulos de texto
a_conhecidos = [p_menor(1), p_inter(1), p_maior(1)];
b_conhecidos = [p_menor(2), p_inter(2), p_maior(2)];

% 3. MODELAGEM MATEMÁTICA (SUPERFÍCIE DE CALIBRAÇÃO)
poly_a = polyfit(CG_conhecidos, a_conhecidos, 2);
poly_b = polyfit(CG_conhecidos, b_conhecidos, 2);

% 4. TESTE DE PREVISÃO PARA UM NOVO CG (Simulação)
CG_alvo = -0.2000; % [m] -> Exemplo de um CG que você nunca mediu

% Estimando a nova reta
a_estimado = polyval(poly_a, CG_alvo);
b_estimado = polyval(poly_b, CG_alvo);

fprintf('--- Modelo Preditivo para CG = %.4f m ---\n', CG_alvo);
fprintf('Coeficiente Angular (a) estimado: %.4f\n', a_estimado);
fprintf('Coeficiente Linear (b) estimado: %.4f\n', b_estimado);
fprintf('Equação da nova reta: Feq = %.4f * d %+.4f\n\n', a_estimado, b_estimado);

% 5. PLOTAGEM DOS RESULTADOS 

% Figura 1: Comportamento dos Coeficientes em relação ao CG
figure('Name', 'Parâmetros de Calibração vs Posição do CG', 'Color', 'w', 'Position', [100, 100, 800, 400]);

% Plot do Coeficiente Angular 'a' (Rigidez)
subplot(1, 2, 1);
CG_plot = linspace(min(CG_conhecidos), max(CG_conhecidos), 100);
a_plot = polyval(poly_a, CG_plot);
plot(CG_plot, a_plot, '-k', 'LineWidth', 1); hold on;
scatter(CG_conhecidos, a_conhecidos, 40, 'k', 'filled'); % Pontos medidos

% Adicionando os rótulos de sensibilidade nos pontos medidos (Rigidez)
for i = 1:length(CG_conhecidos)
    text(CG_conhecidos(i), a_conhecidos(i), sprintf('  S = %.4f', S_conhecidos(i)), ...
        'VerticalAlignment', 'middle', 'HorizontalAlignment', 'left', 'FontSize', 9);
end

%scatter(CG_alvo, a_estimado, 40, 'b*', 'LineWidth', 1.5); % Ponto estimado
title('Comportamento da Rigidez (a)');
xlabel('Posição do CG (m)');
ylabel('Coef. Angular (a)');
%legend('Modelo Preditivo', 'Dados Reais', 'Estimativa Nova', 'Location', 'best');
legend('Modelo Preditivo', 'Dados Reais', 'Location', 'best');
grid on;

% Plot do Coeficiente Linear 'b' (Offset)
subplot(1, 2, 2);
b_plot = polyval(poly_b, CG_plot);
plot(CG_plot, b_plot, '-k', 'LineWidth', 1); hold on;
scatter(CG_conhecidos, b_conhecidos, 40, 'k', 'filled'); 

% Adicionando os rótulos de sensibilidade nos pontos medidos (Offset)
for i = 1:length(CG_conhecidos)
    text(CG_conhecidos(i), b_conhecidos(i), sprintf('  S = %.4f', S_conhecidos(i)), ...
        'VerticalAlignment', 'middle', 'HorizontalAlignment', 'left', 'FontSize', 9);
end

%scatter(CG_alvo, b_estimado, 40, 'b*', 'LineWidth', 1.5); 
title('Comportamento do Offset (b)');
xlabel('Posição do CG (m)');
ylabel('Coef. Linear (b)');
grid on;

% Figura 2: Curva de Calibração Estimada vs Reais
figure('Name', 'Curva de Calibração Estimada', 'Color', 'w', 'Position', [950, 100, 600, 500]);
hold on;

% Plotando as 3 retas reais
d_plot_real = linspace(0, 15, 50);
plot(d_plot_real, polyval(p_menor, d_plot_real), ':k', 'LineWidth', 1);
plot(d_plot_real, polyval(p_inter, d_plot_real), ':k', 'LineWidth', 1);
plot(d_plot_real, polyval(p_maior, d_plot_real), ':k', 'LineWidth', 1);

% Rótulos da Figura 2
x_pos_menor = 4;
y_pos_menor = polyval(p_menor, x_pos_menor);
text(x_pos_menor, y_pos_menor + 40, 'S = 0,0179 m/N', 'FontSize', 10, 'HorizontalAlignment', 'center');

x_pos_inter = 8.5;
y_pos_inter = polyval(p_inter, x_pos_inter);
text(x_pos_inter, y_pos_inter + 40, 'S = 0,0582 m/N', 'FontSize', 10, 'HorizontalAlignment', 'center');

x_pos_maior = 12.5;
y_pos_maior = polyval(p_maior, x_pos_maior);
text(x_pos_maior, y_pos_maior + 40, 'S = 0,0939 m/N', 'FontSize', 10, 'HorizontalAlignment', 'center');

% Plotando a nova reta estimada
d_plot_estimado = linspace(0, 15, 50);
f_estimada = polyval([a_estimado, b_estimado], d_plot_estimado);
%plot(d_plot_estimado, f_estimada, '-b', 'LineWidth', 2);

%title(sprintf('Previsão de Calibração para CG = %.4f m', CG_alvo));
title(sprintf('Curvas de Calibração para Diferentes Sensibilidades'));
xlabel('Deslocamento (\mum)');
ylabel('Força F_{eq} (\muN)');
%legend('Casos Reais Medidos', '', '', 'Curva Estimada (Nova)', 'Location', 'northwest');
legend('Casos Reais Medidos', '', '', 'Location', 'northwest');
grid on;
ylim([0 1000]); 
hold off;
