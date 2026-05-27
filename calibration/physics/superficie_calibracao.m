clear all; clc;

% 1. KNOWN INPUT DATA
% CG Positions [m]
CG_inter = -0.3131; 
CG_menor = -0.3369; 
CG_maior = -0.0672; 

% Corresponding Sensitivities [m/N]
S = 0.0582; 
S_menor = 0.0179; 
S_maior = 0.0939; 

% Displacement and Force vectors for each case
d_inter = [1.8039, 3.9369, 5.8372, 9.7834];
f_inter = [167.1960, 324.3694, 486.3337, 808.3664];

d_menor = [1.4982, 4.3618];
f_menor = [167.1960, 618.1822];

d_maior = [3.3523, 6.7382, 9.5474, 14.2316];
f_maior = [167.1960, 418.8246, 618.1822, 918.3950];

% 2. EXTRACTION OF REAL CURVE COEFFICIENTS (F = a*d + b)
p_inter = polyfit(d_inter, f_inter, 1);
p_menor = polyfit(d_menor, f_menor, 1);
p_maior = polyfit(d_maior, f_maior, 1);

% --- R^2 CALCULATION BLOCK ---
% Intermediate Sensitivity
y_fit_inter = polyval(p_inter, d_inter);
SQ_res_inter = sum((f_inter - y_fit_inter).^2);
SQ_tot_inter = (length(f_inter)-1) * var(f_inter);
R2_inter = 1 - (SQ_res_inter / SQ_tot_inter);

% Lower Sensitivity
y_fit_menor = polyval(p_menor, d_menor);
SQ_res_menor = sum((f_menor - y_fit_menor).^2);
SQ_tot_menor = (length(f_menor)-1) * var(f_menor);
R2_menor = 1 - (SQ_res_menor / SQ_tot_menor);

% Higher Sensitivity
y_fit_maior = polyval(p_maior, d_maior);
SQ_res_maior = sum((f_maior - y_fit_maior).^2);
SQ_tot_maior = (length(f_maior)-1) * var(f_maior);
R2_maior = 1 - (SQ_res_maior / SQ_tot_maior);

% Print R^2 results to the Command Window
fprintf('--- R^2 Coefficients ---\n');
fprintf('S = %.4f m/N (Lower CG) -> R^2 = %.4f\n', S_menor, R2_menor);
fprintf('S = %.4f m/N (Inter CG) -> R^2 = %.4f\n', S, R2_inter);
fprintf('S = %.4f m/N (Higher CG) -> R^2 = %.4f\n\n', S_maior, R2_maior);
% -----------------------------

% Grouping data in the same order (Lower CG, Intermediate, Higher CG)
CG_conhecidos = [CG_menor, CG_inter, CG_maior];
S_conhecidos = [S_menor, S, S_maior]; % Auxiliary vector for text labels
a_conhecidos = [p_menor(1), p_inter(1), p_maior(1)];
b_conhecidos = [p_menor(2), p_inter(2), p_maior(2)];

% 3. MATHEMATICAL MODELING (CALIBRATION SURFACE)
poly_a = polyfit(CG_conhecidos, a_conhecidos, 2);
poly_b = polyfit(CG_conhecidos, b_conhecidos, 2);

% 4. PREDICTION TEST FOR A NEW CG (Simulation)
CG_alvo = -0.2000; % [m] -> Example of an unmeasured CG

% Estimating the new line
a_estimado = polyval(poly_a, CG_alvo);
b_estimado = polyval(poly_b, CG_alvo);

fprintf('--- Predictive Model for CG = %.4f m ---\n', CG_alvo);
fprintf('Estimated Angular Coefficient (a): %.4f\n', a_estimado);
fprintf('Estimated Linear Coefficient (b): %.4f\n', b_estimado);
fprintf('New line equation: Feq = %.4f * d %+.4f\n\n', a_estimado, b_estimado);

% 5. PLOTTING RESULTS 
% Figure 1: Coefficient Behavior vs CG Position
figure('Name', 'Calibration Parameters vs CG Position', 'Color', 'w', 'Position', [100, 100, 800, 400]);

% Plot of Angular Coefficient 'a' (Stiffness)
subplot(1, 2, 1);
CG_plot = linspace(min(CG_conhecidos), max(CG_conhecidos), 100);
a_plot = polyval(poly_a, CG_plot);
plot(CG_plot, a_plot, '-k', 'LineWidth', 1); hold on;
scatter(CG_conhecidos, a_conhecidos, 40, 'k', 'filled'); % Measured points

% Adding sensitivity labels to measured points (Stiffness)
for i = 1:length(CG_conhecidos)
    text(CG_conhecidos(i), a_conhecidos(i), sprintf('  S = %.4f m/N', S_conhecidos(i)), ...
        'VerticalAlignment', 'middle', 'HorizontalAlignment', 'left', 'FontSize', 13);
end

%scatter(CG_alvo, a_estimado, 40, 'b*', 'LineWidth', 1.5); % Estimated point
title('Stiffness Behavior (a)', 'Fontsize', 13);
xlabel('CG Position (m)');
ylabel('Angular Coef. (a)');
%legend('Predictive Model', 'Real Data', 'Estimated New', 'Location', 'best', 'FontSize', 13);
legend('Predictive Model', 'Real Data', 'Location', 'best', 'FontSize', 13);
grid on;

% Plot of Linear Coefficient 'b' (Offset)
subplot(1, 2, 2);
b_plot = polyval(poly_b, CG_plot);
plot(CG_plot, b_plot, '-k', 'LineWidth', 1); hold on;
scatter(CG_conhecidos, b_conhecidos, 40, 'k', 'filled'); 

% Adding sensitivity labels to measured points (Offset)
for i = 1:length(CG_conhecidos)
    text(CG_conhecidos(i), b_conhecidos(i), sprintf('  S = %.4f m/N', S_conhecidos(i)), ...
        'VerticalAlignment', 'middle', 'HorizontalAlignment', 'left', 'FontSize', 13);
end

%scatter(CG_alvo, b_estimado, 40, 'b*', 'LineWidth', 1.5); 
title('Offset Behavior (b)', 'Fontsize', 13);
xlabel('CG Position (m)');
ylabel('Linear Coef. (b)');
grid on;

% Figure 2: Estimated Calibration Curve vs Reals
figure('Name', 'Estimated Calibration Curve', 'Color', 'w', 'Position', [950, 100, 600, 500]);
hold on;

% Plotting the 3 real lines
d_plot_real = linspace(0, 15, 50);
plot(d_plot_real, polyval(p_menor, d_plot_real), '-k', 'LineWidth', 2);
plot(d_plot_real, polyval(p_inter, d_plot_real), '-k', 'LineWidth', 2);
plot(d_plot_real, polyval(p_maior, d_plot_real), '-k', 'LineWidth', 2);

% Figure 2 Labels
x_pos_menor = 4;
y_pos_menor = polyval(p_menor, x_pos_menor);
%text(x_pos_menor, y_pos_menor + 40, 'S = 0.0179 m/N', 'FontSize', 13, 'HorizontalAlignment', 'center');

x_pos_inter = 8.5;
y_pos_inter = polyval(p_inter, x_pos_inter);
%text(x_pos_inter, y_pos_inter + 40, 'S = 0.0582 m/N', 'FontSize', 13, 'HorizontalAlignment', 'center');

x_pos_maior = 12.5;
y_pos_maior = polyval(p_maior, x_pos_maior);
%text(x_pos_maior, y_pos_maior + 40, 'S = 0.0939 m/N', 'FontSize', 13, 'HorizontalAlignment', 'center');

% Plotting the new estimated line
d_plot_estimado = linspace(0, 15, 50);
f_estimada = polyval([a_estimado, b_estimado], d_plot_estimado);
%plot(d_plot_estimado, f_estimada, '-b', 'LineWidth', 2);
%title(sprintf('Calibration Prediction for CG = %.4f m', CG_alvo));

title('Calibration Curves for Different Sensitivities', 'FontSize', 20);
xlabel('Displacement (\mum)');
ylabel('Force F_{eq} (\muN)');
%legend('Measured Real Cases', '', '', 'Estimated Curve (New)', 'Location', 'northwest', 'FontSize', 13);
legend('Measured Real Cases', '', '', 'Location', 'northwest', 'FontSize', 20);
grid on;
ylim([0 1000]); 
hold off;
