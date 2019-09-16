from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, SentiForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from . senti2 import senti
import pandas as pd

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('sentiment')) 
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('sentiment')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/sentiment', methods=['GET', 'POST'])
@login_required
def sentiment():
    form = SentiForm()
    searchtext = ''

    freq_pct = ''
    freq_cnt = ''
    labels_pct = ''
    values_pct = ''
    labels_cnt = ''
    values_cnt = ''
    
    pos_sel = ''
    neg_sel = ''
    net_sel = ''
    
    if form.validate_on_submit():
        searchtext = form.search.data
        df = senti(searchtext)
        pos_sel = df[df['sentiment'] == 'positive' ].head(10).to_html(index=False)
        neg_sel = df[df['sentiment'] == 'negative' ].head(10).to_html(index=False)
        net_sel = df[df['sentiment'] == 'netural' ].head(10).to_html(index=False)
        freq_pct = df['sentiment'].value_counts(normalize=True)
        freq_cnt = df['sentiment'].value_counts()
        labels_pct = list(freq_pct.sort_index(ascending=True).index)
        values_pct = list(freq_pct.sort_index(ascending=True))
        labels_cnt = list(freq_cnt.sort_index(ascending=True).index)
        values_cnt = list(freq_cnt.sort_index(ascending=True))
    return render_template('sentiment.html', 
        title='Sentiment', form=form, searchtext=searchtext, pos_df=pos_sel, neg_df=neg_sel, net_df=net_sel,
        values_pct=values_pct, labels_pct=labels_pct, values_cnt=values_cnt, labels_cnt=labels_cnt)