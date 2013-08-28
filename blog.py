# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime

from flask import Flask, render_template, send_from_directory, make_response
from flask.ext.flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer

from core import StaticBlog


app = Flask(__name__)
app.config.from_object('config')
pages = FlatPages(app)
freezer = Freezer(app)


# create static blog instance
static_blog = StaticBlog(app, pages)


@app.template_filter('date_to_iso')
def date_to_iso(s):
    '''
    Convert 2010-11-17 09:47 to python datetime
    '''

    date = datetime.strptime(s, '%Y-%m-%d %H:%M')
    return date.strftime('%Y-%m-%d')


@app.context_processor
def inject_nav_pages():
    return dict(flat_pages=static_blog.get_pages_for('flat_pages'))


@app.context_processor
def inject_sidebar():
    # inject categories list
    categories = static_blog.get_categories()
    # inject tags list
    tags = static_blog.get_tags()
    return dict(categories=categories, tags=tags)


'''
Views
'''

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}


@app.route('/CNAME')
def cname():
    cname_path = os.path.join(app.root_path, 'static')
    return send_from_directory(cname_path, 'CNAME', mimetype='text/plain')


@app.route('/favicon.ico')
def favicon():
    favicon_path = os.path.join(app.root_path, 'static')
    return send_from_directory(favicon_path, 'favicon.ico', mimetype='image/x-icon')


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """
    Generate sitemap.xml. Makes a list of urls and date modified.
    """

    flat_pages = static_blog.get_pages_for('flat_pages')
    articles = static_blog.get_articles()

    sitemap_xml = render_template('sitemap.xml', flat_pages=flat_pages, articles=articles)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/')
def index():
    blogs = static_blog.get_blogs()
    return render_template('index.html', blogs=blogs)


@app.route('/<string:name>/<string:page_name>/')
def page(name, page_name):
    '''
    Render flatpages
    '''

    flat_page = static_blog.get_page_by_name_for(name, page_name)
    return render_template(getattr(flat_page, 'template'), flat_page=flat_page)


@app.route('/wiki/')
def wiki_index():
    '''
    Render wiki pages
    '''

    wiki_pages = static_blog.get_pages_for('wiki_pages')
    return render_template('wiki_index.html', wiki_pages=wiki_pages)


"""
@app.route('/page/<string:page_name>/')
def page(page_name):
    '''
    Render pages like 'about', 'experience', 'contacts'
    '''

    flat_page = static_blog.get_flat_page_by_name(page_name)
    return render_template('page.html', flat_page=flat_page)


@app.route('/wiki/<string:page_name>/')
def wiki_page(page_name):
    '''
    Render wiki page
    '''

    wiki_page = static_blog.get_wiki_page_by_name(page_name)
    return render_template('wiki_page.html', wiki_page=wiki_page)
"""

@app.route('/blog/<string:lang>/')
def blog(lang):
    '''
    Render blog index page
    '''

    articles = static_blog.get_articles(language=lang)
    return render_template('blog.html', articles=articles, language=lang)


@app.route('/blog/<string:lang>/<string:article_name>/')
def post(lang, article_name):
    '''
    Render blog post
    '''

    article = static_blog.get_article_by_name(article_name)
    return render_template('post.html', article=article, language=lang)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', articles=tagged, tag=tag)


@app.route('/category/<string:category>/')
def category(category):
    articles = static_blog.get_articles()
    articles_in_category = [
        p for p in articles if category == p.meta.get('category', '')]
    return render_template('category.html', articles=articles_in_category,
                           category=category)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        app.config['CDN_STATIC'] = True
        freezer.freeze()
    else:
        app.run(port=8000)
