# -*- coding: utf-8 -*-
from collections import Counter



class StaticBlog(object):
    pages_dir = None
    wiki_dir = None
    blogs = None


    '''
    Functions to sort, get publishd and get page/blog articles
    '''

    sort_by_date = lambda self, articles: sorted(
        articles, reverse=True, key=lambda p: p.meta['date']
    )  # sort list of pages by date
    sort_by_position = lambda self, pages: sorted(
        pages, reverse=False, key=lambda x: x.meta.get('position', 0)
    )  # sort list of pages by position value

    get_published = lambda self, articles: [
        p for p in articles if (p.meta.get('status', '') == 'published')
    ]  # return only pages with meta status 'published'


    def __init__(self, app, pages):
        self.app = app
        self.site_structure = app.config['SITE_STRUCTURE']


        self.pages_dir = app.config['PAGES_DIR']
        self.wiki_dir = app.config['WIKI_DIR']
        self.blog_dirs = app.config['BLOG_DIRS']
        self.pages = pages


        self.articles_for_blog = lambda lang: [
            p for p in self.pages if p.path.startswith(self.blog_dirs[lang])
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


    def get_pages_for(self, name):
        '''
        Return pages list for something (wiki, flatpages etc.)
        '''

        sr_pages = self.site_structure['pages']

        if name not in sr_pages.keys():
            raise Exception(
                "Wrong page name: {} (should be in {})".format(
                    name, sr_pages.keys()))

        pages = []
        for page in self.pages:
            if page.path.startswith(sr_pages[name]['url']):
                page_name, = page.path.split('/')[-1:]
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


    '''
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


    def get_wiki_pages(self):
        pages = []
        for page in self.pages:
            if page.path.startswith(self.wiki_dir):
                page_name, = page.path.split('/')[-1:]
                setattr(page, 'name', page_name)
                pages.append(page)
        return sorted(pages, reverse=False, key=lambda x: x.meta.get('title', ''))


    def get_wiki_page_by_name(self, page_name):
        wiki_page = None
        wiki_pages = self.get_wiki_pages()
        for page in wiki_pages:
            if page.path.endswith(page_name):
                wiki_page = page
                break
        return wiki_page
    '''

    def get_blogs(self, post_limit=5):
        '''
        pages = []
        for page in self.pages:
            for lang, path in self.blog_dirs.items():
                if page.path.startswith(path):
                    page_name, = page.path.split('/')[-1:]
                    setattr(page, 'language', lang)
                    setattr(page, 'url', page_name)
                    pages.append(page)
        '''
        blogs = []
        for lang, path in self.blog_dirs.items():
            articles = self.get_published(self.articles_for_blog(lang))
            blog_data = {
                'language': lang,
                'count': len(articles),
                'articles': self.sort_by_date(articles)[:post_limit]
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
        categories = sorted(
            self.uniq_list([
                p.meta['category'] for p in self.get_articles() 
                if p.meta.get('category', None)
            ]),
            key=lambda x: x[0])
        return categories


    def get_tags(self):
        tags = []
        for p in self.get_articles():
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
