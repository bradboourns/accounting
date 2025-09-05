from flask import Flask, render_template, request, redirect, flash
import pandas as pd


app = Flask(__name__)
app.secret_key = "dev"


def parse_transactions(file_stream):
    """Parse uploaded CSV and compute accounting summaries.

    The parser is flexible with column names. The CSV must include at least
    ``date``, ``description`` and ``amount`` columns (case-insensitive).
    If ``category`` is missing, it is inferred from the sign of ``amount``.
    If ``gst`` is missing, it is estimated at 10% of the absolute amount.
    """

    df = pd.read_csv(file_stream)
    # Normalise column names for case-insensitive lookup
    df.columns = df.columns.str.strip().str.lower()

    required = {"date", "description", "amount"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    if "category" in df.columns:
        df["category"] = df["category"].str.lower()
    else:
        # Infer category from the sign of amount
        df["category"] = df["amount"].apply(lambda x: "income" if x >= 0 else "expense")

    if "gst" in df.columns:
        df["gst"] = pd.to_numeric(df["gst"], errors="coerce").abs().fillna(0)
    else:
        df["gst"] = df["amount"].abs() * 0.1

    income_total = df[df["category"] == "income"]["amount"].clip(lower=0).sum()
    expenses_total = df[df["category"] == "expense"]["amount"].abs().sum()
    profit_loss = income_total - expenses_total

    assets = df[df["category"] == "asset"]["amount"].abs().sum()
    liabilities = df[df["category"] == "liability"]["amount"].abs().sum()

    gst_collected = df[df["category"] == "income"]["gst"].sum()
    gst_paid = df[df["category"] == "expense"]["gst"].sum()
    gst_net = gst_collected - gst_paid

    return {
        "income": income_total,
        "expenses": expenses_total,
        "profit_loss": profit_loss,
        "assets": assets,
        "liabilities": liabilities,
        "gst_collected": gst_collected,
        "gst_paid": gst_paid,
        "gst_net": gst_net,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("No file selected")
            return redirect(request.url)
        try:
            summary = parse_transactions(file)
        except ValueError as exc:  # pragma: no cover - simple feedback
            flash(str(exc))
            return redirect(request.url)
        return render_template("summary.html", summary=summary)
    return render_template("index.html")


if __name__ == "__main__":  # pragma: no cover - manual run helper
    app.run(debug=True)

