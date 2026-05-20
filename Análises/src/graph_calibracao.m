clear all; clc; close all;

%% ESTE SCRIPT BUSCA PLOTAR AS CURVAS DE CALIBRAÇÃO INDIVIDUALMENTE E TAMBÉM UM GRAFICO UNIFICANDO TODAS AS CURVAS

% === PARÂMETROS DA BALANÇA ===
% Sensibilidades [m/N]
S_todos = [0.0582, 0.0179, 0.0939];
titulos_janela = {'S = 0.0582 (Intermediária)', 'S = 0.0179 (Menor)', 'S = 0.0939 (Maior)'};

% === CAMINHOS DE DIRETÓRIOS ===
caminhos_salvamento = {
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\sensibilidade intermediaria', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\menor sensibilidade', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\maior sensibilidade'
    };

% Caminhos dos arquivos de dados crus (.txt)
caminhos_txt = {
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\sensibilidade intermediaria\resultados_curvaCalibracao_sensIntermed.txt', ... % Mude aqui quando tiver a intermediária
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\menor sensibilidade\resultados_curvaCalibracao_menorSensibilidade.txt', ...
    'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\maior sensibilidade\resultados_curvaCalibracao_maiorSensibilidade.txt'
    };

% Limites de Força definidos para os gráficos
F_min_plot = 0;   % [uN]
F_max_plot = 1000; % [uN]

% === 1. LEITURA E PREPARAÇÃO DOS DADOS CRUS ===
d_crus_todos = cell(1, 3);
f_crus_todos = cell(1, 3);

fprintf('--- Importando Dados Crus ---\n');
for i = 1:3
    caminho_arquivo = caminhos_txt{i};
    if ~isempty(caminho_arquivo) && exist(caminho_arquivo, 'file')
        % Lê a tabela do arquivo
        tabela_cru = readtable(caminho_arquivo, 'Delimiter', '\t');

        % Extrai colunas
        f_temp = tabela_cru.Forca_Equivalente_uN;
        d_temp = tabela_cru.Deslocamento_script_um;

        % Conversão segura (Texto com vírgula -> Número com ponto)
        if iscell(f_temp) || isstring(f_temp) || ischar(f_temp)
            f_num = str2double(strrep(string(f_temp), ',', '.'));
        else
            f_num = double(f_temp);
        end

        if iscell(d_temp) || isstring(d_temp) || ischar(d_temp)
            d_num = str2double(strrep(string(d_temp), ',', '.'));
        else
            d_num = double(d_temp);
        end

        % Remove possíveis NaNs (linhas em branco no fim do txt)
        idx_validos = ~isnan(d_num) & ~isnan(f_num);
        d_num = d_num(idx_validos);
        f_num = f_num(idx_validos);

        % Salva na matriz de células
        d_crus_todos{i} = d_num;
        f_crus_todos{i} = f_num;

        fprintf('S = %.4f: %d amostras carregadas com sucesso.\n', S_todos(i), length(d_num));
    else
        fprintf('S = %.4f: Arquivo TXT não encontrado. Ignorando esta sensibilidade.\n', S_todos(i));
    end
end
fprintf('\n');

% === 2. GERAÇÃO DOS GRÁFICOS INDIVIDUAIS ===
% Variáveis para armazenar os dados dos modelos e gerar o comparativo
coef_a_salvos = zeros(1,3);
coef_b_salvos = zeros(1,3);
R2_salvos = zeros(1,3);
dados_existem = false(1,3);

for i = 1:3
    % Se a célula estiver vazia (sem dados), pula para a próxima iteração
    if isempty(d_crus_todos{i})
        continue;
    end

    dados_existem(i) = true;
    d_calculo = d_crus_todos{i};
    f_calculo = f_crus_todos{i};
    S_atual = S_todos(i);
    caminho_salvar = caminhos_salvamento{i};

    % Criação do Modelo Linear com base 100% nos dados crus
    mdl = fitlm(d_calculo, f_calculo);
    R2_val = mdl.Rsquared.Ordinary;

    % Coeficientes: F = a*d + b
    b_coef = mdl.Coefficients.Estimate(1);
    a_coef = mdl.Coefficients.Estimate(2);

    % Salva as informações necessárias para plotar o gráfico comparativo depois
    coef_a_salvos(i) = a_coef;
    coef_b_salvos(i) = b_coef;
    R2_salvos(i) = R2_val;

    % Extrapolação da linha de tendência forçada entre 10 uN e 1000 uN
    d_min_limite = (F_min_plot - b_coef) / a_coef;
    d_max_limite = (F_max_plot - b_coef) / a_coef;
    d_plot = linspace(d_min_limite, d_max_limite, 100)';

    % Calcula a linha predita e os intervalos de confiança (95%)
    [f_plot, f_ci] = predict(mdl, d_plot, 'Prediction', 'curve');

    fig = figure('Name', sprintf('Gráfico de Calibração - %s', titulos_janela{i}), ...
        'Color', 'w', 'Position', [100 + (i*50), 100 + (i*50), 900, 500]);
    hold on;

    % 1. Região Sombreada (Banda de Confiança)
    X_patch = [d_plot', fliplr(d_plot')];
    Y_patch = [f_ci(:,2)', fliplr(f_ci(:,1)')];
    fill(X_patch, Y_patch, [0.9 0.8 1], 'FaceAlpha', 0.6, 'EdgeColor', [0.8 0 0.8], 'LineWidth', 1);

    % 2. Linha de Tendência Ideal
    plot(d_plot, f_plot, 'k--', 'LineWidth', 1.5);

    % 3. Dispersão dos Dados Crus
    scatter(d_calculo, f_calculo, 40, 'MarkerEdgeColor', 'k', 'MarkerFaceColor', [0.4 0.4 0.4]);

    legend({sprintf('Região de Confiança 95%% (R^2 = %.4f)', R2_val), 'Linha de Tendência Ideal', 'Amostras'}, 'Location', 'best');
    title(sprintf('Curva de Calibração para S = %.4f m/N', S_atual));
    xlabel('Deslocamento (\mum)');
    ylabel('Força F_{eq} (\muN)');

    % Trava o eixo Y para exibir estritamente de 10 a 1000
    ylim([F_min_plot, F_max_plot]);
    grid on;
    hold off;

    % Salvar gráfico
    if ~exist(caminho_salvar, 'dir')
        mkdir(caminho_salvar);
    end
    nome_arquivo = sprintf('curva_calibracao_S_%.4f.png', S_atual);
    caminho_completo = fullfile(caminho_salvar, nome_arquivo);
    saveas(fig, caminho_completo);
    fprintf('Gráfico salvo: %s (R^2 = %.4f)\n', nome_arquivo, R2_val);
end

% === 3. GERAÇÃO DO GRÁFICO COMPARATIVO ===
% Só gera o comparativo se houver pelo menos um conjunto de dados lido
if any(dados_existem)
    fig_comp = figure('Name', 'Comparativo de Sensibilidades', 'Color', 'w', 'Position', [300, 200, 900, 500]);
    hold on;
    estilos_linha = {'-k', ':k', '-.k'};
    legendas_comp = {};

    fprintf('\n--- Equações das Retas de Tendência (Feq = a * d + b) ---\n');
    for i = 1:3
        % Só plota no comparativo as curvas que de fato tiveram dados crus carregados
        if dados_existem(i)
            a_coef = coef_a_salvos(i);
            b_coef = coef_b_salvos(i);
            S_atual = S_todos(i);

            % Força os limites de X baseados nos limites de Y
            d_min_limite = (F_min_plot - b_coef) / a_coef;
            d_max_limite = (F_max_plot - b_coef) / a_coef;

            d_plot = [d_min_limite, d_max_limite];
            f_plot = a_coef * d_plot + b_coef;

            plot(d_plot, f_plot, estilos_linha{i}, 'LineWidth', 1.5);

            legendas_comp{end+1} = sprintf('S = %.4f m/N', S_atual);
            fprintf('S = %.4f m/N -> Feq = %.4f * d %+.4f (R^2 = %.4f)\n', S_atual, a_coef, b_coef, R2_salvos(i));
        end
    end

    legend(legendas_comp, 'Location', 'northwest');
    title('Comparativo das Curvas de Calibração (10 \muN a 1000 \muN)');
    xlabel('Deslocamento (\mum)');
    ylabel('Força F_{eq} (\muN)');

    % Trava o eixo Y do comparativo também
    ylim([F_min_plot, F_max_plot]);
    grid on;
    hold off;

    fprintf('\nRotina finalizada com sucesso.\n');
else
    fprintf('\nNenhum dado cru foi encontrado. O gráfico comparativo não pôde ser gerado.\n');
end
