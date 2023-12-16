from datetime import datetime
import pytz

TIMEZONE = 'Europe/Paris'
BUILD_TIME = datetime.now(pytz.timezone(TIMEZONE))

AUTHOR = 'LC'
SITENAME = "bibliographer"
SITESUBTITLE = 'a curated TCS bibliography'
SITEURL = 'https://lclem.github.io/bibliographer'
TIMEZONE = "Europe/Paris"

THEME = 'themes/bootstrap2'
OUTPUT_PATH = 'docs'
PATH = 'library'

# can be useful in development, but set to False when you're ready to publish
# RELATIVE_URLS = True
RELATIVE_URLS = False

STORK_INPUT_OPTIONS = {
    "html_selector": "nobr",
    # "url_prefix" : ""
    "url_prefix": "/bibliographer"
}

LOAD_CONTENT_CACHE = False
# CONTENT_CACHING_LAYER = 'generator'

# PORT = 8808
# BIND = "192.168.0.15"

GITHUB_URL = 'https://github.com/lclem/bibliographer'
GITHUB_VIEW_URL = GITHUB_URL + '/tree/main'
GITHUB_BLOB_URL = GITHUB_URL + '/blob/main'
GITHUB_EDIT_URL = GITHUB_URL + '/edit/main'
REVERSE_CATEGORY_ORDER = True
LOCALE = 'en_US.UTF-8'
DEFAULT_PAGINATION = 8
DEFAULT_DATE = (2012, 3, 2, 14, 1, 1)

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# this gives some errors such as
# File name too long:      __init__.py:666
# '/home/ubuntu/_work/bibliographer/bibliograp                
# her/docs/feeds/tags/computational-complexity                
# -cscc-algebraic-geometry-mathag-group-theory                
# -mathgr-representation-theory-mathrt-quantum                
# -physics-quant-ph-fos-computer-information-s                
# ciences-fos-computer-information-sciences-fo                
# s-mathematics-fos-mathematics-fos-physical-s                
# ciences-fos-physical-sciences-f13.atom.xml'       
# TAG_FEED_ATOM = 'feeds/tags/{slug}.atom.xml'

FEED_ALL_RSS = 'feeds/all.rss.xml'
# CATEGORY_FEED_RSS = 'feeds/{slug}.rss.xml'
# TAG_FEED_RSS = "tag/%s/feed"

# STORK_INPUT_OPTIONS = {
#     base_directory: 'output'
# }

TAG_CLOUD_STEPS = 4	#Count of different font sizes in the tag cloud
TAG_CLOUD_MAX_ITEMS = 100	#Maximum number of tags in the cloud
TAG_CLOUD_SORTING = "random"	#Tag cloud ordering scheme. Valid values: random, alphabetically, alphabetically-rev, size, and size-rev
TAG_CLOUD_BADGE = True

MENUITEMS = [
        ('tags', STORK_INPUT_OPTIONS["url_prefix"] + '/tags.html'),
        ('no doi', STORK_INPUT_OPTIONS["url_prefix"] + '/nodoi.html'),
        ('no pdf', STORK_INPUT_OPTIONS["url_prefix"] + '/nopdf.html'),
        ('bad author', STORK_INPUT_OPTIONS["url_prefix"] +'/authors_bad.html'),
        ('add item', STORK_INPUT_OPTIONS["url_prefix"] + '/form.html')
    ]

SLUGIFY_SOURCE = "basename"
DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = True

NEWEST_FIRST_ARCHIVES = True

# path-specific metadata
# EXTRA_PATH_METADATA = {
#     'extra/robots.txt': {'path': 'robots.txt'},
#     }

# static paths will be copied without parsing their contents
STATIC_PATHS = [
    'doi'
    # 'images',
    # 'extra/robots.txt',
    ]

# custom page generated with a jinja2 template
# TEMPLATE_PAGES = {'pages/jinja2_template.html': 'jinja2_template.html'}

# there is no other HTML content
READERS = {'html': None}

# code blocks with line numbers
PYGMENTS_RST_OPTIONS = {'linenos': 'table'}

# ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{slug}/'
# ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{slug}/index.html'

ARTICLE_URL = 'articles/{slug}/'
ARTICLE_SAVE_AS = 'articles/{slug}/index.html'

PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'

# Custom Home page
DIRECT_TEMPLATES = ['index', 'author', 'archives', 'authors_bad', 'nodoi', 'nopdf', 'form', 'tags']
PAGINATED_TEMPLATES = {'index' : 20}
TEMPLATE_PAGES = {'nopdf.html': 'nopdf.html', 'nodoi.html': 'nodoi.html', 'authors.html': 'authors.html', 'authors_bad.html': 'authors_bad.html', 'form.html': 'form.html'}
