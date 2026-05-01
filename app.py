from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import base64
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
HF_TOKEN = os.getenv("HF_API_TOKEN")


def analyze_dataframe(df):
    analysis = {}

    analysis['rows'] = len(df)
    analysis['columns'] = len(df.columns)
    analysis['missing_values'] = int(df.isnull().sum().sum())
    analysis['duplicates'] = int(df.duplicated().sum())

    analysis['column_names'] = df.columns.tolist()

    return analysis


def get_ai_insights(analysis_summary):
    return f"""
1. Dataset contains {analysis_summary['rows']} rows and {analysis_summary['columns']} columns.

2. Missing values found: {analysis_summary['missing_values']}. Data cleaning may improve quality.

3. Available columns are {analysis_summary['column_names']}. These can be used for deeper analysis.
"""


def create_visualizations(df):
    charts = []

    numeric_cols = df.select_dtypes(include='number').columns[:3]

    for col in numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 4))

        df[col].hist(ax=ax, bins=20)

        ax.set_title(f"Distribution of {col}")

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        charts.append(img_base64)

        plt.close()

    return charts


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']

    df = pd.read_csv(file)

    analysis = analyze_dataframe(df)

    ai_insights = get_ai_insights(analysis)

    charts = create_visualizations(df)

    return jsonify({
        'rows': analysis['rows'],
        'columns': analysis['columns'],
        'missing': analysis['missing_values'],
        'duplicates': analysis['duplicates'],
        'column_names': analysis['column_names'],
        'ai_insights': ai_insights,
        'charts': charts
    })


if __name__ == '__main__':
    app.run(debug=True)