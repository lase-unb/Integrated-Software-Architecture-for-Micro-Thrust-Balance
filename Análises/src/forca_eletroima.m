clear all; clc;
% ---------------------------------------------------------
% DADOS DO EXPERIMENTO
% ---------------------------------------------------------
d = [7.71; 10.77; 14.19; 17.18; 20.02; 21.85]; % Distância (mm)
f = [0.065727; 0.030411; 0.014715; 0.006867; 0.003924; 0.002943]; % Força (N)

% ---------------------------------------------------------
% CÁLCULO E PROPAGAÇÃO DE ERRO
% ---------------------------------------------------------
g = 9.81; % m/s^2 (Aceleração da gravidade)
erro_massa_g = 0.05; % Incerteza da balança em gramas
erro_massa_kg = erro_massa_g / 1000; % Conversão para kg
erro_forca = erro_massa_kg * g; % Erro em Newtons (N)

% Vetor de erros para os dados experimentais
err_f = repmat(erro_forca, length(f), 1);

% ---------------------------------------------------------
% REGRESSÃO NÃO-LINEAR (CURVE FITTING)
% ATENÇÃO: O ajuste é feito SOMENTE com os dados reais experimentais
% ---------------------------------------------------------
% Ajuste: Lei de Potência (F = a * d^b)
[fit_power, gof_power] = fit(d, f, 'power1');

% ---------------------------------------------------------
% EXTENSÃO DA CURVA (EXTRAPOLAÇÃO)
% ---------------------------------------------------------
% Criar pontos contínuos de 2 mm a 25 mm para desenhar a curva
d_ext = linspace(2, 25, 300)'; 
f_power_ext = fit_power(d_ext); % Aplica a equação da potência na extensão

% ---------------------------------------------------------
% PLOTAGEM DO GRÁFICO
% ---------------------------------------------------------
figure('Name', 'Força Magnética vs Distância (Modelo: Lei de Potência)', 'Color', 'w');
hold on; grid on;

% Plota a linha de tendência estendida (2 a 25 mm)
p1 = plot(d_ext, f_power_ext, 'b--', 'LineWidth', 1);

% Plota os dados reais com barras de erro
p2 = errorbar(d, f, err_f, 'ko', 'MarkerFaceColor', 'k', 'MarkerSize', 6, 'LineWidth', 1.2);

% Formatação e limites do gráfico
xlim([0, 26]); % Garante que o eixo X vá um pouco antes de 2 e depois de 25
ylim([-0.05, max(f_power_ext) * 1.05]); % Escala o eixo Y para caber o pico em 2mm

xlabel('Distância (mm)', 'FontSize', 12, 'FontWeight', 'bold');
ylabel('Força Magnética (N)', 'FontSize', 12, 'FontWeight', 'bold');
title('Decaimento da Força do Eletroímã', 'FontSize', 14);

% Legenda ajustada
legend([p2, p1], ...
    sprintf('Dados Experimentais \\pm %.5f N', erro_forca), ...
    sprintf('Lei de Potência: F = %.4f*d^{%.4f} (R^2 = %.4f)', fit_power.a, fit_power.b, gof_power.rsquare), ...
    'Location', 'northeast', 'FontSize', 10);

% ---------------------------------------------------------
% IMPRESSÃO DOS RESULTADOS NO CONSOLE
% ---------------------------------------------------------
fprintf('--- RESULTADOS DO AJUSTE (LEI DE POTÊNCIA) ---\n');
fprintf('Incerteza Constante da Força: +/- %.6f N\n\n', erro_forca);
fprintf('Equação: F = a * d^b\n');
fprintf('   a  = %.4f\n', fit_power.a);
fprintf('   b  = %.4f\n', fit_power.b);
fprintf('   R² = %.4f\n\n', gof_power.rsquare);

fprintf('--- PREVISÃO POR EXTRAPOLAÇÃO ---\n');
fprintf('Força estimada a 2 mm: %.4f N\n', fit_power(2));

% ---------------------------------------------------------
% SALVANDO FIGURA
% ---------------------------------------------------------
folder = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\eletroima-forca'; 

filename = ['forca-vs-deslocamento-eletroima-LaSE.png'];

% Create the full path
fullPath = fullfile(folder, filename);

% Save the current figure (gcf) to that path
exportgraphics(gcf, fullPath, 'Resolution', 300); 

% Imprime mensagem de confirmação de salvamento
fprintf('Gráfico salvo com sucesso em:\n%s\n', fullPath);
