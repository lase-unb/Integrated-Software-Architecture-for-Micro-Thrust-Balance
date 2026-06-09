clear all; clc;
% ==============================================================================
% 1. KNOWN INPUT DATA
% ==============================================================================
% CG Positions [m]
CG_inter   = -0.3131; 
CG_menor   = -0.3369; 
CG_maior   = -0.0672;
CG_S2      = -0.09055;
CG_1_junho = -0.08859;

% Corresponding Sensitivities [m/N]
S         = 0.0582; 
S_menor   = 0.0179; 
S_maior   = 0.0939; 
S_S2      = 0.0697;
S_1_junho = 0.0712;

% Displacement and Force vectors for each case
d_inter = [1.8039, 3.9369, 5.8372, 9.7834];
f_inter = [167.1960, 324.3694, 486.3337, 808.3664];

d_menor = [1.4982, 4.3618];
f_menor = [167.1960, 618.1822];

d_maior = [3.3523, 6.7382, 9.5474, 14.2316];
f_maior = [167.1960, 418.8246, 618.1822, 918.3950];

d_S2 = [1.843000, 2.953000, 3.832000, 8.125000, 12.431000, 16.988000, 11.738000, 16.135000, 21.305000, 17.254000, 23.252000, 30.319000, 25.455000, 35.177000, 46.763500, 31.620000, 39.336500];
f_S2 = [38.7153, 73.7835, 108.8517, 166.9689, 318.2088, 469.4487, 219.4649, 418.2556, 617.0463, 323.9287, 617.3423, 910.7560, 481.2407, 917.1472, 1353.0536, 634.0472, 807.2681];

% Dados de 1 de Junho
d_1_junho = [2.403500, 3.558790, 8.633470, 13.283070, 17.047410, 11.899050, 11.899050, 17.967160, 23.099000, 17.077400, 25.282920, 43.202470, 19.815610, 30.164730, 39.264370, 26.991540, 63.414910];
f_1_junho = [38.7153, 73.7835, 108.8517, 166.9689, 318.2088, 469.4487, 219.4649, 418.2556, 617.0463, 323.9287, 617.3423, 910.7560, 481.2407, 917.1472, 1353.0536, 634.0472, 807.2681];

% ==============================================================================
% 2. EXTRACTION OF REAL CURVE COEFFICIENTS (F = a*d) - FORÇANDO A ORIGEM (0,0)
% ==============================================================================
a_inter = d_inter(:) \ f_inter(:);
p_inter = [a_inter, 0];

a_menor = d_menor(:) \ f_menor(:);
p_menor = [a_menor, 0];

a_maior = d_maior(:) \ f_maior(:);
p_maior = [a_maior, 0];

a_S2 = d_S2(:) \ f_S2(:);
p_S2 = [a_S2, 0];

a_1_junho = d_1_junho(:) \ f_1_junho(:);
p_1_junho = [a_1_junho, 0];

% --- R^2 CALCULATION BLOCK ---
y_fit_inter = polyval(p_inter, d_inter);
SQ_res_inter = sum((f_inter - y_fit_inter).^2);
SQ_tot_inter = (length(f_inter)-1) * var(f_inter);
R2_inter = 1 - (SQ_res_inter / SQ_tot_inter);

y_fit_menor = polyval(p_menor, d_menor);
SQ_res_menor = sum((f_menor - y_fit_menor).^2);
SQ_tot_menor = (length(f_menor)-1) * var(f_menor);
R2_menor = 1 - (SQ_res_menor / SQ_tot_menor);

y_fit_maior = polyval(p_maior, d_maior);
SQ_res_maior = sum((f_maior - y_fit_maior).^2);
SQ_tot_maior = (length(f_maior)-1) * var(f_maior);
R2_maior = 1 - (SQ_res_maior / SQ_tot_maior);

y_fit_S2 = polyval(p_S2, d_S2);
SQ_res_S2 = sum((f_S2 - y_fit_S2).^2);
SQ_tot_S2 = (length(f_S2)-1) * var(f_S2);
R2_S2 = 1 - (SQ_res_S2 / SQ_tot_S2);

y_fit_1_junho = polyval(p_1_junho, d_1_junho);
SQ_res_1_junho = sum((f_1_junho - y_fit_1_junho).^2);
SQ_tot_1_junho = (length(f_1_junho)-1) * var(f_1_junho);
R2_1_junho = 1 - (SQ_res_1_junho / SQ_tot_1_junho);

% Print R^2 results to the Command Window
fprintf('--- R^2 Coefficients ---\n');
fprintf('S = %.4f m/N (Lower CG)  -> R^2 = %.4f\n', S_menor, R2_menor);
fprintf('S = %.4f m/N (Inter CG)  -> R^2 = %.4f\n', S, R2_inter);
fprintf('S = %.4f m/N (S2 CG)     -> R^2 = %.4f\n', S_S2, R2_S2);
fprintf('S = %.4f m/N (1 Junho)   -> R^2 = %.4f\n', S_1_junho, R2_1_junho);
fprintf('S = %.4f m/N (Higher CG) -> R^2 = %.4f\n\n', S_maior, R2_maior);

% ==============================================================================
% 3. MATHEMATICAL MODELING (CALIBRATION SURFACE)
% ==============================================================================
% O caso 1_junho foi adicionado aos vetores conhecidos para compor o modelo
CG_conhecidos = [CG_menor, CG_inter, CG_S2, CG_1_junho, CG_maior];
S_conhecidos  = [S_menor, S, S_S2, S_1_junho, S_maior]; 
a_conhecidos  = [p_menor(1), p_inter(1), p_S2(1), p_1_junho(1), p_maior(1)];
b_conhecidos  = [p_menor(2), p_inter(2), p_S2(2), p_1_junho(2), p_maior(2)]; % Serão todos 0

poly_a = polyfit(CG_conhecidos, a_conhecidos, 2);
poly_b = polyfit(CG_conhecidos, b_conhecidos, 2); 

% ==============================================================================
% 4. PREDICTION TEST FOR A NEW CG (Simulation)
% ==============================================================================
CG_alvo = -0.2000; % [m]
a_estimado = polyval(poly_a, CG_alvo);
b_estimado = polyval(poly_b, CG_alvo);

fprintf('--- Predictive Model for CG = %.4f m ---\n', CG_alvo);
fprintf('Estimated Angular Coefficient (a): %.4f\n', a_estimado);
fprintf('Estimated Linear Coefficient (b): %.4f\n', b_estimado);
fprintf('New line equation: Feq = %.4f * d %+.4f\n\n', a_estimado, b_estimado);

% ==============================================================================
% 5. PLOTTING RESULTS 
% ==============================================================================
% Figure 1: Coefficient Behavior vs CG Position
figure('Name', 'Calibration Parameters vs CG Position', 'Color', 'w', 'Position', [100, 100, 500, 400]);

CG_plot = linspace(min(CG_conhecidos), max(CG_conhecidos), 100);
a_plot = polyval(poly_a, CG_plot);

plot(CG_plot, a_plot, '-k', 'LineWidth', 1); hold on;
scatter(CG_conhecidos, a_conhecidos, 40, 'k', 'filled'); 

for i = 1:length(CG_conhecidos)
    text(CG_conhecidos(i), a_conhecidos(i), sprintf('  S = %.4f m/N', S_conhecidos(i)), ...
        'VerticalAlignment', 'middle', 'HorizontalAlignment', 'left', 'FontSize', 11);
end

title('Comportamento da Rigidez Linear do Sistema', 'Fontsize', 12);
xlabel('Posição do CG (m)');
ylabel('Rigidez Linear');
legend('Modelo Preditivo', 'Amostra', 'Location', 'best', 'FontSize', 11);
grid on;

% ==============================================================================
% Figure 2: Estimated Calibration Curve vs Reals
% ==============================================================================
figure('Name', 'Curva de Calibração Estimada', 'Color', 'w', 'Position', [650, 100, 600, 500]);
hold on;

% Vetor de Deslocamento começando em 0 e indo até 4000 µm
d_plot = linspace(0, 4000, 1000); 

% Plotamos as retas com estilos de linha diferentes (F = a * d)
p1 = plot(d_plot, d_plot * p_menor(1), '-k',  'LineWidth', 2);   % Linha contínua
p2 = plot(d_plot, d_plot * p_inter(1), '--k', 'LineWidth', 2);   % Linha tracejada
p3 = plot(d_plot, d_plot * p_S2(1),    '-.k', 'LineWidth', 2);   % Linha traço-ponto
p4 = plot(d_plot, d_plot * p_maior(1), ':k',  'LineWidth', 2.5); % Linha pontilhada
p5 = plot(d_plot, d_plot * p_1_junho(1), '-', 'Color', [0.5 0.5 0.5], 'LineWidth', 2); % Linha contínua cinza para 1_junho

xlabel('Deslocamento (\mum)');
ylabel('Força F_{eq} (\muN)');
% Limite Y imposto de 10 a 100.000 µN mantido
ylim([10 100000]); 
% Limite X forçado de 0 até 4000 µm
xlim([0 4000]);

% Criando a legenda dinâmica com as respectivas sensibilidades (agora com 5 curvas)
legend([p1, p2, p3, p5, p4], ...
    sprintf('S = %.4f m/N', S_menor), ...
    sprintf('S = %.4f m/N', S), ...
    sprintf('S = %.4f m/N', S_S2), ...
    sprintf('S = %.4f m/N (1 Junho)', S_1_junho), ...
    sprintf('S = %.4f m/N', S_maior), ...
    'Location', 'best', 'FontSize', 12);
grid on;
hold off;
