

import os
import sys
from figure1_joinpoint import run_figure1
from figure2_aapc import run_figure2
from figure3_percentage import run_figure3

def main():
    """main function: running all analyses"""
    print("=" * 60)
    print("GBD data analysis tool")
    print("=" * 60)
    
    output_dir = '/Users/patricia-yj/Desktop/GBD'
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\noutput directory: {output_dir}\n")
    
    print("provide the data file path:")
    print("  Figure 1 needs .xlsx file (contains 3 sheets)")
    print("  Figure 2 needs .csv file")
    print("  Figure 3 needs .csv file")
    
    figure1_data = input("\nFigure 1 data file path (xlsx): ").strip()
    if not figure1_data:
        figure1_data = "/path/to/your/data.xlsx" 
    
    figure2_data = input("Figure 2 data file path (csv): ").strip()
    if not figure2_data:
        figure2_data = "/path/to/your/data.csv"  

    figure3_data = input("Figure 3 data file path (csv): ").strip()
    if not figure3_data:
        figure3_data = "/path/to/your/data.csv"  
    

    print("\n" + "=" * 60)
    print("select the analysis to run:")
    print("  1. Figure 1 - Joinpoint regression analysis")
    print("  2. Figure 2 - AAPC comparison analysis")
    print("  3. Figure 3 - percentage stacked chart")
    print("  4. running all analyses")
    choice = input("\nenter the option (1-4): ").strip()
    
    results = []
    
    print("\n" + "=" * 60)
    print("starting analysis...")
    print("=" * 60)
    
    try:
        if choice in ['1', '4']:
            print("\n[1/3] running Figure 1 - Joinpoint regression analysis...")
            if os.path.exists(figure1_data):
                result = run_figure1(figure1_data)
                results.append(("Figure 1", result))
            else:
                print(f"error: file not found - {figure1_data}")
                results.append(("Figure 1", False))
        
        if choice in ['2', '4']:
            print("\n[2/3] running Figure 2 - AAPC comparison analysis...")
            if os.path.exists(figure2_data):
                result = run_figure2(figure2_data, output_dir)
                results.append(("Figure 2", result))
            else:
                print(f"error: file not found - {figure2_data}")
                results.append(("Figure 2", False))
        
        if choice in ['3', '4']:
            print("\n[3/3] running Figure 3 - percentage stacked chart...")
            if os.path.exists(figure3_data):
                result = run_figure3(figure3_data, output_dir)
                results.append(("Figure 3", result))
            else:
                print(f"error: file not found - {figure3_data}")
                results.append(("Figure 3", False))
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("analysis completed!")
    print("=" * 60)
    print("\nresult summary:")
    for name, success in results:
        status = "✓ success" if success else "✗ failed"
        print(f"  {name}: {status}")
    
    print(f"\nall output files saved in: {output_dir}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\ninterupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nerror: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)