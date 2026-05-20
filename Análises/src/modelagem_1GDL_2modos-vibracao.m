% ESTE SCRIPT TEM COMO OBJETIVO A MODELAGEM DO SISTEMA DA BALANÇA PENDULAR
% COMO UM SISTEMA DE UM GRAU DE LIBERDADE. O SEGUNDO MODO DE VIBRAÇÃO É
% CONSIDERADO DESACOPLADO AO MODO DE VIBRAÇÃO PRINCIPAL

% Parâmetros do sistema
m = 3;
c = 1;
k = 2;

% Condições iniciais
x0 = 0;
v0 = 0.25;

% Matriz de estado A
A = [ 0 1; -k/m -c/m ];

% Configurações de tempo
d_T = 0.05;         % Passo de tempo
t = 0:d_T:20;       % Vetor de tempo de 0 a 20 s
N = length(t);      % Número de iterações

% Frequência natural e período
omega_n = sqrt(k/m);
T = 2*pi/omega_n;

% Inicialização do vetor de estados (x)
% A linha 1 armazenará x1 (posição) e a linha 2 armazenará x2 (velocidade)
x = zeros(2, N);
x(:, 1) = [x0; v0]; % Aplicando as condições iniciais

% Loop de integração numérica pelo Método de Euler
for i = 1:(N-1)
    % Calcula a derivada no instante atual (x_ponto = A * x)
    x_ponto = A * x(:, i);
    
    % Atualiza o próximo estado
    x(:,i+1) = x(:, i) + d_T * x_ponto;
end

% Extrai apenas a posição x(t), que é a primeira linha da matriz
x_pos = x(1, :);

% Plotagem do resultado
figure;
plot(t, x_pos, 'b', 'LineWidth', 1.5);
grid on;
xlabel('Tempo (s)');
ylabel('Posição x(t)');
title('Resposta do Sistema (Método de Euler)');
