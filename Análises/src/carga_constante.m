clear all; close all; clc;
% =========================================================================
% SCRIPT PRINCIPAL
% =========================================================================

% Importa os dados brutos
% Colunas são separadas por TAB ('\t')
dados_raw = readmatrix('P1_d1_09-04-2026.txt', 'OutputType', 'string', 'Delimiter', '\t');

% Substitui ',' por '.' e converte tudo para números (double)
dados_num = double(strrep(dados_raw, ',', '.'));

% Limpa qualquer linha vazia
dados = rmmissing(dados_num); 

% ---> TRAVA DE SEGURANÇA <---
if isempty(dados)
    error('ERRO: A matriz ficou vazia. O arquivo P1_d1_09-04-2026.txt pode não estar separado por TAB. Tente mudar o "Delimiter" acima para espaço (" ") ou ponto-e-vírgula (";").');
end

t = dados(:, 1); % Vetor de tempo
x = dados(:, 2); % Vetor de deslocamento

% Dados de medição 
m_conhecida = 0.00002; % kg
g_local = 9.784; % m/s^2
l = 0.00552; % m
L = 0.3675; % m

% Bloco de funções
delta_d = deslocamento(t, x);

Feq_Newtons = forca_equivalente(m_conhecida, g_local, l, L);
Feq = Feq_Newtons * 1e6; % Converte a força para micro-Newtons (µN) para bater com a unidade da rigidez

k = rigidez_linear(Feq, delta_d);

% Exibe os resultados finais na tela do MATLAB
fprintf('\n--- RESULTADOS ---\n');
fprintf('Força equivalente calculada: %.5f µN\n', Feq); % Adicionado \n no final
fprintf('Deslocamento Medido (Delta d): %.5f µm\n', delta_d);
fprintf('Rigidez Calculada (k):         %.5f µN/µm\n\n', k);


% =========================================================================
% DEFINIÇÃO DAS FUNÇÕES
% =========================================================================

function [Feq] = forca_equivalente(m_conhecida, g_local, l, L)
    Feq = m_conhecida * g_local * l * (1/L);
end

function [diff_val] = deslocamento(time, d)
    % Parâmetros do filtro e das janelas de tempo
    find_diff = true;
    time1 = [150, 280];
    time2 = [400, 600];
    cutoff_freq = 0.05;
    order = 5;

    % =========================================================================
    % Filtragem (Filtro Butterworth Passa-Baixa)
    % =========================================================================
    N = length(d);
    fs = N / (time(end) - time(1)); % Frequência de amostragem
    
    Wn = cutoff_freq / (fs / 2); % Frequência normalizada de Nyquist
    [b, a] = butter(order, Wn, 'low');
    
    av = filtfilt(b, a, d); % Aplica o filtro

    % =========================================================================
    % Cálculos de Deslocamento e Incerteza
    % =========================================================================
    diff_val = 0; % Variável de segurança
    
    if find_diff
        % --- Janela 1 ---
        [~, startindex1] = min(abs(time - time1(1)));
        [~, endindex1]   = min(abs(time - time1(2)));
        
        d1 = d(startindex1:endindex1);
        av1 = mean(d1);
        std1 = std(av(startindex1:endindex1));
        startime1 = time(startindex1);
        endtime1  = time(endindex1);
        
        % --- Janela 2 ---
        [~, startindex2] = min(abs(time - time2(1)));
        [~, endindex2]   = min(abs(time - time2(2)));
        
        d2 = d(startindex2:endindex2);
        av2 = mean(d2);
        std2 = std(av(startindex2:endindex2));
        startime2 = time(startindex2);
        endtime2  = time(endindex2);
            
        % --- Diferença (Deslocamento) e Propagação do Erro ---
        diff_val = abs(av1 - av2);
        disp_std = sqrt((std1^2) + (std2^2));
    end

    % =========================================================================
    % Plotagem do Gráfico Avançado
    % =========================================================================
    figure('Name', 'Analise de Deslocamento', 'Color', 'w');
    hold on;
    
    % Sinal bruto e Sinal filtrado
    plot(time, d, 'Color', [0.6 0.6 0.6], 'LineWidth', 0.5, 'DisplayName', 'Raw Data');
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
            'DisplayName', sprintf('Deslocamento = %.5f µm (Erro: %.5f µm)', diff_val, disp_std));
    end
    
    xlabel('Tempo (s)');
    ylabel('Deslocamento (\mu m)');
    title('Calibração: 1 Toque Canto Esquerdo');
    grid on;
    legend('Location', 'best');
    hold off;
end

function [k] = rigidez_linear(Feq, delta_d)
    k = Feq / delta_d;
end

