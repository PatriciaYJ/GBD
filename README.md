# GBD Data Analysis Tool

This project contains Python scripts for analyzing Global Burden of Disease (GBD) data, generating three types of visualizations and statistical analyses.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Data Requirements](#data-requirements)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)
- [Author](#author)

## 🎯 Project Overview

This tool analyzes developmental disability trends from GBD data, focusing on six conditions:
- ADHD (Attention-deficit/hyperactivity disorder)
- ASD (Autism spectrum disorders)
- Epilepsy
- Hearing Loss
- Intellectual Disability
- Vision Loss

The analysis generates three main figures:
1. **Figure 1**: Joinpoint regression analysis showing trend changes over time
2. **Figure 2**: AAPC (Average Annual Percent Change) comparison between Prevalence and DALYs
3. **Figure 3**: Percentage stacked bar charts by region and SDI level

## ✨ Features

- **Automated Analysis**: Run all three analyses with a single command
- **High-Quality Outputs**: Generates publication-ready figures (PNG, PDF, TIFF formats)
- **Data Tables**: Exports statistical results to CSV and Excel formats
- **Customizable**: Easy to modify parameters and styling
- **Error Handling**: Robust error checking and user-friendly messages

## 📁 Project Structure

```
GBD/
├── figure1_joinpoint.py    # Joinpoint regression analysis
├── figure2_aapc.py          # AAPC comparison analysis
├── figure3_percentage.py    # Percentage stacked charts
├── main.py                  # Main execution script
├── README.md                # This file
└── requirements.txt         # Python dependencies (optional)
```

## 🔧 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Step 1: Install Python (if not already installed)

**macOS:**
```bash
# Using Homebrew
brew install python3
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install Required Packages

```bash
pip install pandas numpy matplotlib openpyxl scikit-learn scipy geopandas
```

Or create a `requirements.txt` file:

```txt
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
openpyxl>=3.0.0
scikit-learn>=0.24.0
scipy>=1.7.0
geopandas>=0.9.0
```

Then install:
```bash
pip install -r requirements.txt
```

### Step 3: Download Project Files

1. Create a project directory:
```bash
mkdir -p /Users/patricia-yj/Desktop/GBD
cd /Users/patricia-yj/Desktop/GBD
```

2. Copy all Python files to this directory

## 🚀 Usage

### Quick Start

1. **Prepare your data files** (see [Data Requirements](#data-requirements))

2. **Run the main script**:
```bash
cd /Users/patricia-yj/Desktop/GBD
python main.py
```

3. **Follow the prompts**:
   - Enter paths to your data files
   - Choose which analyses to run (1-4)
   - Wait for completion

### Running Individual Analyses

**Figure 1 Only:**
```bash
python figure1_joinpoint.py
```

**Figure 2 Only:**
```bash
python figure2_aapc.py
```

**Figure 3 Only:**
```bash
python figure3_percentage.py
```

### Advanced Usage

Edit the file paths directly in the Python scripts:

```python
# In figure1_joinpoint.py
file_path = "/path/to/your/data.xlsx"

# In figure2_aapc.py
file_path = "/path/to/your/data.csv"
output_dir = "/Users/patricia-yj/Desktop/GBD"

# In figure3_percentage.py
file_path = "/path/to/your/data.csv"
output_dir = "/Users/patricia-yj/Desktop/GBD"
```

Then run:
```bash
python figure1_joinpoint.py
python figure2_aapc.py
python figure3_percentage.py
```

## 📊 Data Requirements

### Figure 1 Data Format (Excel - .xlsx)

**Required Sheets:**
- **Sheet1**: Raw prevalence/DALYs data
- **Sheet2**: AAPC (Average Annual Percent Change) data
- **Sheet3**: APC (Annual Percent Change) by segment

**Required Columns:**
- `year`: Year (1990-2021)
- `age`: Age group (must include '<20 years')
- `sex`: Sex category (use 'Both')
- `location`: Geographic location (use 'Global')
- `cause`: Disease name
- `measure`: Measure type ('Prevalence' or 'DALYs')
- `val`: Value
- `upper`: Upper confidence interval
- `lower`: Lower confidence interval

### Figure 2 Data Format (CSV - .csv)

**Required Columns:**
- `year`: Year (1990-2021)
- `cause`: Disease name
- `location`: Must include 'Global'
- `sex`: Must include 'Both'
- `age`: Must include '<20 years' pattern
- `metric`: Must be 'Rate'
- `measure`: 'Prevalence' or 'DALYs'
- `val`: Value

### Figure 3 Data Format (CSV - .csv)

**Required Columns:**
- `year`: Year (1990, 2021)
- `location`: Region or SDI level
- `age`: Must be '<20 years'
- `sex`: Must be 'Both'
- `metric`: Must be 'Rate'
- `measure`: 'Prevalence' or 'DALYs'
- `cause`: Disease name
- `val`: Value

**Supported Locations:**
- SDI levels: Global, High SDI, High-middle SDI, Middle SDI, Low-middle SDI, Low SDI
- Regions: Andean Latin America, Australasia, Caribbean, Central Asia, etc.

## 📤 Output Files

All output files are saved to `/Users/patricia-yj/Desktop/GBD/`

### Figure 1 Outputs:
- `Figure1_Joinpoint_Analysis.png` (300 DPI)
- `Figure1_Joinpoint_Analysis.pdf` (Vector format)

### Figure 2 Outputs:
- `Figure2_AAPC_Comparison.png` (300 DPI)
- `Figure2_AAPC_Results.csv` (Statistical results)

### Figure 3 Outputs:
- `Figure3_final.tiff` (600 DPI, publication quality)
- `Figure3_final.png` (300 DPI, preview)
- `Figure3_percentage_tables.xlsx` (Data tables by year)
- `Figure3_all_percentages.csv` (Combined data)
- `Figure3_color_scheme.csv` (Color legend reference)

## 🔍 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'pandas'**
```bash
# Solution: Install missing packages
pip install pandas numpy matplotlib openpyxl
```

**2. FileNotFoundError: [Errno 2] No such file or directory**
```bash
# Solution: Check your file paths
# Make sure the data file exists at the specified location
ls /path/to/your/data.xlsx
```

**3. Permission Denied Error**
```bash
# Solution: Check folder permissions
chmod 755 /Users/patricia-yj/Desktop/GBD
```

**4. Empty or Invalid Data**
- Verify your data has all required columns
- Check that column names match exactly (case-sensitive)
- Ensure data values are not empty or corrupted

**5. Font Warning Messages**
```python
# Solution: The script will use default fonts
# You can install additional fonts or ignore these warnings
import warnings
warnings.filterwarnings('ignore')
```

### Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify your data format matches requirements
3. Ensure all dependencies are installed
4. Check file paths are correct
5. Look for typos in disease names or column headers

## 📝 Customization

### Changing Colors

Edit the color scheme in each script:

```python
# In figure1_joinpoint.py
self.disease_colors = {
    "Attention-deficit/hyperactivity disorder": "#0072B2",
    "Autism spectrum disorders": "#E69F00",
    # ... add your colors
}
```

### Modifying Output Resolution

```python
# Change DPI settings
plt.savefig(output_path, dpi=600)  # Default is 300
```

### Adding New Diseases

```python
# In relevant script
diseases = [
    'ADHD',
    'ASD',
    'Your New Disease',  # Add here
    # ...
]
```

## 📄 License

This project is provided as-is for research and educational purposes.

## 👤 Author

**PatriciaYJ**
- Created: 2025-10-02
- Location: /Users/patricia-yj/Desktop/GBD

## 🙏 Acknowledgments

- Data source: Global Burden of Disease Study
- Analysis methods: Joinpoint regression, AAPC calculation
- Visualization: Matplotlib, Pandas

## 📚 References

For more information about the analysis methods:
- Joinpoint Regression: [National Cancer Institute](https://surveillance.cancer.gov/joinpoint/)
- GBD Study: [IHME](http://www.healthdata.org/gbd)

---

**Last Updated**: 2025-10-02  
**Version**: 1.0  
**Python Version**: 3.7+

---

## 🚦 Quick Reference Commands

```bash
# Navigate to project directory
cd /Users/patricia-yj/Desktop/GBD

# Run all analyses
python main.py

# Run individual figure
python figure1_joinpoint.py
python figure2_aapc.py
python figure3_percentage.py

# Check Python version
python --version

# Install dependencies
pip install pandas numpy matplotlib openpyxl scikit-learn scipy

# List output files
ls -lh /Users/patricia-yj/Desktop/GBD/Figure*.png
```

---

For questions or issues, please check the Troubleshooting section or review the console output for specific error messages.