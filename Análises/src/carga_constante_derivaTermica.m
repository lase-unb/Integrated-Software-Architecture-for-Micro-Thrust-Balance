clear all; close all; clc;

% =========================================================================
% SCRIPT PRINCIPAL
% =========================================================================

% 1. Importa os dados brutos
% Define o caminho da pasta onde estão os dados
pasta_dados = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\data\deriva_termica';

% Define o nome do arquivo
nome_arquivo = 'deriva_peso4_28-04';

% Une a pasta e o arquivo de forma segura (cria o caminho completo)
caminho_completo = fullfile(pasta_dados, nome_arquivo);

% Importa os dados brutos usando o caminho completo
dados_raw = readmatrix(caminho_completo, 'OutputType', 'string', 'Delimiter', '\t');

% Substitui ',' por '.' e converte tudo para números (double)
dados_num = double(strrep(dados_raw, ',', '.'));

% Limpa qualquer linha vazia
dados = rmmissing(dados_num); 

% ---> TRAVA DE SEGURANÇA <---
if isempty(dados)
    error('ERRO: A matriz ficou vazia. O arquivo pode não estar separado por TAB. Tente mudar o "Delimiter".');
end

t = dados(:, 1); % Vetor de tempo
x = dados(:, 2); % Vetor de deslocamento

% 2. Dados de medição 
m_conhecida = 0.00002; % Massa conhecida [kg]
g_local = 9.784;       % Aceleração da gravidade local [m/s^2]
l = 0.00552;           % Distância do pivô até o ponto de aplicação da massa conhecida [m]
L = 0.3675;            % Comprimento do braço do pêndulo [m]

% 3. Cálculos principais
% Agora recebemos o delta_d e a incerteza do deslocamento (erro_d)
[delta_d, erro_d] = deslocamento(t, x, nome_arquivo);
Feq_Newtons = forca_equivalente(m_conhecida, g_local, l, L);

% Converte a força para micro-Newtons (µN) para bater com a unidade da rigidez
Feq = Feq_Newtons * 1e6; 

% Função de rigidez
k = rigidez_torsional(Feq, delta_d);

% ---> CALCULO DA INCERTEZA DA RIGIDEZ <---
% Assumindo que a incerteza dominante é o ruído dinâmico do deslocamento
erro_k = k * (erro_d / delta_d);

% 4. Exibe os resultados finais no Command Window
fprintf('\n--- RESULTADOS COM CORREÇÃO DE DERIVA ---\n');
fprintf('Força equivalente calculada: %.5f µN\n', Feq); 
fprintf('Deslocamento Medido (Delta d): %.5f ± %.5f µm\n', delta_d, erro_d);
fprintf('Rigidez Calculada (k):         %.5f ± %.5f µN/µm\n\n', k, erro_k);

% =========================================================================
% BLOCO RESULTADOS NO GRÁFICO
% =========================================================================
% O símbolo \pm gera o '±' no gráfico
str_resultados = sprintf('--- RESULTADOS ---\nForça Eq.: %.5f \\muN\n\\Delta d: %.5f \\pm %.5f \\mum\nRigidez (k): %.2f \\pm %.2f \\muN/\\mum', Feq, delta_d, erro_d, k, erro_k);

caixa = annotation('textbox', [0.65, 0.15, 0.25, 0.15], ...
    'String', str_resultados, ...
    'FitBoxToText', 'on', ...           
    'BackgroundColor', [1 1 1 0.9], ... 
    'EdgeColor', 'k', ...               
    'FontSize', 10, ...
    'FontWeight', 'bold');
caixa.ButtonDownFcn = 'selectobject';

% =========================================================================
% SALVAMENTO DA FIGURA
% =========================================================================
% Define the folder
folder = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante'; 

% Separa o nome do arquivo da extensão '.txt' e adiciona '.png'
[~, nome_base, ~] = fileparts(nome_arquivo);
filename = [nome_base, '.png'];

% Create the full path
fullPath = fullfile(folder, filename);

% Save the current figure (gcf) to that path
%exportgraphics(gcf, fullPath, 'Resolution', 300); 

% Imprime mensagem de confirmação de salvamento
%fprintf('Gráfico salvo com sucesso em:\n%s\n', fullPath);


% =========================================================================
% DEFINIÇÃO DAS FUNÇÕES
% =========================================================================

function [Feq] = forca_equivalente(m_conhecida, g_local, l, L)
    Feq = m_conhecida * g_local * l * (1/L);
end

function [diff_val, disp_std] = deslocamento(time, d, titulo_grafico)
    % Parâmetros do filtro e das janelas de tempo
    find_diff = true;
    time1 = [30, 100];
    time2 = [150, 230];
    cutoff_freq = 0.05;
    order = 5;

    % =========================================================================
    % 1. CORREÇÃO DE DERIVA TÉRMICA (DETRENDING)
    % =========================================================================
    % Isolamos a Janela 1 para descobrir a inclinação do sensor no repouso
    [~, start_baseline] = min(abs(time - time1(1)));
    [~, end_baseline]   = min(abs(time - time1(2)));
    
    tempo_baseline = time(start_baseline:end_baseline);
    disp_baseline  = d(start_baseline:end_baseline);
    
    % Calcula a reta de deriva (polinômio de grau 1: y = a*x + b)
    coefs_deriva = polyfit(tempo_baseline, disp_baseline, 1);
    
    % Projeta essa reta para todo o ensaio e subtrai do sinal original
    reta_deriva = polyval(coefs_deriva, time);
    d_corrigido = d - reta_deriva;
    
    % Zera a linha de base para facilitar a leitura no gráfico
    offset_zero = mean(d_corrigido(start_baseline:end_baseline));
    d_corrigido = d_corrigido - offset_zero;

    % =========================================================================
    % 2. Filtragem (Filtro Butterworth Passa-Baixa)
    % =========================================================================
    N = length(d_corrigido);
    fs = N / (time(end) - time(1)); % Frequência de amostragem
    
    Wn = cutoff_freq / (fs / 2); % Frequência normalizada de Nyquist
    [b, a] = butter(order, Wn, 'low');
    
    av = filtfilt(b, a, d_corrigido); % Aplica o filtro no sinal já sem deriva

    % =========================================================================
    % 3. Cálculos de Deslocamento e Incerteza
    % =========================================================================
    diff_val = 0; 
    disp_std = 0;
    
    if find_diff
        % --- Janela 1 ---
        [~, startindex1] = min(abs(time - time1(1)));
        [~, endindex1]   = min(abs(time - time1(2)));
        
        d1 = d_corrigido(startindex1:endindex1);
        av1 = mean(d1);
        std1 = std(av(startindex1:endindex1));
        startime1 = time(startindex1);
        endtime1  = time(endindex1);
        
        % --- Janela 2 ---
        [~, startindex2] = min(abs(time - time2(1)));
        [~, endindex2]   = min(abs(time - time2(2)));
        
        d2 = d_corrigido(startindex2:endindex2);
        av2 = mean(d2);
        std2 = std(av(startindex2:endindex2));
        startime2 = time(startindex2);
        endtime2  = time(endindex2);
            
        % --- Diferença (Deslocamento) e Propagação do Erro ---
        diff_val = abs(av1 - av2);
        disp_std = sqrt((std1^2) + (std2^2));
    end

    % =========================================================================
    % 4. Plotagem do Gráfico Avançado
    % =========================================================================
    figure('Name', 'Analise de Deslocamento', 'Color', 'w', 'Position', [100, 100, 900, 500]);
    hold on;
    
    % Sinal bruto corrigido e Sinal filtrado
    plot(time, d_corrigido, 'Color', [0.6 0.6 0.6], 'LineWidth', 0.5, 'DisplayName', 'Raw Data (S/ Deriva)');
    plot(time, av, 'b-', 'LineWidth', 1.5, ...
        'DisplayName', sprintf('Filtro Butterworth: order=%d, cutoff=%.2fHz', order, cutoff_freq));
    
    if find_diff
        % Plot Janela 1
        plot([startime1, endtime1], [av1, av1], 'k--', 'LineWidth', 1.5, ...
            'DisplayName', sprintf('Média (%ds a %ds) = %.5f µm', time1(1), time1(2), av1));
        plot([startime1, endtime1], [av1+std1, av1+std1], 'r--', ...
            'DisplayName', sprintf('Desvio Padrão 1 = %.5f µm', std1));
        plot([startime1, endtime1], [av1-std1, av1-std1], 'r--', 'HandleVisibility', 'off');
        
        % Plot Janela 2
        plot([startime2, endtime2], [av2, av2], 'k--', 'LineWidth', 1.5, ...
            'DisplayName', sprintf('Média (%ds a %ds) = %.5f µm', time2(1), time2(2), av2));
        plot([startime2, endtime2], [av2+std2, av2+std2], 'r--', ...
            'DisplayName', sprintf('Desvio Padrão 2 = %.5f µm', std2));
        plot([startime2, endtime2], [av2-std2, av2-std2], 'r--', 'HandleVisibility', 'off');
        
        % Linha de Deslocamento Total
        plot([time(end), time(end)], [av1, av2], 'g', 'LineWidth', 5.0, ...
            'DisplayName', sprintf('Deslocamento = %.5f \\pm %.5f µm', diff_val, disp_std));
    end
    
    xlabel('Tempo (s)');
    ylabel('Deslocamento (\mu m)');
    
    title(titulo_grafico, 'Interpreter', 'none'); 
    
    grid on;
    legend('Location', 'best');
    hold off;
end

function [k] = rigidez_torsional(Feq, delta_d)
    k = Feq / delta_d;
end
