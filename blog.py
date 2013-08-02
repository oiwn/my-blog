# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
from collections import Counter

from flask import Flask, render_template, send_from_directory, make_response
from flask.ext.flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer


app = Flask(__name__)
app.config.from_object('config')
pages = FlatPages(app)
freezer = Freezer(app)

@app.template_filter('date_to_iso')
def date_to_iso(s):
    '''
    Convert 2010-11-17 09:47 to python datetime
    '''

    date = datetime.strptime(s, '%Y-%m-%d %H:%M')
    return date.isoformat()


class StaticBlog(object):
    def __init__(self, pages_dir, blog_dirs, pages):
        self.pages_dir = pages_dir
        self.blog_dirs = blog_dirs
        self.pages = pages

        '''
        Functions to sort, get publishd and get page/blog articles
        '''

        self.sort_by_date = lambda articles: sorted(
            articles, reverse=True, key=lambda p: p.meta['date']
        )  # sort list of pages by date

        self.get_published = lambda articles: [
            p for p in articles if (p.meta.get('status', '') == 'published')
        ]  # return only pages with meta status 'published'

        self.articles_for_blog = lambda lang: [
            p for p in self.pages if p.path.startswith(self.blog_dirs[lang])
        ]  # return only blog articles


    def uniq_list(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x not in seen and not seen_add(x)]


    def get_flat_pages(self):
        pages = []
        for page in self.pages:
            if page.path.startswith(self.pages_dir):
                page_name, = page.path.split('/')[-1:]
                setattr(page, 'name', page_name)
                pages.append(page)
        return sorted(pages, reverse=False, key=lambda x: x.meta.get('position', 0))


    def get_flat_page_by_name(self, page_name):
        flat_page = None
        flat_pages = self.get_flat_pages()
        for page in flat_pages:
            if page.path.endswith(page_name):
                flat_page = page
                break
        return flat_page


    def get_blogs(self, post_limit=5):
        pages = []
        for page in self.pages:
            for lang, path in self.blog_dirs.items():
                if page.path.startswith(path):
                    page_name, = page.path.split('/')[-1:]
                    setattr(page, 'language', lang)
                    setattr(page, 'url', page_name)
                    pages.append(page)

        blogs = []
        for lang, path in app.config['BLOG_DIRS'].items():
            blog_data = {
                'language': lang,
                'articles': self.sort_by_date(
                    self.get_published(self.articles_for_blog(lang)))[:post_limit]
            }
            blogs.append(blog_data)

        return blogs


    def get_articles(self, language=None):
        articles = []
        for page in self.pages:
            for lang, path in self.blog_dirs.items():
                if (language is not None) and (lang != language):
                    continue
                if page.path.startswith(path):
                    page_name, = page.path.split('/')[-1:]
                    setattr(page, 'language', lang)
                    setattr(page, 'name', page_name)
                    articles.append(page)
        return self.sort_by_date(self.get_published(articles))


    def get_article_by_name(self, article_name):
        article = None
        articles = self.get_articles()
        for page in articles:
            if page.path.endswith(article_name):
                article = page
                break
        return article


    def get_categories(self):
        categories = sorted(self.uniq_list(
            [
                p.meta['category'] for p in self.get_articles()
                if p.meta.get('category', None)
            ]),
            key=lambda x: x[0])
        return categories


    def get_tags(self):
        tags = []
        for p in self.get_articles():
            if p.meta.get('tags', None) is not None:
                tags.extend(p.meta['tags'])
        tags = Counter(sorted(tags, key=lambda x: x[0]))
        tags_total = len(tags)

        # calculate index
        for tag, count in tags.items():
            index = int(float(count)/float(tags_total)*10)
            tags[tag] = app.config['TAG_RANK'][index]
        return tags


# create static blog instance
static_blog = StaticBlog(app.config['PAGES_DIR'], app.config['BLOG_DIRS'], pages)


@app.context_processor
def inject_nav_pages():
    return dict(flat_pages=static_blog.get_flat_pages())


@app.context_processor
def inject_sidebar():
    # inject categories list
    categories = static_blog.get_categories()
    # inject tags list
    tags = static_blog.get_tags()
    return dict(categories=categories, tags=tags)


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

    flat_pages = static_blog.get_flat_pages()
    articles = static_blog.get_articles()

    sitemap_xml = render_template('sitemap.xml', flat_pages=flat_pages, articles=articles)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@app.route('/')
def index():
    blogs = static_blog.get_blogs()
    return render_template('index.html', blogs=blogs)


@app.route('/page/<string:page_name>/')
def page(page_name):
    '''
    Render pages like 'about', 'experience', 'contacts'
    '''

    flat_page = static_blog.get_flat_page_by_name(page_name)
    return render_template('page.html', flat_page=flat_page)


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
        freezer.freeze()
    else:
        app.run(port=8000)
