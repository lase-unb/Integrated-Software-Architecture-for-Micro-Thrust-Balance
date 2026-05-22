clear all; close all; clc;
%% ESSE SCRIPT ANALISA O COMPORTAMENTO DE UMA AMOSTRA INDIVIDUALMENTE
% =========================================================================
% SCRIPT PRINCIPAL
% =========================================================================

% 1. Importa os dados brutos
pasta_dados = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\data\carga_constante';
nome_arquivo = 'P1_d3_2.txt';
caminho_completo = fullfile(pasta_dados, nome_arquivo);

dados_raw = readmatrix(caminho_completo, 'OutputType', 'string', 'Delimiter', '\t');
dados_num = double(strrep(dados_raw, ',', '.'));
dados = rmmissing(dados_num); 

if isempty(dados)
    error('ERRO: A matriz ficou vazia. Verifique o delimitador do arquivo txt.');
end

t = dados(:, 1); % Vetor de tempo
x = dados(:, 2); % Vetor de deslocamento

% 2. Dados de medição 
m_conhecida = 0.00002; % Massa conhecida [kg]
g_local = 9.784;       % Aceleração da gravidade local [m/s^2]
l = 0.01552;           % Distância do pivô até o ponto de aplicação da massa conhecida [m]
L = 0.368;             % Comprimento do braço do pêndulo [m]

% 3. Cálculos principais
% Agora a função 'deslocamento' retorna também a razão de amortecimento (zeta)
[delta_d, zeta] = deslocamento(t, x, nome_arquivo);

Feq_Newtons = forca_equivalente(m_conhecida, g_local, l, L);
Feq = Feq_Newtons * 1e6; % Converte para µN

% Função de rigidez
k = rigidez_linear(Feq, delta_d);

% 4. Exibe os resultados finais no Command Window
fprintf('\n--- RESULTADOS ---\n');
fprintf('Força equivalente calculada: %.5f µN\n', Feq); 
fprintf('Deslocamento Medido (Delta d): %.5f µm\n', delta_d);
fprintf('Rigidez Calculada (k):         %.5f µN/µm\n', k);
if ~isnan(zeta)
    fprintf('Razão de Amortecimento (zeta): %.5f\n\n', zeta);
else
    fprintf('Razão de Amortecimento (zeta): Não foi possível calcular (picos insuficientes)\n\n');
end

% =========================================================================
% BLOCO RESULTADOS NO GRÁFICO
% =========================================================================
if ~isnan(zeta)
    str_resultados = sprintf('--- RESULTADOS ---\nForça Eq.: %.5f \\muN\n\\Delta d: %.5f \\mum\nRigidez (k): %.5f \\muN/\\mum\nAmortecimento (\\zeta): %.5f', Feq, delta_d, k, zeta);
else
    str_resultados = sprintf('--- RESULTADOS ---\nForça Eq.: %.5f \\muN\n\\Delta d: %.5f \\mum\nRigidez (k): %.5f \\muN/\\mum\nAmortecimento (\\zeta): N/A', Feq, delta_d, k);
end

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
folder = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante'; 
[~, nome_base, ~] = fileparts(nome_arquivo);
filename = [nome_base, '.png'];
fullPath = fullfile(folder, filename);
exportgraphics(gcf, fullPath, 'Resolution', 300); 
fprintf('Gráfico salvo com sucesso em:\n%s\n', fullPath);

% =========================================================================
% DEFINIÇÃO DAS FUNÇÕES
% =========================================================================
function [Feq] = forca_equivalente(m_conhecida, g_local, l, L)
    Feq = m_conhecida * g_local * l * (1/L);
end

function [diff_val, zeta] = deslocamento(time, d, titulo_grafico)
    % Parâmetros do filtro e das janelas de tempo
    find_diff = true;
    time1 = [30, 100];
    time2 = [150, 230];
    time_transiente = [102, 140]; % <-- NOVO: Janela onde ocorre a oscilação livre
    
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
    % Cálculos de Deslocamento, Incerteza e Amortecimento
    % =========================================================================
    diff_val = 0; 
    zeta = NaN;
    
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
        
        % =================================================================
        % CÁLCULO DO AMORTECIMENTO (Método do Decremento Logarítmico)
        % =================================================================
        [~, start_t] = min(abs(time - time_transiente(1)));
        [~, end_t]   = min(abs(time - time_transiente(2)));
        
        t_osc = time(start_t:end_t);
        d_osc = d(start_t:end_t); % Usamos dados raw para não perder amplitude no filtro
        
        % Define a proeminência mínima para ignorar ruídos (metade do desvio padrão)
        prominence_thresh = std(d_osc) * 0.5; 
        
        % Encontra os picos (depende se o degrau foi para cima ou para baixo)
        if av2 > av1
            [pks, locs_idx] = findpeaks(d_osc, 'MinPeakProminence', prominence_thresh);
        else
            [pks_inv, locs_idx] = findpeaks(-d_osc, 'MinPeakProminence', prominence_thresh);
            pks = -pks_inv;
        end
        
        t_pks = t_osc(locs_idx);
        
        % Calcula as amplitudes em relação à nova posição de equilíbrio (av2)
        Amplitudes = abs(pks - av2);
        
        if length(Amplitudes) >= 2
            % Decremento Logarítmico
            A1 = Amplitudes(1);
            An = Amplitudes(end);
            n = length(Amplitudes); % Número de picos
            
            delta = (1 / (n - 1)) * log(A1 / An);
            zeta = delta / sqrt(4 * pi^2 + delta^2);
        end
    end
    
    % =========================================================================
    % Plotagem do Gráfico Avançado
    % =========================================================================
    figure('Name', 'Analise de Deslocamento', 'Color', 'w', 'Position', [100, 100, 900, 500]);
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
            'DisplayName', sprintf('Deslocamento = %.5f µm', diff_val));
            
        % Plot dos picos encontrados para o amortecimento
        if length(Amplitudes) >= 2
            plot(t_pks, pks, 'ro', 'MarkerSize', 6, 'LineWidth', 1.5, ...
                'DisplayName', 'Picos de Oscilação (\zeta)');
        end
    end
    
    xlabel('Tempo (s)');
    ylabel('Deslocamento (\mu m)');
    
    title(titulo_grafico, 'Interpreter', 'none'); 
    
    grid on;
    legend('Location', 'best');
    hold off;
end

function [k] = rigidez_linear(Feq, delta_d)
    k = Feq / delta_d;
end
