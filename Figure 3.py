#Figure 3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.font_manager import FontProperties
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 600
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def generate_percentage_tables(filtered_data, measures, years):
    print("Generating percentage data tables...")
    tables = {}
    
    for measure in measures:
        for year in years:
            data_subset = filtered_data[
                (filtered_data['year'] == year) & 
                (filtered_data['measure'] == measure)
            ]
            
            if len(data_subset) == 0:
                continue
            
            pivot_table = data_subset.pivot_table(
                values='percentage', 
                index='location', 
                columns='cause', 
                fill_value=0,
                aggfunc='mean'
            )
            
            pivot_table = pivot_table.round(1)
            pivot_table['Total'] = pivot_table.sum(axis=1).round(1)
            tables[f'{measure}_{year}'] = pivot_table
    
    return tables

def save_percentage_tables(tables, output_dir):
    if not tables:
        return None, None
        
    excel_path = os.path.join(output_dir, 'Figure3_percentage_tables.xlsx')
    final_csv_path = os.path.join(output_dir, 'Figure3_all_percentages.csv')
    
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for table_name, table in tables.items():
                table.to_excel(writer, sheet_name=table_name)
        print(f"Excel file saved: {excel_path}")
    except:
        excel_path = None
    
    try:
        combined_data = []
        for table_name, table in tables.items():
            measure, year = table_name.split('_')
            table_copy = table.reset_index()
            table_copy.insert(0, 'Measure', measure)
            table_copy.insert(1, 'Year', int(year))
            combined_data.append(table_copy)
        
        if combined_data:
            final_table = pd.concat(combined_data, ignore_index=True)
            final_table.to_csv(final_csv_path, index=False, encoding='utf-8')
            print(f"Combined CSV file saved: {final_csv_path}")
    except:
        final_csv_path = None
    
    return excel_path, final_csv_path

def plot_stacked_bar(data, measure, year, ax, colors, hatches, annotate=True):
    data_subset = data[
        (data['year'] == year) & 
        (data['measure'] == measure)
    ]
    
    if len(data_subset) == 0:
        return None
    
    pivot_data = data_subset.pivot_table(
        values='percentage', 
        index='location', 
        columns='cause', 
        fill_value=0
    )
    
    color_list = [colors[cause] for cause in pivot_data.columns]
    
    bars = pivot_data.plot(
        kind='barh', 
        stacked=True, 
        ax=ax, 
        color=color_list,
        linewidth=0.8,
        edgecolor='white',
    )
    
    for i, container in enumerate(ax.containers):
        if i < len(hatches):
            for patch in container.patches:
                patch.set_hatch(hatches[i])
    
    ax.set_title(f'{year}', fontsize=16)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.legend().set_visible(False)

    if annotate:
        for container in ax.containers:
            labels = []
            for v in container.datavalues:
                if v >= 3:
                    labels.append(f'{int(round(v))}')
                else:
                    labels.append('')
            ax.bar_label(container, labels=labels, label_type='center', 
                        fontsize=13, fontweight='bold', color='black')

    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_ticks_position('none')

    for bar in ax.patches:
        bar.set_height(bar.get_height() * 1.5)
    ax.margins(y=0.02)
    
    return bars

def run_figure3(file_path, output_dir):
    ensure_dir(output_dir)
    
    measures = ['Prevalence', 'DALYs']
    locations = [
        'Global', 'High SDI', 'High-middle SDI', 'Middle SDI', 'Low-middle SDI', 'Low SDI',
        'Andean Latin America', 'Australasia', 'Caribbean', 'Central Asia', 
        'Central Europe', 'Central Latin America', 'Central Sub-Saharan Africa', 
        'East Asia', 'Eastern Europe', 'Eastern Sub-Saharan Africa', 
        'High-income Asia Pacific', 'High-income North America', 
        'North Africa and Middle East', 'Oceania', 'South Asia', 
        'South-East Asia Region', 'Southern Latin America', 
        'Southern Sub-Saharan Africa', 'Tropical Latin America', 
        'Western Europe', 'Western Sub-Saharan Africa'
    ]
    years = [1990, 2021]
    causes = [
        'Attention-deficit/hyperactivity disorder', 'Autism spectrum disorders', 
        'Epilepsy', 'Hearing loss', 'Intellectual disability', 'Vision loss'
    ]
    
    colors = {
        "Attention-deficit/hyperactivity disorder": "#0072B2",
        "Autism spectrum disorders": "#E69F00",
        "Epilepsy": "#009E73",
        "Hearing loss": "#F0E442",
        "Intellectual disability": "#D55E00",
        "Vision loss": "#CC79A7"
    }
    
    hatches = ['|||||', '/////', '\\\\\\\\\\\\\\\\\\\\', '++++', '----', 'oooo']
    
    print("Reading data...")
    try:
        data = pd.read_csv(file_path, encoding='utf-8')
        print(f"Data loaded successfully, total rows: {len(data)}")
    except Exception as e:
        print(f"Error reading data: {e}")
        return False
    
    print("Filtering data...")
    filtered_data = data[
        (data['metric'] == 'Rate') & 
        (data['age'] == '<20 years') & 
        (data['sex'] == 'Both') & 
        (data['location'].isin(locations)) & 
        (data['year'].isin(years)) & 
        (data['measure'].isin(measures)) & 
        (data['cause'].isin(causes))
    ].copy()
    
    print(f"Filtered data rows: {len(filtered_data)}")
    
    filtered_data.loc[:, 'val_sum'] = filtered_data.groupby(['location', 'year', 'measure'])['val'].transform('sum')
    filtered_data.loc[:, 'percentage'] = (filtered_data['val'] / filtered_data['val_sum']) * 100
    
    filtered_data['location'] = pd.Categorical(
        filtered_data['location'], 
        categories=locations[::-1], 
        ordered=True
    )
    filtered_data = filtered_data.sort_values(
        by=['location', 'year', 'measure'], 
        ascending=[False, True, True]
    )
    
    percentage_tables = generate_percentage_tables(filtered_data, measures, years)
    excel_file, csv_file = save_percentage_tables(percentage_tables, output_dir)

    print("Generating side-by-side charts...")
    for measure in measures:
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(16, 14), sharey=True)
        fig.subplots_adjust(hspace=0.3, wspace=0.05)

        for j, year in enumerate(years):
            ax = axes[j]
            plot_stacked_bar(filtered_data, measure, year, ax, colors, hatches)

        fig.text(0.5, 0.9, f'{measure} (%)', ha='center', fontsize=18, fontweight='bold')

        integrated_path = os.path.join(output_dir, f'Figure3_{measure}_integrated_plot.tiff')
        plt.savefig(integrated_path, bbox_inches='tight', dpi=600, format='tiff')
        plt.close()
        print(f"Saved: {measure}_integrated_plot.tiff")
    
    legend_handles = []
    for i, cause in enumerate(causes):
        patch = plt.Rectangle((0, 0), 1, 1, 
                             fc=colors[cause],
                             ec='white',
                             lw=2.0,
                             hatch=hatches[i] if i < len(hatches) else '')
        legend_handles.append(patch)
    
    font_props = FontProperties(family='Times New Roman', size=14)
    
    print("Generating combined plot...")
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(16, 28), sharey=True)
    fig.subplots_adjust(hspace=0)

    for i, measure in enumerate(measures):
        img_path = os.path.join(output_dir, f'Figure3_{measure}_integrated_plot.tiff')
        if os.path.exists(img_path):
            try:
                img = plt.imread(img_path)
                axes[i].imshow(img)
                axes[i].axis('off')
            except Exception as e:
                print(f"Image loading failed: {e}")
                axes[i].text(0.5, 0.5, f'Loading {measure}...', 
                           ha='center', va='center', transform=axes[i].transAxes)

        box = axes[i].get_position()
        axes[i].set_position([box.x0, box.y0 + 0.08, box.width, box.height * 0.7])

    legend = fig.legend(
        legend_handles, 
        causes, 
        loc='center right', 
        bbox_to_anchor=(1.2, 0.5),
        prop=font_props,
        handlelength=3.0,
        borderpad=1.2,
        frameon=True,
        edgecolor='#CCCCCC',
        framealpha=1.0,
        fancybox=False,
        shadow=False,
        labelspacing=1.2
    )

    fig.tight_layout(pad=0, rect=[0, 0, 0.93, 1])

    final_combined_path = os.path.join(output_dir, 'Figure3_final.tiff')
    plt.savefig(final_combined_path, bbox_inches='tight', dpi=600, format='tiff')
    
    png_path = os.path.join(output_dir, 'Figure3_final.png')
    plt.savefig(png_path, bbox_inches='tight', dpi=300)
    
    plt.close()
    print(f"Final combined plot saved: {final_combined_path}")

    color_info = pd.DataFrame([
        {
            "Condition": cause, 
            "Color_Hex": color, 
            "Pattern": hatches[i] if i < len(hatches) else "",
        }
        for i, (cause, color) in enumerate(colors.items())
    ])
    
    color_info_path = os.path.join(output_dir, 'Figure3_color_scheme.csv')
    color_info.to_csv(color_info_path, index=False)
    
    print(f"Chart generation completed.")
    print(f"Output files:")
    print(f"  - Combined plot: {final_combined_path}")
    print(f"  - Data tables: {excel_file}")
    print(f"  - Combined data: {csv_file}")
    
    return True

if __name__ == "__main__":
    file_path = '/～/data.csv'
    output_dir = '/Users/patricia-yj/Desktop/GBD'
    run_figure3(file_path, output_dir)