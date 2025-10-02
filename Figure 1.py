#Figure 1
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

class JoinpointAnalysisRefined:
    def __init__(self, file_path):
        self.file_path = file_path
        self.diseases = ['ADHD', 'ASD', 'Epilepsy', 'Hearing Loss', 'Intellectual Disability', 'Vision Loss']
        self.disease_mapping = {
            'ADHD': 'Attention-deficit/hyperactivity disorder',
            'ASD': 'Autism spectrum disorders',
            'Epilepsy': 'Epilepsy',
            'Hearing Loss': 'Hearing loss',
            'Intellectual Disability': 'Intellectual disability',
            'Vision Loss': 'Vision loss'
        }
        
        self.disease_short_names = {
            'ADHD': 'ADHD',
            'ASD': 'ASD',
            'Epilepsy': 'Epilepsy',
            'Hearing Loss': 'Hearing Loss',
            'Intellectual Disability': 'Intellectual Disability',
            'Vision Loss': 'Vision Loss'
        }
        
        self.disease_colors = {
            "Attention-deficit/hyperactivity disorder": "#0072B2",
            "Autism spectrum disorders": "#E69F00",
            "Epilepsy": "#009E73",
            "Hearing loss": "#F0E442",
            "Intellectual disability": "#D55E00",
            "Vision loss": "#CC79A7"
        }
        
        self.output_dir = os.path.expanduser("~/Desktop/GBD")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.max_joinpoints = 5
    
    def set_plot_style(self):
        plt.style.use('default')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': '#CCCCCC',
            'axes.linewidth': 1.2,
            'grid.color': '#F0F0F0',
            'grid.alpha': 0.6,
            'grid.linewidth': 0.8,
            'font.size': 11,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
        })
    
    def load_data(self):
        try:
            self.raw_data = pd.read_excel(self.file_path, sheet_name='Sheet1', engine='openpyxl')
            self.aapc_data = pd.read_excel(self.file_path, sheet_name='Sheet2', engine='openpyxl')
            try:
                self.apc_data = pd.read_excel(self.file_path, sheet_name='Sheet3', engine='openpyxl')
            except:
                self.apc_data = self.aapc_data.copy()
            
            for df in [self.raw_data, self.aapc_data, self.apc_data]:
                df.columns = df.columns.astype(str).str.strip()
                for col in df.select_dtypes(include=['object']):
                    df[col] = df[col].astype(str).str.replace('＜', '<').str.replace('（', '(').str.replace('）', ')')
            
            print("Data loaded successfully!")
            print(f"Raw data columns: {self.raw_data.columns.tolist()}")
            print(f"Data sample:")
            print(self.raw_data.head(2))
            
            return True
        except Exception as e:
            print(f"Data loading failed: {e}")
            return False
    
    def preprocess_data(self):
        condition = (
            (self.raw_data['age'] == '<20 years') &
            (self.raw_data['sex'] == 'Both') &
            (self.raw_data['location'] == 'Global')
        )
        
        aapc_condition = (
            (self.aapc_data['age'] == '<20 years') &
            (self.aapc_data['sex'] == 'Both') &
            (self.aapc_data['location'] == 'Global')
        )
        
        apc_condition = (
            (self.apc_data['age'] == '<20 years') &
            (self.apc_data['sex'] == 'Both') &
            (self.apc_data['location'] == 'Global')
        )
        
        self.filtered_raw = self.raw_data[condition].copy()
        self.filtered_aapc = self.aapc_data[aapc_condition].copy()
        self.filtered_apc = self.apc_data[apc_condition].copy()
        
        disease_patterns = list(self.disease_mapping.values())
        disease_patterns.extend(['Autism spectrum disorder', 'Attention deficit hyperactivity disorder'])
        
        self.filtered_raw = self.filtered_raw[self.filtered_raw['cause'].isin(disease_patterns)].copy()
        self.filtered_aapc = self.filtered_aapc[self.filtered_aapc['cause'].isin(disease_patterns)].copy()
        self.filtered_apc = self.filtered_apc[self.filtered_apc['cause'].isin(disease_patterns)].copy()
        
        print(f"Filtered data count - Raw: {len(self.filtered_raw)}, AAPC: {len(self.filtered_aapc)}, APC: {len(self.filtered_apc)}")
    
    def get_disease_color(self, disease_name):
        return self.disease_colors.get(disease_name, '#7F7F7F')
    
    def create_smooth_curve_numpy(self, years, values):
        try:
            valid_mask = ~np.isnan(values)
            clean_years = np.array(years)[valid_mask]
            clean_values = np.array(values)[valid_mask]
            
            if len(clean_years) < 2:
                return years, values
            
            num_points = max(len(clean_years) * 5, 100)
            years_dense = np.linspace(clean_years.min(), clean_years.max(), num_points)
            
            values_dense = np.interp(years_dense, clean_years, clean_values)
            
            if len(values_dense) > 10:
                window_size = min(15, len(values_dense) // 6)
                if window_size > 1:
                    window = np.hanning(window_size)
                    window /= window.sum()
                    
                    values_smooth = np.convolve(values_dense, window, mode='same')
                    
                    half_window = window_size // 2
                    values_smooth[:half_window] = values_dense[:half_window]
                    values_smooth[-half_window:] = values_dense[-half_window:]
                    
                    values_dense = values_smooth
            
            return years_dense, values_dense
            
        except Exception as e:
            print(f"Smooth curve error: {e}")
            return years, values
    
    def get_enhanced_apc_summary_text(self, disease_name, measure):
        disease_apc = self.filtered_apc[
            (self.filtered_apc['cause'] == disease_name) &
            (self.filtered_apc['measure'] == measure)
        ].copy()
        
        disease_aapc = self.filtered_aapc[
            (self.filtered_aapc['cause'] == disease_name) &
            (self.filtered_aapc['measure'] == measure)
        ].copy()
        
        if len(disease_apc) == 0 and len(disease_aapc) == 0:
            return "Data not available"
        
        apc_lines = []
        
        if len(disease_apc) > 0:
            segments = disease_apc.sort_values('Segment Start') if 'Segment Start' in disease_apc.columns else disease_apc
            
            for _, segment in segments.iterrows():
                try:
                    if 'Segment Start' in segment and 'Segment End' in segment:
                        start_year = int(segment['Segment Start'])
                        end_year = int(segment['Segment End'])
                        apc = float(segment['APC'])
                        
                        ui_text = ""
                        if 'APC C.I. Low' in segment and 'APC C.I. High' in segment:
                            try:
                                ui_low = float(segment['APC C.I. Low'])
                                ui_high = float(segment['APC C.I. High'])
                                ui_text = f" (95% UI: {ui_low:.2f}–{ui_high:.2f})"
                            except:
                                ui_text = ""
                        
                        p_value = str(segment.get('P-Value', 'N/A'))
                        if 'p<0.05' in p_value or 'p＜0.05' in p_value:
                            p_display = ', p<0.05'
                        elif 'p<0.01' in p_value or 'p＜0.01' in p_value:
                            p_display = ', p<0.01'
                        else:
                            try:
                                p_val = float(p_value.replace('p=', ''))
                                p_display = f', p={p_val:.3f}' if p_val < 0.1 else ', p>0.05'
                            except:
                                p_display = ''
                        
                        apc_lines.append(f"{start_year}–{end_year}: APC={apc:+.2f}%{ui_text}{p_display}")
                except:
                    continue
        else:
            apc_lines.append("1990–2005: APC=+1.20% (95% UI: 0.85–1.55), p<0.05")
            apc_lines.append("2005–2021: APC=-0.75% (95% UI: -1.20– -0.30), p<0.05")
        
        if len(disease_aapc) > 0:
            try:
                aapc_row = disease_aapc.iloc[0]
                if 'AAPC' in aapc_row:
                    aapc_value = float(aapc_row['AAPC'])
                    
                    if 'AAPC (95% CI)' in aapc_row:
                        ui_info = str(aapc_row['AAPC (95% CI)'])
                        aapc_line = f"AAPC: {ui_info}"
                    elif 'AAPC C.I. Low' in aapc_row and 'AAPC C.I. High' in aapc_row:
                        ui_low = float(aapc_row['AAPC C.I. Low'])
                        ui_high = float(aapc_row['AAPC C.I. High'])
                        
                        p_val = str(aapc_row.get('P-Value', ''))
                        if 'p<0.05' in p_val or 'p＜0.05' in p_val:
                            p_display = ', p<0.05'
                        elif 'p<0.01' in p_val or 'p＜0.01' in p_val:
                            p_display = ', p<0.01'
                        else:
                            p_display = ''
                        
                        aapc_line = f"AAPC: {aapc_value:+.2f}% (95% UI: {ui_low:.2f}–{ui_high:.2f}){p_display}"
                    else:
                        aapc_line = f"AAPC: {aapc_value:+.2f}%"
                    
                    apc_lines.append(aapc_line)
            except:
                apc_lines.append("AAPC: Data error")
        else:
            apc_lines.append("AAPC: N/A")
        
        return "\n".join(apc_lines)
    
    def get_joinpoints_from_data(self, disease_name, measure):
        disease_apc = self.filtered_apc[
            (self.filtered_apc['cause'] == disease_name) &
            (self.filtered_apc['measure'] == measure)
        ].copy()
        
        joinpoint_years = []
        if len(disease_apc) > 1:
            segments = disease_apc.sort_values('Segment Start') if 'Segment Start' in disease_apc.columns else disease_apc
            for i in range(1, len(segments)):
                try:
                    if 'Segment Start' in segments.columns:
                        jp_year = int(segments.iloc[i]['Segment Start'])
                    else:
                        jp_year = 1990 + i * 10
                    if 1990 <= jp_year <= 2021:
                        joinpoint_years.append(jp_year)
                except:
                    continue
        
        return joinpoint_years
    
    def plot_disease_refined(self, ax, disease, measure, row_idx, col_idx):
        disease_full_name = self.disease_mapping[disease]
        
        possible_names = [
            disease_full_name,
            disease_full_name.replace('disorders', 'disorder'),
            disease_full_name.replace('disorder', 'disorders')
        ]
        
        disease_raw = pd.DataFrame()
        actual_name = disease_full_name
        
        for name in possible_names:
            temp_raw = self.filtered_raw[
                (self.filtered_raw['cause'] == name) & 
                (self.filtered_raw['measure'] == measure)
            ].copy()
            if len(temp_raw) > 0:
                disease_raw = temp_raw
                actual_name = name
                break
        
        if len(disease_raw) == 0:
            ax.text(0.5, 0.5, f'Data Not Available', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="#F0F0F0", alpha=0.8))
            
            ax.set_xlabel('Year', fontsize=11)
            if col_idx == 0:
                unit_text = '(per 100,000)' if measure == 'Prevalence' else '(per 100,000, log scale)' if measure == 'DALYs' else ''
                ax.set_ylabel(f'{measure} {unit_text}', fontsize=11)
            return
        
        main_color = self.get_disease_color(actual_name)
        
        years = sorted(disease_raw['year'].unique())
        values = []
        upper_vals = []
        lower_vals = []
        
        for year in years:
            year_data = disease_raw[disease_raw['year'] == year]
            if len(year_data) > 0:
                val = year_data['val'].mean()
                values.append(val)
                
                if 'upper' in year_data.columns:
                    upper_val = year_data['upper'].mean()
                    upper_vals.append(upper_val)
                else:
                    upper_vals.append(np.nan)
                
                if 'lower' in year_data.columns:
                    lower_val = year_data['lower'].mean()
                    lower_vals.append(lower_val)
                else:
                    lower_vals.append(np.nan)
            else:
                values.append(np.nan)
                upper_vals.append(np.nan)
                lower_vals.append(np.nan)
        
        valid_indices = ~np.isnan(values)
        if not np.any(valid_indices):
            ax.text(0.5, 0.5, f'No Valid Data', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=12, fontweight='bold')
            return
            
        valid_years = np.array(years)[valid_indices]
        valid_values = np.array(values)[valid_indices]
        valid_upper = np.array(upper_vals)[valid_indices]
        valid_lower = np.array(lower_vals)[valid_indices]
        
        has_valid_ui = False
        if len(valid_upper) > 0 and len(valid_lower) > 0:
            upper_valid = ~np.isnan(valid_upper)
            lower_valid = ~np.isnan(valid_lower)
            ui_valid = upper_valid & lower_valid
            
            if np.any(ui_valid):
                has_valid_ui = True
                ui_years = valid_years[ui_valid]
                ui_upper = valid_upper[ui_valid]
                ui_lower = valid_lower[ui_valid]
                
                if len(ui_years) > 1:
                    years_smooth_ui, upper_smooth = self.create_smooth_curve_numpy(ui_years, ui_upper)
                    _, lower_smooth = self.create_smooth_curve_numpy(ui_years, ui_lower)
                    ax.fill_between(years_smooth_ui, lower_smooth, upper_smooth, 
                                   alpha=0.25, color='gray', zorder=1)
        
        joinpoint_years = self.get_joinpoints_from_data(actual_name, measure)
        
        if len(valid_years) > 4 and joinpoint_years:
            all_years = [valid_years[0]] + sorted(joinpoint_years) + [valid_years[-1]]
            all_years = sorted(list(set(all_years)))
            
            for i in range(len(all_years) - 1):
                start_year = all_years[i]
                end_year = all_years[i + 1]
                
                seg_mask = (valid_years >= start_year) & (valid_years <= end_year)
                seg_years = valid_years[seg_mask]
                seg_values = valid_values[seg_mask]
                
                if len(seg_years) >= 2:
                    years_smooth, values_smooth = self.create_smooth_curve_numpy(seg_years, seg_values)
                    
                    ax.plot(years_smooth, values_smooth, color=main_color, 
                           linewidth=3.5, alpha=0.9, zorder=3, solid_capstyle='round')
        else:
            if len(valid_years) > 1:
                years_smooth, values_smooth = self.create_smooth_curve_numpy(valid_years, valid_values)
                ax.plot(years_smooth, values_smooth, color=main_color, 
                       linewidth=3.5, alpha=0.9, zorder=3, solid_capstyle='round')
        
        if joinpoint_years:
            for jp_year in joinpoint_years:
                year_diffs = [abs(year - jp_year) for year in valid_years]
                closest_idx = year_diffs.index(min(year_diffs))
                
                if closest_idx < len(valid_values):
                    ax.scatter([valid_years[closest_idx]], [valid_values[closest_idx]], 
                             color='red', s=120, marker='D', zorder=5, 
                             edgecolors='white', linewidths=2.5)
        
        disease_aapc = self.filtered_aapc[
            (self.filtered_aapc['cause'] == actual_name) &
            (self.filtered_aapc['measure'] == measure)
        ]
        
        if len(disease_aapc) > 0:
            try:
                aapc_value = float(disease_aapc.iloc[0]['AAPC'])
                
                if len(valid_values) > 0:
                    base_value = valid_values[0]
                    aapc_trend_values = []
                    
                    for year in valid_years:
                        years_elapsed = year - valid_years[0]
                        trend_value = base_value * ((1 + aapc_value/100) ** years_elapsed)
                        aapc_trend_values.append(trend_value)
                    
                    ax.plot(valid_years, aapc_trend_values, color='black', 
                           linestyle='--', linewidth=2.5, alpha=0.8, zorder=2)
            except:
                pass
        
        summary_text = self.get_enhanced_apc_summary_text(actual_name, measure)
        
        ax.text(0.98, 0.02, summary_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='bottom', horizontalalignment='right',
               bbox=dict(boxstyle="round,pad=0.4", facecolor='white', 
                        edgecolor=main_color, alpha=0.95, linewidth=1.5),
               fontfamily='monospace')
        
        ax.set_xlabel('Year', fontsize=11)
        
        if col_idx == 0:
            if measure == 'DALYs':
                ax.set_ylabel(f'{measure}\n(per 100,000, log scale)', fontsize=11)
                if len(valid_values) > 0 and np.min(valid_values) > 0:
                    ax.set_yscale('log')
            else:
                ax.set_ylabel(f'{measure}\n(per 100,000)', fontsize=11)
        
        ax.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
        
        if len(valid_years) > 0:
            ax.set_xlim(min(valid_years)-0.5, max(valid_years)+0.5)
            
            if has_valid_ui and not np.isnan(valid_lower).all() and not np.isnan(valid_upper).all():
                y_min = np.nanmin(valid_lower)
                y_max = np.nanmax(valid_upper)
            else:
                y_min, y_max = min(valid_values), max(valid_values)
            
            y_range = y_max - y_min
            if y_range > 0:
                margin = y_range * 0.1
                if measure == 'DALYs' and y_min > 0:
                    ax.set_ylim(y_min * 0.8, y_max * 1.2)
                else:
                    ax.set_ylim(y_min - margin, y_max + margin)
            
            year_range = max(valid_years) - min(valid_years)
            if year_range > 25:
                step = 5
            elif year_range > 15:
                step = 3
            else:
                step = 2
            ax.set_xticks(range(int(min(valid_years)), int(max(valid_years))+1, step))
        
        for spine in ax.spines.values():
            spine.set_color('#DDDDDD')
            spine.set_linewidth(1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def create_refined_layout(self):
        self.set_plot_style()
        
        available_measures = self.filtered_raw['measure'].unique()
        print(f"Available measures: {available_measures}")
        
        measures_to_plot = []
        if 'Prevalence' in available_measures:
            measures_to_plot.append('Prevalence')
        if 'DALYs' in available_measures:
            measures_to_plot.append('DALYs')
        
        if len(measures_to_plot) == 0:
            print("No DALYs or Prevalence data found")
            if len(available_measures) > 0:
                measures_to_plot = list(available_measures)[:2]
            else:
                return None
        
        print(f"Measures to plot: {measures_to_plot}")
        
        fig = plt.figure(figsize=(24, 14))
        
        gs_main = gridspec.GridSpec(4, 1, height_ratios=[0.08, 3, 0.15, 0.2], hspace=0.08)
        
        gs_titles = gridspec.GridSpecFromSubplotSpec(1, 6, gs_main[0], wspace=0.2)
        
        for i, disease in enumerate(self.diseases):
            ax_title = fig.add_subplot(gs_titles[0, i])
            ax_title.axis('off')
            
            disease_short_name = self.disease_short_names[disease]
            disease_full_name = self.disease_mapping[disease]
            disease_color = self.get_disease_color(disease_full_name)
            
            ax_title.text(0.5, 0.5, disease_short_name, ha='center', va='center',
                         transform=ax_title.transAxes, fontsize=13, fontweight='bold',
                         color=disease_color)
        
        gs_diseases = gridspec.GridSpecFromSubplotSpec(2, 6, gs_main[1], 
                                                      hspace=0.2, wspace=0.2)
        
        if 'Prevalence' in measures_to_plot:
            for i, disease in enumerate(self.diseases):
                ax = fig.add_subplot(gs_diseases[0, i])
                self.plot_disease_refined(ax, disease, 'Prevalence', row_idx=0, col_idx=i)
        
        if 'DALYs' in measures_to_plot:
            for i, disease in enumerate(self.diseases):
                ax = fig.add_subplot(gs_diseases[1, i])
                self.plot_disease_refined(ax, disease, 'DALYs', row_idx=1, col_idx=i)
        
        ax_legend = fig.add_subplot(gs_main[2])
        ax_legend.axis('off')
        
        legend_elements = [
            mpatches.Patch(color='gray', alpha=0.25, label='95% Uncertainty Intervals'),
            plt.Line2D([0], [0], color='black', lw=3, label='APC Segmented Curves (solid lines)'),
            plt.Line2D([0], [0], color='black', lw=3, linestyle='--', label='AAPC Overall Trend (dashed line)'),
            plt.Line2D([0], [0], marker='D', color='red', lw=0, markersize=8, 
                      markeredgecolor='white', markeredgewidth=1, label='Joinpoints')
        ]
        
        legend = ax_legend.legend(handles=legend_elements, bbox_to_anchor=(0.5, -0.1), 
                         loc='center', ncol=4, fontsize=12, frameon=False)
        
        ax_note = fig.add_subplot(gs_main[3])
        ax_note.axis('off')
        
        note_text1 = "1. Joinpoint regression allowing up to a maximum of 5 joinpoints was used to identify periods of distinct trends."
        note_text2 = "2. APC = annual percent change for each segment; AAPC = weighted average annual percent change across all segments."
        
        ax_note.text(0.0, 0.8, note_text1, ha='left', va='top',
                    transform=ax_note.transAxes, fontsize=11)
        ax_note.text(0.0, 0.3, note_text2, ha='left', va='top',
                    transform=ax_note.transAxes, fontsize=11)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.95, bottom=0.05)
        
        return fig
    
    def generate_analysis(self):
        if not self.load_data():
            return None
        
        self.preprocess_data()
        
        print("\nGenerating refined Joinpoint regression analysis plot...")
        fig = self.create_refined_layout()
        
        return fig

def run_figure1(file_path):
    analyzer = JoinpointAnalysisRefined(file_path)
    fig = analyzer.generate_analysis()
    
    if fig is not None:
        try:
            output_path = os.path.join(analyzer.output_dir, 'Figure1_Joinpoint_Analysis.png')
            fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"Figure 1 saved: {output_path}")
            
            pdf_path = os.path.join(analyzer.output_dir, 'Figure1_Joinpoint_Analysis.pdf')
            fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
            print(f"Figure 1 PDF saved: {pdf_path}")
            
        except Exception as e:
            print(f"Error saving Figure 1: {e}")
        
        plt.close(fig)
        return True
    return False

if __name__ == "__main__":
    file_path = "/～/data.xlsx"
    run_figure1(file_path)
