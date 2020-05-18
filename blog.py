# -*- coding: utf-8 -*-
import os
import sys
from urllib.parse import urljoin
from datetime import datetime

from flask import (Flask, render_template, send_from_directory,
                   make_response, request, url_for)
from flask_flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer
#  from werkzeug.contrib.atom import AtomFeed
from werkzeug.routing import BaseConverter, ValidationError

from core import StaticBlog
from config import WEBSITE_URL


app = Flask(__name__)
app.config.from_object('config')
# flat-pages and freezer
pages = FlatPages(app)
freezer = Freezer(app)
# create static blog instance
static_blog = StaticBlog(app, pages)


'''
Some additional
'''

def make_external(url):
    return urljoin(WEBSITE_URL, url)


'''
Url converters, to avoid wrong url pattern matching
'''

class NoSomethingConverter(BaseConverter):
    restriction = []

    def __ini__(self, url_map):
        super(NoSomethingConverter, self).__init__(url_map)

    def to_python(self, value):
        if value in self.restriction():
            raise ValidationError()
        return value


class NoStaticConverter(NoSomethingConverter):
    restriction = lambda x: ['static']
app.url_map.converters['no_static'] = NoStaticConverter

class NoBlogsConverter(NoSomethingConverter):
    restriction = static_blog.get_blogs_names
app.url_map.converters['no_blogs'] = NoBlogsConverter

class NoPagesConverter(NoSomethingConverter):
    restriction = static_blog.get_pages_names
app.url_map.converters['no_pages'] = NoPagesConverter


'''
Template filters and context processors
'''

@app.template_filter('date_to_iso')
def date_to_iso(s):
    '''
    Convert 2010-11-17 09:47 to python datetime
    '''

    date = datetime.strptime(s, '%Y-%m-%d %H:%M')
    return date.strftime('%Y-%m-%d')


@app.template_filter('count_articles_in_category')
def count_articles_in_category(s):
    return static_blog.count_articles_in_category(s)


@app.context_processor
def inject_nav_pages():
    return dict(flat_pages=static_blog.get_pages_for('page'))


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

    flat_pages = static_blog.get_all_pages()
    articles = static_blog.get_all_articles()

    sitemap_xml = render_template('sitemap.xml', flat_pages=flat_pages, articles=articles)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


"""TODO: AtomFeed is deprecated
@app.route('/feed.atom')
def recent_feed():
    feed = AtomFeed('Ninjaside.info Atom Feed', feed_url=request.url, url=request.url_root)
    articles = static_blog.get_articles('blog', language="ru")
    for article in articles:
        feed.add(
            article.meta['title'], article.meta['summary'],
            content_type='html',
            url=make_external(url_for('post', name=article.blog, lang=article.language, article_name=article.name)),
            updated=datetime.strptime(article.meta['date'], static_blog.post_date_format),
            published=datetime.strptime(article.meta['date'], static_blog.post_date_format)
        )
    return feed.get_response()
"""


@app.route('/')
def index():
    blogs = static_blog.get_all_blogs()
    return render_template('index.html', blogs=blogs)


@app.route('/<no_blogs:name>/<string:page_name>/')
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

    wiki_pages = static_blog.get_pages_for('wiki')
    return render_template('wiki_index.html', wiki_pages=wiki_pages)


@app.route('/<no_pages:name>/')
def blog_lang(name):
    '''
    Render blog page with languages
    '''

    blog = static_blog.get_blog(name)
    return render_template('blog_all.html', blog=blog)


@app.route('/<no_pages:name>/<string:lang>/')
def blog(name, lang):
    '''
    Render blog index page
    '''

    articles = static_blog.get_articles(name, language=lang)
    return render_template('blog.html', articles=articles, language=lang)


@app.route('/<no_static:name>/<string:lang>/<string:article_name>/')
def post(name, lang, article_name):
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
    articles = static_blog.get_all_articles()
    articles_in_category = [
        p for p in articles if category == p.meta.get('category', '')]
    return render_template('category.html', articles=articles_in_category,
                           category=category)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        app.config['CDN_STATIC'] = True
        app.config['PAGES_ADDITIONAL_JS'] = True
        freezer.freeze()
    else:
        app.run(port=8000)
