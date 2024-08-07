from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Email settings
EMAIL_ADDRESS = 'paragiswalkar1987@gmail.com'
EMAIL_PASSWORD = 'qvtj ehvp rtkq gwzo'

def send_email(subject, body, to):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())
        print(f'Email sent to {to}')
    except Exception as e:
        print(f'Failed to send email: {e}')

@app.route('/')
def index():
    try:
        df = pd.read_csv('stocks.csv')
        symbols = df['symbol'].unique()
        return render_template('index.html', symbols=symbols)
    except Exception as e:
        flash(f'Error reading CSV file: {e}', 'danger')
        return render_template('index.html', symbols=[])

@app.route('/chart/<symbol>')
def chart(symbol):
    try:
        df = pd.read_csv('stocks.csv')
        df = df[df['symbol'] == symbol]

        fig = go.Figure(data=[go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        )])

        fig.update_layout(
            title=f'Candlestick Chart for {symbol}',
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            xaxis=dict(
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(204, 204, 204)'
                )
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                showticklabels=True,
                gridcolor='rgb(84, 84, 84)',
                linecolor='rgb(204, 204, 204)',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(204, 204, 204)'
                )
            ),
            legend=dict(
                font=dict(
                    family='Arial',
                    size=12,
                    color='rgb(204, 204, 204)'
                ),
                orientation='h',
                yanchor='bottom',
                xanchor='right'
            ),
            margin=dict(l=40, r=40, t=40, b=40)
        )

        fig.update_traces(
            increasing_line_color='rgba(0, 255, 0, 0.8)',
            decreasing_line_color='rgba(255, 0, 0, 0.8)',
            increasing_fillcolor='rgba(0, 255, 0, 0.2)',
            decreasing_fillcolor='rgba(255, 0, 0, 0.2)'
        )

        chart_html = fig.to_html(full_html=False)

        return render_template('chart.html', chart_html=chart_html, symbol=symbol)
    except Exception as e:
        flash(f'Error generating chart: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/check_prices')
def check_prices():
    try:
        df = pd.read_csv('stocks.csv')
        notifications = []
        for symbol in df['symbol'].unique():
            stock_data = df[df['symbol'] == symbol]
            latest_close = stock_data['close'].iloc[-1]

            # Ensure thresholds are numeric
            buy_threshold = pd.to_numeric(stock_data['buy_threshold'].iloc[0])
            sell_threshold = pd.to_numeric(stock_data['sell_threshold'].iloc[0])
            
            if latest_close <= buy_threshold:
                try:
                    print("Buy condition met")
                    notifications.append(f'Buy Alert for {symbol}: Price {latest_close} is below the buy threshold {buy_threshold}.')
                    send_email(
                        subject=f'Buy Alert for {symbol}',
                        body=f'The price of {symbol} has fallen to {latest_close}, which is below the buy threshold of {buy_threshold}.',
                        to='paragiswalkar1987@gmail.com'
                    )
                except Exception as e:
                    print(f'Error in buy notification: {e}')

            elif latest_close >= sell_threshold:
                try:
                    print("Sell condition met")
                    notifications.append(f'Sell Alert for {symbol}: Price {latest_close} is above the sell threshold {sell_threshold}.')
                    send_email(
                        subject=f'Sell Alert for {symbol}',
                        body=f'The price of {symbol} has risen to {latest_close}, which is above the sell threshold of {sell_threshold}.',
                        to='paragiswalkar1987@gmail.com'
                    )
                except Exception as e:
                    print(f'Error in sell notification: {e}')
        
        if notifications:
            flash(' '.join(notifications), 'success')
        else:
            flash('No notifications to send.', 'info')
    except Exception as e:
        flash(f'Error checking prices: {e}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)