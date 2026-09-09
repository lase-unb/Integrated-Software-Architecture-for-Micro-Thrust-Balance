clear all; clc;

% ==============================================================================
% 1. KNOWN INPUT DATA
% ==============================================================================
% Dados de sensibilidade obtidos no script CG_sensibilidade.m
S = 0.0582; % [m/N]
S_maior = 0.0939; % [m/N]
S_S2 = 0.0517;
S_1_junho = 0.0518;

% Vetor da primeira coluna (Deslocamento/Deflexão) em µm
d = [1.8039, 3.9369, 5.8372, 9.7834];
d_maior = [3.3523, 6.7382, 9.5474, 14.2316];
d_S2 = [1.843000, 2.953000, 3.832000, 8.125000, 12.431000, 16.988000, 11.738000, 16.135000, 21.305000, 17.254000, 23.252000, 30.319000, 25.455000, 35.177000, 46.763500, 31.620000, 39.336500];
d_1_junho = [2.403500, 3.558790, 8.633470, 13.283070, 17.047410, 11.899050, 11.899050, 17.967160, 23.099000, 17.077400, 25.282920, 43.202470, 19.815610, 30.164730, 39.264370, 26.991540, 63.414910];

d_todos = {d, d_maior, d_S2, d_1_junho};

% Vetor da segunda coluna (Força) em µN
f = [167.1960, 324.3694, 486.3337, 808.3664];
f_maior = [167.1960, 418.8246, 618.1822, 918.3950];
f_S2 = [38.7153, 73.7835, 108.8517, 166.9689, 318.2088, 469.4487, 219.4649, 418.2556, 617.0463, 323.9287, 617.3423, 910.7560, 481.2407, 917.1472, 1353.0536, 634.0472, 807.2681];
f_1_junho = [38.7153, 73.7835, 108.8517, 166.9689, 318.2088, 469.4487, 219.4649, 418.2556, 617.0463, 323.9287, 617.3423, 910.7560, 481.2407, 917.1472, 1353.0536, 634.0472, 807.2681];

f_todos = {f, f_maior, f_S2, f_1_junho};
S_todos = [S, S_maior, S_S2];

titulos_janela = {'S = 0.0582', 'S = 0.0939', 'S = 0.0697', 'S = 1 junho'};

caminhos_salvamento = {
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\sensibilidade intermediaria', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\maior sensibilidade', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\27_maio\S-2', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\1_junho'
};

% ==============================================================================
% DEFINIÇÃO DO REGIME DE EXTRAPOLAÇÃO: 50 µN (0.05 mN) até 100.000 µN (100 mN)
% (Mantemos o vetor interno em µN para o cálculo correto da Incerteza/Matrizes)
% ==============================================================================
F_extrapolada = linspace(50, 100000, 1000); 

% --- Loop 1: Gerar, plotar e salvar os gráficos individuais ---
for i = 1:3 
    d_atual = d_todos{i};
    f_atual = f_todos{i};
    S_atual = S_todos(i);
    caminho_atual = caminhos_salvamento{i};
    
    % Ajuste linear FORÇANDO A ORIGEM (F = a*d -> b=0)
    a = d_atual(:) \ f_atual(:);
    b = 0;
    
    % --- CÁLCULO DA MATRIZ DE COVARIÂNCIA E INCERTEZA ---
    N = length(d_atual);
    f_ajuste = a * d_atual + b;
    
    if N > 2
        s2 = sum((f_atual - f_ajuste).^2) / (N - 2); 
    else
        s2 = 1e-10; % Variância teórica mínima
    end
    
    X_mat = [d_atual(:), ones(N, 1)];
    C = s2 * inv(X_mat' * X_mat);
    var_a = C(1,1);
    var_b = C(2,2);
    cov_ab = C(1,2);
    % -----------------------------------------------------
    
    % Deslocamento Extrapolado (Baseado no vetor F_extrapolada)
    d_plot = F_extrapolada / a; 
    
    % Propagação da Incerteza 
    z = 2; % Fator de cobertura (95% de confiança)
    sigma_f = sqrt((d_plot.^2) * var_a + var_b + 2 * d_plot * cov_ab);
    
    f_sup = F_extrapolada + z * sigma_f;
    f_inf = F_extrapolada - z * sigma_f;
    
    fig = figure('Name', sprintf('Gráfico de Calibração - %s', titulos_janela{i}), ...
                 'Color', 'w', 'Position', [100 + (i*50), 100 + (i*50), 900, 500]);
       
    hold on;
    
    % 1. Plota a região de confiança sombreada (Forças divididas por 1000 para virar mN)
    fill([d_plot, fliplr(d_plot)], [f_sup/1000, fliplr(f_inf)/1000], 'r', ...
        'FaceAlpha', 0.15, 'EdgeColor', 'none', 'HandleVisibility', 'on');
    
    % 2. Plota a linha de tendência extrapolada (em mN)
    plot(d_plot, F_extrapolada/1000, 'r--', 'LineWidth', 1.5); 
    
    % 3. Plota os dados experimentais (em mN)
    plot(d_atual, f_atual/1000, 'bo', 'MarkerSize', 6, 'MarkerFaceColor', 'b'); 
    
    legend('Região de Confiança (95%)', 'Linha de Tendência', 'Dados Experimentais', 'Location', 'northwest');
    title(sprintf('Curva de Calibração para S = %.4f m/N', S_atual));
    xlabel('Deslocamento (\mum)');
    ylabel('Força F_{eq} (mN)'); % Label atualizado para mN
    
    % Impondo limites (0.05 a 100 mN)
    ylim([0.05 100]);
    xlim([min(d_plot) max(d_plot)]);
    
    grid on;
    hold off;
    
    % Salvar
    if ~exist(caminho_atual, 'dir')
        mkdir(caminho_atual);
    end
    nome_arquivo = sprintf('curva_calibracao_S_%.4f.png', S_atual);
    caminho_completo = fullfile(caminho_atual, nome_arquivo);
    saveas(fig, caminho_completo);
    fprintf('Gráfico individual salvo em: %s\n', caminho_completo);
end

% --- Nova Figura: Comparativo das Curvas de Tendência ---
fig_comp = figure('Name', 'Comparativo de Sensibilidades', 'Color', 'w', 'Position', [300, 200, 900, 500]);
hold on;

estilos_linha = {'-k', '--k', ':k'}; 
legendas_comp = cell(1, 3);
fprintf('\n--- Equações das Retas de Tendência (Feq = a * d) ---\n');
a_min = inf; 

for i = 1:3 
    d_atual = d_todos{i};
    f_atual = f_todos{i};
    S_atual = S_todos(i);
    
    % Ajuste linear forçando origem
    a = d_atual(:) \ f_atual(:);
    
    % Verifica a menor inclinação para definir o xlim dinâmico depois
    if a < a_min
        a_min = a;
    end
    
    % Extrapolação baseada na força
    d_plot = F_extrapolada / a;
    
    % Plota a linha extrapolada (convertida para mN dividindo por 1000)
    plot(d_plot, F_extrapolada/1000, estilos_linha{i}, 'LineWidth', 1.5);
    
    % Legenda e Impressão (Mantendo a equação impressa no console com as unidades da física originais)
    legendas_comp{i} = sprintf('S = %.4f m/N', S_atual);
    fprintf('S = %.4f m/N -> Feq(µN) = %.4f * d(µm)\n', S_atual, a);
end

legend(legendas_comp, 'Location', 'northwest');
title('Comparativo das Curvas de Calibração para Diferentes Configurações de Sensibilidade');
xlabel('Deslocamento (\mum)');
ylabel('Força F_{eq} (mN)'); % Label atualizado

% Impondo limites no gráfico comparativo de 0.05 mN até 100 mN
ylim([0.05 100]);

% Para o limite de deslocamento no gráfico comparativo
xlim([0 max(F_extrapolada / a_min)]);

grid on;
hold off;

fprintf('\nRotina finalizada com sucesso.\n');
