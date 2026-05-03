clear all; clc;

% 1. Importa os dados brutos
% Define o caminho da pasta onde estão os dados
pasta_dados = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\data\carga_constante';

% Define o nome do arquivo
nome_arquivo = 'P4_d1_1.txt';

%  Cria o caminho completo
caminho_completo = fullfile(pasta_dados, nome_arquivo);

% Importa os dados brutos usando o caminho completo
dados_raw = readmatrix(caminho_completo, 'OutputType', 'string', 'Delimiter', '\t');

% Substitui ',' por '.' e converte tudo para números (double)
dados_num = double(strrep(dados_raw, ',', '.'));

% Limpa qualquer linha vazia
dados = rmmissing(dados_num); 

% Interrompe o script caso haja problema com a matriz de input
if isempty(dados)
    error('ERRO: A matriz ficou vazia. O arquivo P1_d1_09-04-2026.txt pode não estar separado por TAB. Tente mudar o "Delimiter" acima para espaço (" ") ou ponto-e-vírgula (";").');
end

t = dados(:, 1); % Vetor de tempo
x = dados(:, 2); % Vetor de deslocamento

plot(t,x);
grid on;
