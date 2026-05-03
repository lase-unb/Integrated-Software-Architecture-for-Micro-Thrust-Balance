clear all; clc;
% dados de sensibilidade obtidos no script CG_sensibilidade.m
S = 0.0582; % [m/N]
S_menor = 0.0179; % [m/N]
S_maior = 0.0939; % [m/N]
CG = -0.3131; % [m] em relação ao pivô
CG_menor = -0.3369; % [m] em relação ao pivô
CG_maior = -0.0672; % [m] em relação ao pivô

% Vetor da primeira coluna (ex: Deslocamento/Deflexão)
d = [1.8039, 3.9369, 5.8372, 9.7834];
desvio_padrao_d = [0.130990767, 0.188488684, 0.279612644, 0.303495368];

d_menor = [1.4982, 4.3618];
desvio_padrao_d_menor = [0.132113257, 0.09809839705];

d_maior = [3.3523, 6.7382, 9.5474, 14.2316];
desvio_padrao_d_maior = [0.05143538368, 0.2499271287, 0.2451215176, 0.2824337905];

% Agrupamento ajustado para Cell Arrays ({})
% Ordem padronizada: {Intermediária, Menor, Maior}
d_todos = {d, d_menor, d_maior};
desvio_padrao_todos = {desvio_padrao_d, desvio_padrao_d_menor, desvio_padrao_d_maior};

% Vetor da segunda coluna (ex: Força)
f = [167.1960, 324.3694, 486.3337, 808.3664];
f_menor = [167.1960, 618.1822];
f_maior = [167.1960, 418.8246, 618.1822, 918.3950];
f_todos = {f, f_menor, f_maior};

% Encontra a força máxima global para usar na extrapolação
max_F = max([f, f_menor, f_maior]);

% Vetores auxiliares para o loop
S_todos = [S, S_menor, S_maior];
titulos_janela = {'S = 0.0582 (Intermediária)', 'S = 0.0179 (Menor)', 'S = 0.0939 (Maior)'};

% Definição dos caminhos de salvamento
caminhos_salvamento = {
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\sensibilidade intermediaria', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\menor sensibilidade', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\maior sensibilidade'
};

% --- Loop 1: Gerar, plotar e salvar os gráficos individuais ---
for i = 1:3
    d_atual = d_todos{i};
    f_atual = f_todos{i};
    desvio_atual = desvio_padrao_todos{i};
    S_atual = S_todos(i);
    caminho_atual = caminhos_salvamento{i};
    
    % Ajuste linear
    p = polyfit(d_atual, f_atual, 1);
    
    % Extrapolação da linha de tendência até a força máxima
    % d = (F - b) / a
    d_max_extrapolado = (max_F - p(2)) / p(1);
    d_plot = [min(d_atual), d_max_extrapolado]; % Vetor de X para a linha
    f_plot = polyval(p, d_plot);                % Vetor de Y para a linha
    
    fig = figure('Name', sprintf('Gráfico de Calibração - %s', titulos_janela{i}), ...
                 'Color', 'w', 'Position', [100 + (i*50), 100 + (i*50), 900, 500]);
       
    % Plota os dados reais com a barra de erro
    errorbar(d_atual, f_atual, desvio_atual, 'horizontal', 'o', 'MarkerSize', 6, 'MarkerFaceColor', 'b'); 
    hold on;
    
    % Plota a linha de tendência extrapolada
    plot(d_plot, f_plot, 'r--', 'LineWidth', 1); 
    
    legend('Dados \pm Desvio Padrão', 'Linha de Tendência', 'Location', 'best');
    title(sprintf('Curva de Calibração para S = %.4f m/N', S_atual));
    xlabel('Deslocamento (\mum)');
    ylabel('Força F_{eq} (\muN)');
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

estilos_linha = {'-k', ':k', '-.k'}; 
legendas_comp = cell(1, 3);

fprintf('\n--- Equações das Retas de Tendência (Feq = a * d + b) ---\n');

for i = 1:3
    d_atual = d_todos{i};
    f_atual = f_todos{i};
    S_atual = S_todos(i);

    % Ajuste linear
    p = polyfit(d_atual, f_atual, 1);
    
    % Extrapolação para o gráfico comparativo
    d_max_extrapolado = (max_F - p(2)) / p(1);
    d_plot = [min(d_atual), d_max_extrapolado];
    f_plot = polyval(p, d_plot);

    % Plota a linha extrapolada
    plot(d_plot, f_plot, estilos_linha{i}, 'LineWidth', 1);

    % Legenda e Impressão
    legendas_comp{i} = sprintf('S = %.4f m/N', S_atual);
    fprintf('S = %.4f m/N -> Feq = %.4f * d %+.4f\n', S_atual, p(1), p(2));
end

% Configurações da figura comparativa
legend(legendas_comp, 'Location', 'best');
title('Comparativo das Curvas de Calibração para Diferentes Configurações de Sensibilidade');
xlabel('Deslocamento (\mum)');
ylabel('Força F_{eq} (\muN)');
grid on;
hold off;
fprintf('\nRotina finalizada com sucesso.\n');
