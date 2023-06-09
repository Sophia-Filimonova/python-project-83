from flask import Flask, render_template, flash
from flask import url_for, redirect, request
from datetime import datetime
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
import requests
from page_analyzer.parser import get_seo_data
from page_analyzer.url import validate_url


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def connect_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


@app.route('/')
def main_page():
    return render_template('main_form.html')


@app.route('/urls')
def urls_get():

    with connect_db() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(
                '''SELECT u_id, name, max_date, status_code
                FROM
                (SELECT urls.id as u_id, name,
                MAX(url_checks.created_at) AS max_date
                FROM urls LEFT JOIN url_checks ON urls.id=url_checks.url_id
                GROUP BY u_id, name
                ) AS maxdates
                LEFT JOIN url_checks ON (url_checks.url_id=maxdates.u_id
                AND url_checks.created_at=maxdates.max_date)
                ORDER BY u_id DESC''')
            urls = curs.fetchall()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def urls_post():

    recieved_url = request.form.get('url', default='')
    errors = validate_url(recieved_url)
    if errors:
        for error in errors:
            flash(error, 'alert alert-danger')
        return render_template('main_form.html'), 422
    parsed_url = urlparse(recieved_url)
    normalized_url = parsed_url.scheme + '://' + parsed_url.hostname

    with connect_db() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            created_at = datetime.now()
            try:
                curs.execute(
                    '''INSERT INTO urls (name, created_at) VALUES (%s, %s)
                    RETURNING id''',
                    (normalized_url, created_at))
            except psycopg2.errors.UniqueViolation:
                flash('Страница уже существует', 'alert alert-info')
                with connect_db() as conn2:
                    with conn2.cursor() as curs2:
                        curs2.execute(
                            '''SELECT id FROM urls WHERE name=%s''',
                            (normalized_url, ))
                        (id,) = curs2.fetchone()
                return redirect(url_for('show_url', id=id))
            (id,) = curs.fetchone()
    flash('Страница успешно добавлена', 'alert alert-success')
    return redirect(url_for('show_url', id=id))


@app.route('/urls/<id>')
def show_url(id):

    with connect_db() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            selected_url = curs.fetchone()
            curs.execute(
                '''SELECT * FROM url_checks
                WHERE url_id=%s ORDER BY id DESC''', (selected_url.id,))
            checks = curs.fetchall()
    return render_template(
        'show_url.html', selected_url=selected_url, checks=checks)


@app.post('/urls/<id>/checks')
def checks(id):

    with connect_db() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            selected_url = curs.fetchone()
            try:
                response = requests.get(selected_url.name)
                response.raise_for_status()
            except Exception:
                flash('Произошла ошибка при проверке', 'alert alert-danger')
                return redirect(url_for('show_url', id=id))
            status_code = response.status_code
            h1, title, description = get_seo_data(response.text)
            created_at = datetime.now()
            curs.execute(
                '''INSERT INTO url_checks (url_id, status_code,
                h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)''',
                (selected_url.id, status_code, h1, title,
                 description, created_at))
            flash('Страница успешно проверена', 'alert alert-success')

    return redirect(url_for('show_url', id=id))
