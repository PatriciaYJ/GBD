#Figure 2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def manual_linregress(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    n = len(x)
    
    if n < 2:
        return 0, 0, 0, 1.0, 0
    
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    
    if denominator == 0:
        return 0, y_mean, 0, 1.0, 0
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)
    
    if ss_tot == 0:
        r_squared = 1.0
    else:
        r_squared = max(0, 1 - (ss_res / ss_tot))
    
    r_value = np.sqrt(r_squared) if slope >= 0 else -np.sqrt(r_squared)
    
    if n > 2:
        mse = ss_res / (n - 2)
        var_slope = mse / denominator if denominator > 0 else 0
        std_err = np.sqrt(var_slope) if var_slope > 0 else 0
    else:
        std_err = 0
    
    if std_err > 0:
        t_stat = abs(slope / std_err)
        if t_stat > 2.58:
            p_value = 0.01
        elif t_stat > 1.96:
            p_value = 0.05
        else:
            p_value = 0.1
    else:
        p_value = 1.0
    
    return slope, intercept, r_value, p_value, std_err

def calculate_aapc(df, measure, diseases):
    aapc_results = []
    for cause in diseases:
        subset = df[(df['cause'] == cause) & (df['measure'] == measure)]
        if not subset.empty:
            years = subset['year']
            values = subset['val']
            slope, intercept, r_value, p_value, std_err = manual_linregress(years, np.log(values))
            aapc = (np.exp(slope) - 1) * 100
            ci_low = (np.exp(slope - 1.96 * std_err) - 1) * 100
            ci_high = (np.exp(slope + 1.96 * std_err) - 1) * 100
            significance = '*' if p_value < 0.05 else ''
            p_value_text = 'p < 0.05' if p_value < 0.05 else f'p = {p_value:.2f}'
            aapc_results.append((cause, aapc, ci_low, ci_high, significance, p_value_text))
    return aapc_results

def run_figure2(file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    data = pd.read_csv(file_path)
    
    diseases = ["Attention-deficit/hyperactivity disorder", "Autism spectrum disorders", 
                "Epilepsy", "Hearing loss", "Intellectual disability", "Vision loss"]
    labels = ["ADHD", "ASD", "Epilepsy", "Hearing Loss", "Intellectual disability", "Vision Loss"]
    
    disease_label_map = dict(zip(diseases, labels))
    
    filtered_data = data[
        (data['cause'].isin(diseases)) &
        (data['location'] == 'Global') &
        (data['sex'] == 'Both') &
        (data['age'].str.contains('<20')) &
        (data['metric'] == 'Rate') &
        (data['year'].between(1990, 2021))
    ].copy()
    
    prevalence_aapc = calculate_aapc(filtered_data, 'Prevalence', diseases)
    dalys_aapc = calculate_aapc(filtered_data, 'DALYs', diseases)
    prevalence_df = pd.DataFrame(prevalence_aapc, columns=['cause', 'aapc_prevalence', 'ci_low_prevalence', 'ci_high_prevalence', 'significance_prevalence', 'p_value_prevalence'])
    dalys_df = pd.DataFrame(dalys_aapc, columns=['cause', 'aapc_dalys', 'ci_low_dalys', 'ci_high_dalys', 'significance_dalys', 'p_value_dalys'])
    
    merged_df = prevalence_df.merge(dalys_df, on='cause')
    merged_df = merged_df.sort_values(by='aapc_prevalence', ascending=False)
    
    merged_df.to_csv(os.path.join(output_dir, 'Figure2_AAPC_Results.csv'), index=False)
    
    colors_prevalence = '#E56F5E'
    colors_dalys = '#FAC795'
    
    cause_labels = [disease_label_map.get(cause, cause) for cause in merged_df['cause']]
    y = np.arange(len(cause_labels))
    height = 0.3
    fig, ax = plt.subplots(figsize=(24, 8))
    
    bars1 = ax.barh(y + height/2, merged_df['aapc_prevalence'], height,
            label='AAPC of Prevalence', color=colors_prevalence)
    
    bars2 = ax.barh(y - height/2, merged_df['aapc_dalys'], height,
            label='AAPC of DALYs', color=colors_dalys)
    
    for i, row in merged_df.iterrows():
        idx = merged_df.index.get_loc(i)
        
        ax.errorbar(row['aapc_prevalence'], y[idx] + height/2, 
                    xerr=[[row['aapc_prevalence'] - row['ci_low_prevalence']], 
                          [row['ci_high_prevalence'] - row['aapc_prevalence']]],
                    fmt='none', ecolor=colors_prevalence, elinewidth=1.5, capsize=3, capthick=1.5)
        
        ax.errorbar(row['aapc_dalys'], y[idx] - height/2, 
                    xerr=[[row['aapc_dalys'] - row['ci_low_dalys']], 
                          [row['ci_high_dalys'] - row['aapc_dalys']]],
                    fmt='none', ecolor=colors_dalys, elinewidth=1.5, capsize=3, capthick=1.5)
    
    x_min, x_max = -1.0, 1.0
    x_ticks = np.arange(x_min, x_max + 0.25, 0.25)
    ax.set_xlim(x_min, x_max)
    ax.set_xticks(x_ticks)
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    text_x = x_max - 0.15
    
    for bar, row in zip(bars1, merged_df.itertuples()):
        ax.text(text_x, bar.get_y() + bar.get_height()/2,
                f"{row.aapc_prevalence:.2f} ({row.ci_low_prevalence:.2f} to {row.ci_high_prevalence:.2f}){row.significance_prevalence}",
                va='center', ha='left', fontsize=15, color='black',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='none'))
    
    for bar, row in zip(bars2, merged_df.itertuples()):
        ax.text(text_x, bar.get_y() + bar.get_height()/2,
                f"{row.aapc_dalys:.2f} ({row.ci_low_dalys:.2f} to {row.ci_high_dalys:.2f}){row.significance_dalys}",
                va='center', ha='left', fontsize=15, color='black',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor='none'))
    
    ax.set_xlabel('AAPC (%)', fontsize=15, fontweight='bold')
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)
    ax.set_yticks(y)
    ax.set_yticklabels(cause_labels, fontsize=15, fontweight='bold')
    for label in ax.get_yticklabels():
        label.set_x(-0.05)
    ax.tick_params(axis='y', pad=10)
    handles, labels_legend = ax.get_legend_handles_labels()
    errorbar_prevalence = plt.Line2D([0], [0], color=colors_prevalence, linewidth=1.5, marker='_', markersize=10, markeredgewidth=1.5)
    errorbar_dalys = plt.Line2D([0], [0], color=colors_dalys, linewidth=1.5, marker='_', markersize=10, markeredgewidth=1.5)
    handles.extend([errorbar_prevalence, errorbar_dalys])
    labels_legend.extend(['95% UI (Prevalence)', '95% UI (DALYs)'])
    ax.legend(handles, labels_legend, loc='upper center', bbox_to_anchor=(0.5, -0.15), 
              ncol=2, fontsize=15, frameon=False)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('black')
    ax.spines['bottom'].set_linewidth(0.5)
    
    ax.grid(axis='x', alpha=0.4, linestyle='-', linewidth=0.8, color='lightgray')
    ax.set_axisbelow(True)
    
    ax.tick_params(axis='x', which='major', length=6, width=0.5, direction='out')
    ax.tick_params(axis='x', which='minor', length=3, width=0.5, direction='out')
    ax.set_xticks(np.arange(x_min, x_max + 0.125, 0.125), minor=True)
    
    output_path = os.path.join(output_dir, 'Figure2_AAPC_Comparison.png')
    plt.savefig(output_path, bbox_inches='tight', transparent=True, dpi=300)
    print(f"Figure 2 saved: {output_path}")
    
    plt.close()
    return True

if __name__ == "__main__":
    file_path = '/～/data.csv'
    output_dir = '/~/Desktop/GBD'
    run_figure2(file_path, output_dir)
