clear all; clc;

% ---------------------------------------------------------
% DADOS COLETADOS
% ---------------------------------------------------------
d = [7.71; 10.77; 14.19; 17.18; 20.02; 21.85]; % Distância (mm)

% Massa real medida pela balança em kg 
massa_kg = [0.0067; 0.0031; 0.0015; 0.0007; 0.0004; 0.0003]; 

% Define a gravidade local (Brasília - DF) e sua incerteza (estimada)
g_local = 9.78; % m/s^2 
erro_g = 0.02;  % m/s^2 

% Cálculo da Força Magnética (N)
f = massa_kg * g_local; 

% ---------------------------------------------------------
% CÁLCULO E PROPAGAÇÃO RIGOROSA DE ERRO
% ---------------------------------------------------------
erro_massa_g = 0.05; % Incerteza instrumental da balança (gramas)
erro_massa_kg = erro_massa_g / 1000; % Conversão para kg

% Fórmula de propagação de incertezas independentes:
% delta_F = sqrt((g * delta_m)^2 + (m * delta_g)^2)
err_f = sqrt((g_local * erro_massa_kg)^2 + (massa_kg .* erro_g).^2);

% ---------------------------------------------------------
% REGRESSÃO NÃO-LINEAR (CURVE FITTING)
% ---------------------------------------------------------
% Ajuste: Lei de Potência (F = a * d^b)
[fit_power, gof_power] = fit(d, f, 'power1');

% ---------------------------------------------------------
% EXTENSÃO DA CURVA (EXTRAPOLAÇÃO)
% ---------------------------------------------------------
d_ext = linspace(2, 25, 300)'; 
f_power_ext = fit_power(d_ext);

% ---------------------------------------------------------
% PLOTAGEM DO GRÁFICO
% ---------------------------------------------------------
figure('Name', 'Força Magnética vs Distância (Gravidade Local)', 'Color', 'w');
hold on; grid on;

% Plota a linha de tendência estendida (2 a 25 mm)
p1 = plot(d_ext, f_power_ext, 'r--', 'LineWidth', 1);

% Plota os dados reais com barras de erro
p2 = errorbar(d, f, err_f, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 6, 'LineWidth', 1);

% ---------------------------------------------------------
% FORMATAÇÃO DOS EIXOS E GRADE
% ---------------------------------------------------------
xlim([0, 26]);
ylim([-0.05, max(f_power_ext) * 1.05]);

xticks(0:1:26); 

xlabel('Distância (mm)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Força Magnética (N)', 'FontSize', 12, 'FontWeight', 'bold');
title('Decaimento da Força do Eletroímã pela Distância', 'FontSize', 14);

legend([p2, p1], ...
    'Dados Experimentais \pm Erro Propagado', ...
    sprintf('Lei de Potência: F = %.4f*d^{%.4f} (R^2 = %.4f)', fit_power.a, fit_power.b, gof_power.rsquare), ...
    'Location', 'northeast', 'FontSize', 10);

% ---------------------------------------------------------
% IMPRESSÃO DOS RESULTADOS NO CONSOLE
% ---------------------------------------------------------
fprintf('--- RESULTADOS DA MEDIÇÃO ---\n');
fprintf('Massa máxima lida: %.1f g\n', max(massa_kg)*1000);
fprintf('Força máxima (g = 9.78): %.6f N\n\n', max(f));

fprintf('--- RESULTADOS DO AJUSTE (LEI DE POTÊNCIA) ---\n');
fprintf('Incerteza da Força (variável com a massa):\n');
fprintf('  -> Erro máx (na menor dist): +/- %.6f N\n', err_f(1));
fprintf('  -> Erro min (na maior dist): +/- %.6f N\n\n', err_f(end));
fprintf('Equação: F = a * d^b\n');
fprintf('   a  = %.4f\n', fit_power.a);
fprintf('   b  = %.4f\n', fit_power.b);
fprintf('   R² = %.4f\n\n', gof_power.rsquare);

fprintf('--- PREVISÃO POR EXTRAPOLAÇÃO ---\n');
fprintf('Força estimada a 2 mm: %.4f N\n\n', fit_power(2));

% ---------------------------------------------------------
% SALVANDO FIGURA
% ---------------------------------------------------------
folder = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\eletroima-forca'; 
filename = 'forca-vs-deslocamento-eletroima-LaSE.png';
% Create the full path
fullPath = fullfile(folder, filename);
% Save the current figure (gcf) to that path
exportgraphics(gcf, fullPath, 'Resolution', 300); 
% Imprime mensagem de confirmação de salvamento
fprintf('Gráfico salvo com sucesso em:\n%s\n', fullPath);
