from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)


def parse_transactions(file_stream):
    """Parse uploaded CSV and compute accounting summaries.

    Expected columns: date, description, amount, category, gst
    - amount and gst should be numeric
    - category should be one of income, expense, asset, liability
    """
    df = pd.read_csv(file_stream)
    df['category'] = df['category'].str.lower()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    df['gst'] = pd.to_numeric(df['gst'], errors='coerce').fillna(0)

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return redirect(request.url)
        summary = parse_transactions(file)
        return render_template('summary.html', summary=summary)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
