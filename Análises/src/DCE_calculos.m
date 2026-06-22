clear all; clc; close all;

%% 1. DEFINIÇÃO DE PARÂMETROS FIXOS E VARIÁVEIS DO SISTEMA
% Constante dielétrica do vácuo
e0 = 8.85418781 * 10^(-12); % F/m

% Distâncias e Diâmetro (em metros)
DE = 0.001; % Distância longitudinal entre os eletrodos (1 mm)
d  = 31.8e-3; % Diâmetro menor (31.8 mm)
AE = (pi / 4) * (d)^2; % Área efetiva

% Limites de projeto da balança (convertidos de mN para N)
FE_min = 0.05e-3; 
FE_max = 10e-3;   

%% 2. CONJUNTO DE DADOS BASE
% --- DADOS EXPERIMENTAIS (INPE / Anselmo, 2017) ---
V_exp = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, ...
         550, 600, 650, 700, 750, 800, 850, 900, 950, 1000];
F_exp_uN = [0, 7, 27, 62, 109, 169, 245, 334, 435, 550, 679, ...
            822, 979, 1149, 1332, 1528, 1739, 1963, 2201, 2452, 2716];
F_exp_N = F_exp_uN * 1e-6; % Conversão para Newtons

%% 3. MODELAGEM EMPÍRICA (Curva do INPE)
% Ajuste polinomial de 2º grau (F = a*V^2 + b*V + c)
p_inpe = polyfit(V_exp, F_exp_N, 2);

%% 4. EXTRAPOLAÇÃO MATEMÁTICA E CÁLCULO DE RAÍZES
% Isolando V na equação analítica: V = DE * sqrt((2 * F) / (e0 * AE))
V_max_req_ana = DE * sqrt((2 * FE_max) / (e0 * AE));

% Para achar o V no modelo empírico (F = 10 mN)
coef_max = p_inpe; coef_max(3) = coef_max(3) - FE_max;
raizes_max = roots(coef_max);
V_max_req_inpe = max(raizes_max(imag(raizes_max)==0));

%% 5. GERAÇÃO DOS DADOS EXTRAPOLADOS PARA PLOTAGEM
% O eixo X vai até a maior tensão necessária (mais 5% de margem)
V_limite_plot = max(V_max_req_ana, V_max_req_inpe) * 1.05;
U_extrapolado = linspace(0, V_limite_plot, 200); 

% Curvas Extrapoladas
F_analitico_extra = 0.5 * e0 * (U_extrapolado ./ DE).^2 * AE;
F_inpe_extra = polyval(p_inpe, U_extrapolado); 

%% 6. GRÁFICO 1: COMPARAÇÃO E EXTRAPOLAÇÃO GERAL
figure('Name', 'Extrapolação: Força vs Tensão', 'Position', [100, 100, 850, 600]);
hold on; grid on; box on;

plot(U_extrapolado, F_analitico_extra, 'k-', 'LineWidth', 1.5, 'DisplayName', 'Modelo Analítico');
plot(U_extrapolado, F_inpe_extra, '--b', 'LineWidth', 1.5, 'DisplayName', 'Modelo Empírico Extrapolado (Anselmo, 2017)');
plot(V_exp, F_exp_N, 'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 5, 'DisplayName', 'Medições Físicas (Anselmo, 2017)');

% Marcação de pontos de projeto: F_max = 10 mN
plot(V_max_req_ana, FE_max, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 6, 'HandleVisibility', 'off');
plot(V_max_req_inpe, FE_max, 'bs', 'MarkerFaceColor', 'b', 'MarkerSize', 6, 'HandleVisibility', 'off');

% Limites de projeto (Linhas horizontais)
yline(FE_min, '--r', 'F_{min} = 0,05 mN', 'LabelHorizontalAlignment', 'left', 'HandleVisibility', 'off');
yline(FE_max, '--r', 'F_{max} = 10 mN', 'LabelHorizontalAlignment', 'left', 'HandleVisibility', 'off');

title('Extrapolação da Força Eletrostática e Tensão Aplicada (DE = 1 mm)', 'FontSize', 12, 'FontWeight', 'bold');
xlabel('Tensão Aplicada (V)', 'FontSize', 11); ylabel('Força Eletrostática (N)', 'FontSize', 11);
legend('Location', 'best', 'FontSize', 10);
xlim([0, V_limite_plot]); ylim([0, FE_max * 1.1]); 
hold off;


%% 7. AVALIAÇÃO DE ERRO RELATIVO DA ANÁLISE COMPLETA

% --- A) Erro Pontual (Fórmula vs Dados Físicos do INPE até 1000V) ---
F_analitico_em_Vexp = 0.5 * e0 * (V_exp ./ DE).^2 * AE;
idx_valid_pts = F_exp_N > 0; 
erro_rel_pontos = zeros(size(F_exp_N));
erro_rel_pontos(idx_valid_pts) = abs(F_analitico_em_Vexp(idx_valid_pts) - F_exp_N(idx_valid_pts)) ./ F_exp_N(idx_valid_pts) * 100;

% --- B) Erro Extrapolado (Fórmula vs Curva Empírica do INPE até ~1850V) ---
% Ignora tensões muito próximas a zero para evitar distorção assintótica na divisão
idx_valid_extra = U_extrapolado >= 50 & F_inpe_extra > 0; 
erro_rel_extrapolado = zeros(size(U_extrapolado));
erro_rel_extrapolado(idx_valid_extra) = abs(F_analitico_extra(idx_valid_extra) - F_inpe_extra(idx_valid_extra)) ./ F_inpe_extra(idx_valid_extra) * 100;


%% 8. GRÁFICO 2: ERRO RELATIVO COMPLETO
figure('Name', 'Erro Relativo Completo', 'Position', [150, 150, 750, 450]);
hold on; grid on; box on;

% Plota a curva do erro extrapolado contínuo
plot(U_extrapolado(idx_valid_extra), erro_rel_extrapolado(idx_valid_extra), '--k', ...
    'LineWidth', 1.5, 'DisplayName', 'Erro Relativo Contínuo (Analítico vs Empírico)');

% Sobrepõe os pontos de erro validados fisicamente
plot(V_exp(idx_valid_pts), erro_rel_pontos(idx_valid_pts), 'ko', ...
    'LineWidth', 1.5, 'MarkerSize', 5, 'MarkerFaceColor', 'k', ...
    'DisplayName', 'Erro Validado Fisicamente (vs Medições)');

yline(0, '--k', 'LineWidth', 1, 'HandleVisibility', 'off');

title('Evolução do Erro Relativo na Extrapolação Completa', 'FontSize', 12, 'FontWeight', 'bold');
xlabel('Tensão Aplicada (V)', 'FontSize', 11);
ylabel('Erro Relativo (%)', 'FontSize', 11);
legend('Location', 'best', 'FontSize', 10);
xlim([50, V_limite_plot]);
hold off;


%% 9. RESUMO NO CONSOLE
fprintf('\n========================================================================\n');
fprintf('                  RESULTADOS DA ANÁLISE DE ERRO COMPLETA                  \n');
fprintf('========================================================================\n');

fprintf('\n[ ZONA DE MEDIÇÃO FÍSICA (Até 1000V) ]\n');
fprintf('Erro Relativo Máximo    : %.2f%%\n', max(erro_rel_pontos));
fprintf('Erro Relativo Médio     : %.2f%%\n', mean(erro_rel_pontos(idx_valid_pts)));

fprintf('\n[ ZONA EXTRAPOLADA COMPLETA (Até %.0fV - Limite do Projeto) ]\n', V_limite_plot);
fprintf('Erro Relativo na Tensão de 10 mN (Analítico vs Empírico): %.2f%%\n', erro_rel_extrapolado(end));
fprintf('Erro Relativo Médio na faixa total extrapolada          : %.2f%%\n', mean(erro_rel_extrapolado(idx_valid_extra)));
fprintf('========================================================================\n\n');
