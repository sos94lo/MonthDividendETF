import tkinter as tk
from tkinter import ttk
import etf_data

class ETFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monthly Dividend ETF Tracker")
        self.root.geometry("1400x600")

        # Create Treeview with scrollbars
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define Columns
        # 1. Basic Info: 9 cols
        basic_cols = ['ticker', 'name', 'market_cap', 'listing_date', 'index', 'est_dist', 'price', 'price_return', 'total_return']
        # 2. Returns: 6 cols
        return_cols = ['ret_1d', 'ret_1w', 'ret_1m', 'ret_3m', 'ret_6m', 'ret_1y']
        # 3. Monthly Dist: 12 months * 2 cols = 24 cols
        month_cols = []
        for m in range(1, 13):
            month_cols.extend([f'dist_{m}', f'yield_{m}'])

        self.columns = basic_cols + return_cols + month_cols

        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings', selectmode='browse')

        # Define Headings
        headings = {
            'ticker': '종목코드', 'name': '종목명', 'market_cap': '시가총액',
            'listing_date': '상장일', 'index': '기초지수', 'est_dist': '예상분배금',
            'price': '현재주가', 'price_return': '주가수익률', 'total_return': '총수익률',
            'ret_1d': '1일 수익률', 'ret_1w': '1주 수익률', 'ret_1m': '1개월 수익률',
            'ret_3m': '3개월 수익률', 'ret_6m': '6개월 수익률', 'ret_1y': '1년 수익률'
        }

        for m in range(1, 13):
            headings[f'dist_{m}'] = f'{m}월 분배금'
            headings[f'yield_{m}'] = f'{m}월 분배율'

        for col in self.columns:
            self.tree.heading(col, text=headings.get(col, col))
            self.tree.column(col, width=100, anchor=tk.CENTER)

        # Specific column widths
        self.tree.column('ticker', width=80)
        self.tree.column('name', width=200, anchor=tk.W) # Name left aligned

        # Scrollbars
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.grid(column=0, row=0, sticky='nsew')
        self.vsb.grid(column=1, row=0, sticky='ns')
        self.hsb.grid(column=0, row=1, sticky='ew')

        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        # Load Data Button
        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.load_btn = ttk.Button(self.btn_frame, text="Load Data", command=self.load_data)
        self.load_btn.pack(side=tk.RIGHT)

        # Auto load
        self.root.after(100, self.load_data)

    def load_data(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = etf_data.get_etf_data_detailed()

        for row in data:
            values = []
            for col in self.columns:
                val = row.get(col, "")

                # Formatting
                if isinstance(val, (int, float)):
                    if 'ret_' in col or 'yield_' in col: # Percentages
                         val = f"{val*100:.2f}%"
                    elif 'dist_' in col or col == 'est_dist': # Money (Distributions)
                         val = f"${val:.4f}"
                    elif col == 'price':
                         val = f"${val:.2f}"
                    elif col == 'market_cap':
                         val = f"{val:,}" # Commas

                values.append(val)

            self.tree.insert('', tk.END, values=values)

if __name__ == "__main__":
    root = tk.Tk()
    app = ETFApp(root)
    root.mainloop()
