clear all; clc;

g = 9.784; % Gravidade local. Coordenadas: (-15.999557, -48.046830).
m_p = 0.75935;  % [kg] (massa do propulsor + base ( kg)) PESAR NO LAB
y_p = -(0.368);  % [m] (distância do propulsor até o pivô. Manter negativo, pois a coordenada está localizada abaixo do pivô.)

m_c = 0;   % [kg] (massa do contra-peso)
y_c = 0;   % [m] (distância do contra-peso até o pivô)

m_b = 0.16133*2; % [kg] (massa do braço. Como é simétrico, considerou-se como apenas um braço) PESAR NO LAB

% ---- Chamada das funções
cg_y = calcular_cg_1d(m_p, y_p, m_c, y_c, m_b);
S = calcular_sensibilidade(y_p, m_p, m_c, g, cg_y);

% ---- Exibição dos resultados
% Definição do diretório e arquivo
pasta_saida = 'C:\Users\thami\OneDrive - unb.br\FGA\Balança de Microempuxo - LaSE\Integrated-Software-Architecture-for-Micro-Thrust-Balance\Análises\resultados\carga_constante\sensibilidade intermediaria';
nome_arquivo = 'resultados_intermediaria_sensibilidade.txt';
caminho_completo = fullfile(pasta_saida, nome_arquivo);

% Garante que a pasta exista
if ~exist(pasta_saida, 'dir')
    mkdir(pasta_saida);
end

% 1. Abre o arquivo no caminho completo para escrita ('w')
fid = fopen(caminho_completo, 'w');

% 2. Salva os resultados numéricos
fprintf(fid, 'Posição do Centro de Gravidade (Y): %.4f m (pivô como referencial)\n', cg_y);
fprintf(fid, 'Sensibilidade: %.4f m/N\n', S);

% 3. Salva as mensagens lógicas
if m_p > 5
    fprintf(fid, 'A balança suporta um propulsor de até 2 kg. Não prosseguir.\n');
end

if cg_y < 0
    fprintf(fid, 'O CG está abaixo do pivô (Equilíbrio Estável).\n');
elseif cg_y > 0
    fprintf(fid, 'O CG está acima do pivô (Equilíbrio Instável). Reduza a massa do contra-peso.\n');
else
    fprintf(fid, 'O CG está exatamente no pivô (Equilíbrio Indiferente). Garanta que o contra-peso tenha massa inferior à do propulsor.\n');
end

% 4. Fecha o arquivo
fclose(fid);

fprintf('Arquivo salvo com sucesso em: %s\n-------\n', caminho_completo);

% ---- print dos resultados
fprintf('Posição do Centro de Gravidade (Y): %.4f m (pivô como referencial)\n', cg_y);
fprintf('Sensibilidade: %.4f m/N\n', S);

% 3. Salva as mensagens lógicas
if m_p > 5
    fprintf('A balança suporta um propulsor de até 2 kg. Não prosseguir.\n');
end

if cg_y < 0
    fprintf('O CG está abaixo do pivô (Equilíbrio Estável).\n');
elseif cg_y > 0
    fprintf('O CG está acima do pivô (Equilíbrio Instável). Reduza a massa do contra-peso.\n');
else
    fprintf('O CG está exatamente no pivô (Equilíbrio Indiferente). Garanta que o contra-peso tenha massa inferior à do propulsor.\n');
end

% --- FUNÇÕES ---
function cg_y = calcular_cg_1d(m_peso, y_peso, m_contra, y_contra, m_braco)
    % Calcula o centro de gravidade vertical.
    
    % Assume braço uniforme entre o peso e o contrapeso
    y_braco = (y_peso + y_contra) / 2.0;
    
    momento_total = (m_peso * y_peso) + (m_contra * y_contra) + (m_braco * y_braco);
    massa_total = m_peso + m_contra + m_braco;
    
    if massa_total == 0
        error('A massa total do sistema não pode ser zero.');
    end
    
    cg_y = momento_total / massa_total;
end

function S = calcular_sensibilidade(LT, MT, MCP, g, cg)
    S = LT^2/((MT+MCP)*g*abs(cg));
end
