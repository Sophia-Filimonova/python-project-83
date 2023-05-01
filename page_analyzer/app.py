from flask import Flask, render_template, flash, get_flashed_messages
from flask import url_for, redirect, request
from datetime import datetime
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import validators
import psycopg2
from psycopg2.extras import NamedTupleCursor


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main_form.html', messages=messages)


@app.route('/urls')
def urls_get():

    messages = get_flashed_messages(with_categories=True)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''SELECT urls.id as u_id, name, MAX(url_checks.created_at) as date
            FROM urls LEFT JOIN url_checks ON urls.id=url_checks.url_id
            GROUP BY u_id, name
            ORDER BY u_id DESC''')
        all_urls = curs.fetchall()
    conn.close()
    return render_template(
        'urls.html', messages=messages, urls=all_urls)


@app.post('/urls')
def urls_post():

    recieved_url = request.form.get('url', default='')
    if recieved_url == '':
        flash('Некорректный URL', 'alert alert-danger')
        flash('URL обязателен', 'alert alert-danger')
        return redirect(url_for('main_page'))

    if validators.url(recieved_url):
        o = urlparse(recieved_url)
        normalized_url = o.scheme + '://' + o.hostname
    else:
        flash('Некорректный URL', 'alert alert-danger')
        return redirect(url_for('main_page'))

    if len(normalized_url) > 255:
        flash('URL превышает 255 символов', 'alert alert-danger')
        return redirect(url_for('main_page'))

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as curs:
        curs.execute('SELECT name FROM urls')
        all_urls = curs.fetchall()
        for url in all_urls:
            if url == (normalized_url,):
                flash('Страница уже существует', 'alert alert-info')
                curs.execute(
                    'SELECT id FROM urls WHERE name=%s', (normalized_url,))
                (id,) = curs.fetchone()
                return redirect(url_for('show_url', id=id))
        created_at = datetime.now()
        curs.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
            (normalized_url, created_at))
        curs.execute('SELECT id FROM urls WHERE name=%s', (normalized_url,))
        (id,) = curs.fetchone()
    conn.close()
    flash('Страница успешно добавлена', 'alert alert-success')
    return redirect(url_for('show_url', id=id))


@app.route('/urls/<id>')
def show_url(id):

    messages = get_flashed_messages(with_categories=True)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
        selected_url = curs.fetchone()
        curs.execute(
            '''SELECT * FROM url_checks
            WHERE url_id=%s ORDER BY id DESC''', (selected_url.id,))
        checks = curs.fetchall()
    conn.close()
    return render_template(
        'show_url.html', messages=messages, selected_url=selected_url,
        checks=checks)


@app.post('/urls/<id>/checks')
def checks(id):

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
        selected_url = curs.fetchone()
        created_at = datetime.now()
        curs.execute(
            'INSERT INTO url_checks (url_id, created_at) VALUES (%s, %s)',
            (selected_url.id, created_at))
    conn.close()

    return redirect(url_for('show_url', id=id))
