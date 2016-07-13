#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, g, render_template, session, request, flash
from form import ContactFormFr, ContactFormEn
from db_manager import *

blueprint = Blueprint('frontend', __name__, url_prefix='/<lang_code>')


# ----------------Gestion URL------------------


@blueprint.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)


@blueprint.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@blueprint.route('/')
def index():
    if g.lang_code == "fr":
        return render_template('fr/corps_index.html', titre="ZompiGame")
    else:
        return render_template('en/corps_index.html', titre="ZompiGame")


@blueprint.route('/telechargement/')
def telechargement():
    if g.lang_code == "fr":
        return render_template('fr/corps_download.html', titre="Download")
    else:
        return render_template('en/corps_download.html', titre="Download")


@blueprint.route('/about/')
def about():
    if g.lang_code == "fr":
        return render_template('fr/corps_about.html', titre="Info")
    else:
        return render_template('en/corps_about.html', titre="Info")


@blueprint.route('/stats/')
def stats():
    stats = select()
    if g.lang_code == "fr":
        return render_template('fr/corps_stats.html', titre="Statistiques", stats=stats)
    else:
        return render_template('en/corps_stats.html', titre="Statistics", stats=stats)


@blueprint.route('/contact/', methods=['GET', 'POST'])
def contact():
    if g.lang_code == "fr":
        form = ContactFormFr(request.form)
    else:
        form = ContactFormEn(request.form)
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if not form.validate():
            if g.lang_code == "fr":
                flash('veuillez remplir correctement tout les champs.')
            else:
                flash('Please complete all fields !')
        else:
            nom = form.name.data
            email = form.email.data
            sujet = form.subject.data
            message = 'De: {} Email: {} Message: {}'.format(nom, email, form.message.data)

            insert(nom, email, sujet, message)

            if g.lang_code == "fr":
                flash('Votre message a bien ete envoyer !')
            else:
                flash('Your message has been sent !')
    if g.lang_code == "fr":
        return render_template('fr/corps_contact.html', titre="Contact", form=form)
    else:
        return render_template('en/corps_contact.html', titre="Contact", form=form)