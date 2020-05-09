from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

from features.downloader import *
from features.processing import *
from features.search import file_search

app = Flask(__name__)
reports = get_links()


@app.after_request
def add_header(r):  # отключить кэширование в браузере, чтобы картинки обновлялись
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/choose', methods=['GET'])
def download_links():
    return render_template('choose.html', reports=reports)


@app.route('/download', methods=['POST'])
def download_report():
    year = request.form.get('year')
    link = reports[year]
    get_pdf(link=link, year=year)
    txt_exists = os.path.exists(f'app/static/data/txt/CBR_report{year}.txt')
    norm_exists = os.path.exists(f'app/static/data/norm/CBR_report{year}_norm.txt')
    freq_exists = os.path.exists(f'app/static/images/freq{year}.png')
    plot_exists = os.path.exists(f'app/static/images/dict{year}.png')
    return render_template('document.html', year=year,
                           txt_exists=txt_exists,
                           norm_exists=norm_exists,
                           freq_exists=freq_exists,
                           plot_exists=plot_exists)


@app.route('/convert', methods=['POST'])
def convert_to_txt():
    year = request.data.decode('utf8')
    get_txt(year)
    return jsonify({"success": True})


@app.route('/normalize', methods=['POST'])
def normalize():
    year = request.data.decode('utf8')
    normalizer(year)
    return jsonify({"success": True})


@app.route('/draw_plot', methods=['POST'])
def draw_plot():
    year = request.data.decode('utf8')
    return plot_dict_size(year)


@app.route('/draw_freq', methods=['POST'])
def draw_freq():
    year = request.data.decode('utf8')
    return plot_freq_table(year)


@app.route('/search', methods=['POST'])
def search():
    req = request.get_json()
    pattern = req['query']
    year = req['year']
    metric = req['metric']
    n_pad_words = int(req['n_pad'])
    exact_search = req['exact_search']
    result = file_search(pattern, year, metric, n_pad_words, exact_search)
    success = result is not None
    return_json = {"success": success}
    if success:
        left = ' '.join(result.split()[:n_pad_words])
        return_json['left'] = left
        middle = ' '.join(result.split()[n_pad_words:-n_pad_words])
        return_json['middle'] = middle
        right = ' '.join(result.split()[-n_pad_words:])
        return_json['right'] = right

    return jsonify(return_json)
