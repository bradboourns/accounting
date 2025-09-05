from datetime import datetime
from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)


transactions_df = None


def load_transactions(file_stream):
    """Load transactions from a CSV stream and normalise the data."""
    df = pd.read_csv(file_stream)
    df.columns = df.columns.str.strip().str.lower()

    required = {"date", "description", "amount", "category"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required column(s): {', '.join(sorted(missing))}")

    if 'gst' not in df.columns:
        df['gst'] = 0

    df['category'] = df['category'].astype(str).str.lower()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    df['gst'] = pd.to_numeric(df['gst'], errors='coerce').fillna(0)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df


def calculate_summary(df):
    """Return accounting summaries for the provided DataFrame."""
    income = df[df['category'] == 'income']['amount'].sum()
    expenses = df[df['category'] == 'expense']['amount'].sum()
    profit_loss = income - expenses

    assets = df[df['category'] == 'asset']['amount'].sum()
    liabilities = df[df['category'] == 'liability']['amount'].sum()

    gst_collected = df[df['category'] == 'income']['gst'].sum()
    gst_paid = df[df['category'] == 'expense']['gst'].sum()
    gst_net = gst_collected - gst_paid

    return {
        'income': income,
        'expenses': expenses,
        'profit_loss': profit_loss,
        'assets': assets,
        'liabilities': liabilities,
        'gst_collected': gst_collected,
        'gst_paid': gst_paid,
        'gst_net': gst_net,
    }


def parse_transactions(file_stream):
    """Backward-compatible helper that loads and summarises transactions."""
    df = load_transactions(file_stream)
    return calculate_summary(df)


def filter_transactions(df, financial_year=None, bas_period=None):
    """Filter transactions by financial year and BAS period.

    Financial year refers to the year ending 30 June. BAS periods are
    quarters within that financial year (Q1-Q4).
    """
    if financial_year:
        start = datetime(financial_year - 1, 7, 1)
        end = datetime(financial_year, 6, 30)
        df = df[(df['date'] >= start) & (df['date'] <= end)]

    if bas_period and financial_year:
        if bas_period == 'Q1':
            start, end = datetime(financial_year - 1, 7, 1), datetime(financial_year - 1, 9, 30)
        elif bas_period == 'Q2':
            start, end = datetime(financial_year - 1, 10, 1), datetime(financial_year - 1, 12, 31)
        elif bas_period == 'Q3':
            start, end = datetime(financial_year, 1, 1), datetime(financial_year, 3, 31)
        elif bas_period == 'Q4':
            start, end = datetime(financial_year, 4, 1), datetime(financial_year, 6, 30)
        else:
            raise ValueError('Invalid BAS period')
        df = df[(df['date'] >= start) & (df['date'] <= end)]

    return df


@app.route('/', methods=['GET', 'POST'])
def index():
    global transactions_df
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return redirect(request.url)
        transactions_df = load_transactions(file)
        return redirect('/summary')
    return render_template('index.html')


@app.route('/summary')
def summary():
    if transactions_df is None:
        return redirect('/')
    fy = request.args.get('financial_year', type=int)
    bas = request.args.get('bas_period')
    df = filter_transactions(transactions_df, financial_year=fy, bas_period=bas)
    summary_data = calculate_summary(df)
    return render_template('summary.html', summary=summary_data, financial_year=fy, bas_period=bas)


@app.route('/transactions')
def transactions():
    if transactions_df is None:
        return redirect('/')
    fy = request.args.get('financial_year', type=int)
    bas = request.args.get('bas_period')
    df = filter_transactions(transactions_df, financial_year=fy, bas_period=bas)
    table = df.to_html(index=False)
    return render_template('transactions.html', table=table, financial_year=fy, bas_period=bas)


if __name__ == '__main__':
    app.run(debug=True)
