from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>청구서 자동 생성기</title>
    <style>
        body { font-family: sans-serif; padding: 2em; }
        label { font-weight: bold; display: block; margin-top: 1em; }
        .media-block { margin-top: 0.5em; }
    </style>
</head>
<body>
    <h2>청구서 자동 생성기</h2>
    <form method="post" action="/generate">
        <label>클라이언트명:
            <select name="client">
                <option value="더마초이스">더마초이스</option>
                <option value="페오펫">페오펫</option>
            </select>
        </label>

        <label>매체 및 금액 입력:</label>
        <div class="media-block">
            <label>메타: <input type="number" name="media_메타"></label>
            <label>네이버 SA: <input type="number" name="media_네이버 SA"></label>
            <label>네이버 GFA: <input type="number" name="media_네이버 GFA"></label>
            <label>구글: <input type="number" name="media_구글"></label>
        </div>
        <button type="submit">엑셀 생성</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_invoice():
    client = request.form.get('client')
    media_keys = ['메타', '네이버 SA', '네이버 GFA', '구글']

    data = []
    total_supply = 0
    total_vat = 0
    total_sum = 0
    period = f"{datetime.now().month}/1 - {datetime.now().month}/30"

    for media in media_keys:
        amount_str = request.form.get(f"media_{media}")
        if not amount_str:
            continue
        amount = int(amount_str)
        supply = round(amount / 1.1)
        vat = amount - supply
        total = amount

        data.append([media, period, supply, vat, total])
        total_supply += supply
        total_vat += vat
        total_sum += total

    data.append(["총합", "", total_supply, total_vat, total_sum])
    df = pd.DataFrame(data, columns=["매체", "운영기간", "공급가액", "부가세", "합계"])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="청구 내역")
    output.seek(0)

    filename = f"청구서_{client}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
