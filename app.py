from flask import Flask, render_template, request, redirect, session
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'


def load_transactions(file_stream):
    """Read uploaded CSV file into a normalised DataFrame."""
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
    df = df.dropna(subset=['date'])
    return df


def compute_summary(df, start_date=None, end_date=None):
    """Compute accounting summary for an optional date range."""
    if start_date is not None:
        df = df[df['date'] >= start_date]
    if end_date is not None:
        df = df[df['date'] <= end_date]

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


def parse_transactions(file_stream, start_date=None, end_date=None):
    """Backwards compatible helper for tests; returns summary."""
    df = load_transactions(file_stream)
    return compute_summary(df, start_date, end_date)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return redirect(request.url)
        df = load_transactions(file)
        session['transactions'] = df.to_json(orient='records', date_format='iso')
        return redirect('/summary')
    return render_template('index.html')


@app.route('/summary')
def summary():
    data_json = session.get('transactions')
    if not data_json:
        return redirect('/')
    df = pd.read_json(data_json, orient='records')

    year = request.args.get('year', type=int)
    bas = request.args.get('bas', type=int)

    start = end = None
    if year:
        start = pd.Timestamp(year, 7, 1)
        end = pd.Timestamp(year + 1, 6, 30)
        if bas in {1, 2, 3, 4}:
            if bas == 1:
                start, end = pd.Timestamp(year, 7, 1), pd.Timestamp(year, 9, 30)
            elif bas == 2:
                start, end = pd.Timestamp(year, 10, 1), pd.Timestamp(year, 12, 31)
            elif bas == 3:
                start, end = pd.Timestamp(year + 1, 1, 1), pd.Timestamp(year + 1, 3, 31)
            else:  # bas == 4
                start, end = pd.Timestamp(year + 1, 4, 1), pd.Timestamp(year + 1, 6, 30)

    summary_data = compute_summary(df, start, end)
    filtered_df = df
    if start is not None:
        filtered_df = filtered_df[filtered_df['date'] >= start]
    if end is not None:
        filtered_df = filtered_df[filtered_df['date'] <= end]

    transactions = filtered_df.to_dict(orient='records')
    return render_template('summary.html', summary=summary_data, transactions=transactions)


if __name__ == '__main__':
    app.run(debug=True)
