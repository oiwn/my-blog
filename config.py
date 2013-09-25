# -*- coding: utf-8 -*-

DEBUG = True
CDN_STATIC = False
BOOTSTRAP_CDN = False
PAGES_ADDITIONAL_JS = False
WEBSITE_URL = 'http://ninjaside.info'

FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_ROOT = 'content'
FLATPAGES_EXTENSION = '.md'

FREEZER_DESTINATION = 'website'
FREEZER_DESTINATION_IGNORE = ['.git*', '.gitignore']

SKIP_DIR = 'trash/'

SITE_STRUCTURE = {
    'flat_pages': {
        'page': {
            'url': 'pages/', 'sort_by': 'position', 'prefix': 'pages',
            'template': 'nav_page.html'
        },
        'wiki': {
            'url': 'wiki/', 'sort_by': 'title', 'prefix': 'wiki',
            'template': 'wiki_page.html'
        },
    },
    'blogs': {
        'blog': {
            'ru': 'blog/ru',
            'en': 'blog/en',
        },
        'music': {
            'ru': 'music/ru',
            'en': 'music/en',
        }
    }
}

BLOG_DIRS = [
    ''
]
PAGES_DIR = 'pages/'
WIKI_DIR = 'wiki/'
BLOG_DIRS = {'ru': 'blog/ru', 'en': 'blog/en'}
MUSIC_DIRS = {'ru': 'music/ru'}


TAG_RANK = (
	"tagRank10", "tagRank9", "tagRank8", "tagRank7", "tagRank6", "tagRank5",
	"tagRank4", "tagRank3", "tagRank2", "tagRank1"
)


import os
import logging

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)