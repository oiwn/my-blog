# -*- coding: utf-8 -*-
from datetime import datetime
from collections import Counter


class StaticBlog:
    """Render site content"""

    blogs = None

    post_date_format = "%Y-%m-%d %H:%M"

    '''
    Functions to sort, get publishd and get page/blog articles
    '''


    def _sort_by_date(self, articles):
        pass

    # hey! this one. why you compare dates as strings?
    sort_by_date = lambda self, articles: sorted(
        articles, reverse=True, key=lambda p: p.meta.get(
            'date', datetime.now().strftime(self.post_date_format))
    )  # sort list of pages by date
    sort_by_position = lambda self, pages: sorted(
        pages, reverse=False, key=lambda x: x.meta.get('position', 0)
    )  # sort list of pages by position value

    get_published = lambda self, articles: [
        p for p in articles if (p.meta.get('status', '') == 'published')
    ]  # return only pages with meta status 'published'


    def __init__(self, app, pages):
        self.app = app
        self.pages = pages
        self.site_structure = app.config['SITE_STRUCTURE']

        self.articles_for_blog = lambda blog, lang: [
            p for p in self.pages
            if p.path.startswith(self.site_structure['blogs'][blog][lang])
        ]  # return only blog articles


    def uniq_list(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x not in seen and not seen_add(x)]


    def sort_func(self, pages, by):
        default_value = None
        if isinstance(by, int):
            default_value = 0
        elif isinstance(by, str):
            default_value = ''
        else:
            raise Exception("Wrong 'by' type!")

        return sorted(pages, reverse=False, key=lambda x: x.meta.get(by, default_value))


    def get_blogs_names(self):
        sr_pages = self.site_structure['blogs']
        return sr_pages.keys()


    def get_pages_names(self):
        sr_pages = self.site_structure['flat_pages']
        return sr_pages.keys()


    def get_all_pages(self):
        '''
        Get all flat pages
        '''

        sr_pages = self.site_structure['flat_pages']
        pages = []
        for fl_page_name, fl_page_values in sr_pages.items():
            pages.extend(self.get_pages_for(fl_page_name))
        return pages


    def get_pages_for(self, name):
        '''
        Return pages list for something (wiki, flatpages etc.)
        '''

        sr_pages = self.site_structure['flat_pages']

        if name not in sr_pages.keys():
            raise Exception(
                "Wrong page name: {} (should be in {})".format(
                    name, sr_pages.keys()))

        pages = []
        for page in self.pages:
            if page.path.startswith(sr_pages[name]['url']):
                page_name, = page.path.split('/')[-1:]
                setattr(page, 'category', name)
                setattr(page, 'name', page_name)
                setattr(page, 'template', sr_pages[name]['template'])
                pages.append(page)

        sort_by = sr_pages[name]['sort_by']
        return self.sort_func(pages, sort_by)


    def get_page_by_name_for(self, name, page_name):
        result_page = None
        pages = self.get_pages_for(name)
        for page in pages:
            if page.path.endswith(page_name):
                result_page = page
                break
        return result_page


    def get_all_blogs(self, post_limit=5):
        sr_blogs = self.site_structure['blogs']
        blogs = {}
        for blog_name, blog_values in sr_blogs.items():
            for lang in blog_values.keys():
                articles = self.get_published(self.articles_for_blog(blog_name, lang))
                blog_data = {
                    'blog': blog_name,
                    'language': lang,
                    'count': len(articles),
                    'articles': self.sort_by_date(articles)[:post_limit]
                }
                if blog_name in blogs:
                    blogs[blog_name].update({lang: blog_data})
                else:
                    blogs[blog_name] = {lang: blog_data}

        return blogs


    def get_blog(self, name, post_limit=5):
        blog = {'name': name, 'subs': {}}
        sr_blogs = self.site_structure['blogs']
        for lang, path in sr_blogs[name].items():
            articles = self.get_published(self.articles_for_blog(name, lang))
            blog_data = {
                'blog': name,
                'language': lang,
                'count': len(articles),
                'articles': self.sort_by_date(articles)[:post_limit]
            }
            blog['subs'][lang] = blog_data

        return blog


    def get_all_articles(self):
        articles = []
        sr_blogs = self.site_structure['blogs']
        for blog_name, blog_data in sr_blogs.items():
            for lang, path in blog_data.items():
                articles.extend(self.get_articles(blog_name, lang))
        return articles


    def get_articles(self, name, language=None):
        articles = []
        sr_blogs = self.site_structure['blogs']
        for page in self.pages:
            for lang, path in sr_blogs[name].items():
                if (language is not None) and (lang != language):
                    continue
                if page.path.startswith(path):
                    page_name, = page.path.split('/')[-1:]
                    setattr(page, 'blog', name)
                    setattr(page, 'language', lang)
                    setattr(page, 'name', page_name)
                    articles.append(page)
        return self.sort_by_date(self.get_published(articles))


    def get_article_by_name(self, article_name):
        article = None
        articles = self.get_all_articles()
        for page in articles:
            if page.path.endswith(article_name):
                article = page
                break
        return article


    def count_articles_in_category(self, category):
        articles = self.sort_by_date(self.get_published(self.get_all_articles()))
        return len([p for p in articles if p.meta.get('category', '') == category])


    def get_categories(self):
        categories = sorted(
            self.uniq_list([
                p.meta['category'] for p in self.get_all_articles()
                if p.meta.get('category', None)
            ]),
            key=lambda x: x[0])
        return categories


    def get_tags(self):
        tags = []
        for p in self.get_all_articles():
            article_tags = p.meta.get('tags', None)
            if article_tags is not None:
                article_tags = [x.strip() for x in article_tags if x.strip()]
                tags.extend(p.meta['tags'])
        tags = Counter(sorted(tags, key=lambda x: x[0]))
        tags_total = len(tags)

        # calculate index
        for tag, count in tags.items():
            index = int(float(count)/float(tags_total)*10)
            tags[tag] = self.app.config['TAG_RANK'][index]
        return tags
