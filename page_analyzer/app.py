from flask import Flask, render_template, flash
from flask import url_for, redirect, request
from datetime import datetime
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import validators
import psycopg2
from psycopg2.extras import NamedTupleCursor
import requests
from page_analyzer.parser import parse_page


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def connect_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def validate_url(url):

    if url == '':
        flash('Некорректный URL', 'alert alert-danger')
        flash('URL обязателен', 'alert alert-danger')
        return False

    if validators.url(url):
        o = urlparse(url)
        normalized_url = o.scheme + '://' + o.hostname
    else:
        flash('Некорректный URL', 'alert alert-danger')
        return False

    if len(normalized_url) > 255:
        flash('URL превышает 255 символов', 'alert alert-danger')
        return False

    return normalized_url


@app.route('/')
def main_page():
    return render_template('main_form.html')


@app.route('/urls')
def urls_get():

    conn = connect_db()
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            '''SELECT urls.id AS u_id, name,
            url_checks.created_at AS date, status_code
            FROM urls LEFT JOIN url_checks ON urls.id=url_checks.url_id
            JOIN
            (SELECT urls.id as u__id, MAX(url_checks.created_at) AS max_date
            FROM urls LEFT JOIN url_checks ON urls.id=url_checks.url_id
            GROUP BY u__id
            ) as maxdates
            ON urls.id=maxdates.u__id AND
            (url_checks.created_at=max_date OR url_checks.created_at IS NULL)
            ORDER BY u_id DESC
            ''')
        urls = curs.fetchall()
    conn.close()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():

    recieved_url = request.form.get('url', default='')
    normalized_url = validate_url(recieved_url)
    if not normalized_url:
        return render_template('main_form.html'), 422

    conn = connect_db()
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

    conn = connect_db()
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
        selected_url = curs.fetchone()
        curs.execute(
            '''SELECT * FROM url_checks
            WHERE url_id=%s ORDER BY id DESC''', (selected_url.id,))
        checks = curs.fetchall()
    conn.close()
    return render_template(
        'show_url.html', selected_url=selected_url, checks=checks)


@app.post('/urls/<id>/checks')
def checks(id):

    conn = connect_db()
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
        selected_url = curs.fetchone()
        try:
            r = requests.get(selected_url.name)
            r.raise_for_status()
        except Exception:
            flash('Произошла ошибка при проверке', 'alert alert-danger')
            conn.close()
            return redirect(url_for('show_url', id=id))
        status_code = r.status_code
        h1, title, description, created_at = parse_page(r)
        curs.execute(
            '''INSERT INTO url_checks (url_id, status_code,
            h1, title, description, created_at)
             VALUES (%s, %s, %s, %s, %s, %s)''',
            (selected_url.id, status_code, h1, title, description, created_at))
        flash('Страница успешно проверена', 'alert alert-success')
    conn.close()

    return redirect(url_for('show_url', id=id))
