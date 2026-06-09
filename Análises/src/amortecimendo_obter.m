% =========================================================================
% Extração de Parâmetros Dinâmicos (Amortecimento e Frequência Natural)
% =========================================================================
clear; clc; close all;

%% 1. Importação dos Dados
% Lê o arquivo txt informando que o separador decimal é a vírgula ','
nome_arquivo = "C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\data\carga_constante\P1_d1_2.txt";
try
    dados = readmatrix(nome_arquivo, 'DecimalSeparator', ',');
catch
    error('Não foi possível ler o arquivo. Verifique o nome e o diretório.');
end

t = dados(:, 1); % Primeira coluna: Tempo (s)
x = dados(:, 2); % Segunda coluna: Deslocamento (mm)

% Remove qualquer offset estático (traz o repouso para o zero)
x = x - mean(x); 

%% 2. Processamento do Sinal e Detecção de Picos
% Encontra os picos (máximos locais) da oscilação
% 'MinPeakProminence' evita que pequenos ruídos sejam detectados como picos
limiar_ruido = max(x) * 0.1; 
[pks, locs] = findpeaks(x, t, 'MinPeakProminence', limiar_ruido);

% Verifica se há picos suficientes para a análise
if length(pks) < 3
    error('O sinal não possui ciclos de oscilação suficientes para análise.');
end

%% 3. Cálculo da Frequência Natural Amortecida (wd)
% O período amortecido (Td) é a média da distância temporal entre os picos
T_d = mean(diff(locs));
f_d = 1 / T_d;          % Frequência em Hz
w_d = 2 * pi * f_d;     % Frequência em rad/s

%% 4. Cálculo do Fator de Amortecimento (zeta) e Frequência Natural (wn)
% Utiliza o decremento logarítmico através do ajuste da envoltória exponencial.
% A equação da envoltória é: X(t) = X0 * exp(-zeta * wn * t)
% Aplicando ln: ln(X) = (-zeta * wn) * t + ln(X0)
% Isso é a equação de uma reta (y = m*x + b), onde a inclinação m = -zeta * wn.

% Ajuste linear (polinômio de grau 1) entre o tempo dos picos e o ln(picos)
coeficientes = polyfit(locs, log(pks), 1);
m = coeficientes(1); % Inclinação da reta

% Resolução do sistema:
% 1) m = -zeta * wn  --> wn = abs(m) / zeta
% 2) w_d = wn * sqrt(1 - zeta^2)
% Substituindo 1 em 2, obtemos de forma direta:
w_n = sqrt(m^2 + w_d^2);
zeta = abs(m) / w_n;

%% 5. Exibição dos Resultados no Console
fprintf('=== Resultados da Identificação Dinâmica ===\n');
fprintf('Período Amortecido (Td):      %.4f s\n', T_d);
fprintf('Frequência Amortecida (fd):   %.4f Hz\n', f_d);
fprintf('Frequência Natural (wn):      %.4f rad/s (%.4f Hz)\n', w_n, w_n/(2*pi));
fprintf('Fator de Amortecimento (Zeta): %.5f\n', zeta);
fprintf('============================================\n');

%% 6. Plotagem Visual da Validação
figure('Name', 'Identificação de Parâmetros', 'Color', 'w');
hold on; grid on;

% Plota o sinal original
plot(t, x, 'b', 'LineWidth', 1, 'DisplayName', 'Sinal Original');

% Plota os picos detectados
plot(locs, pks, 'ro', 'MarkerFaceColor', 'r', 'DisplayName', 'Picos Detectados');

% Reconstrói e plota a envoltória exponencial estimada
envoltoria = exp(coeficientes(2)) * exp(m * t);
plot(t, envoltoria, 'k--', 'LineWidth', 1.5, 'DisplayName', 'Envoltória Estimada');

title('Decaimento Logarítmico - Oscilação Livre');
xlabel('Tempo (s)');
ylabel('Deslocamento (mm)');
legend('Location', 'northeast');
xlim([min(t) max(t)]);
hold off;
