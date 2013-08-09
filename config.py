DEBUG = True
CDN_STATIC = True
WEBSITE_URL = 'http://ninjaside.info'

FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_ROOT = 'content'
FLATPAGES_EXTENSION = '.md'

FREEZER_DESTINATION = 'website'
FREEZER_DESTINATION_IGNORE = ['.git*']

SKIP_DIR = 'trash/'
PAGES_DIR = 'pages/'
WIKI_DIR = 'wiki/'
BLOG_DIRS = {'ru': 'blog/ru', 'en': 'blog/en'}

TAG_RANK = (
	"tagRank10", "tagRank9", "tagRank8", "tagRank7", "tagRank6", "tagRank5",
	"tagRank4", "tagRank3", "tagRank2", "tagRank1"
)
