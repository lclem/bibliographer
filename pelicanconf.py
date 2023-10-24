AUTHOR = 'LC'
SITENAME = "bibliographer"
SITESUBTITLE = 'test'
SITEURL = 'http://'
TIMEZONE = "Europe/Paris"

THEME = 'themes/bootstrap2'
OUTPUT_PATH = 'output'
PATH = 'library'

# can be useful in development, but set to False when you're ready to publish
RELATIVE_URLS = True

GITHUB_URL = 'http://github.com/lclem/bibliographer'
REVERSE_CATEGORY_ORDER = True
LOCALE = "C"
DEFAULT_PAGINATION = 4
DEFAULT_DATE = (2012, 3, 2, 14, 1, 1)

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# FEED_ALL_RSS = 'feeds/all.rss.xml'
# CATEGORY_FEED_RSS = 'feeds/{slug}.rss.xml'

# STORK_INPUT_OPTIONS = {
#     base_directory: 'output'
# }

# LINKS = (('Biologeek', 'http://biologeek.org'),
#          ('Filyb', "http://filyb.info/"),
#          ('Libert-fr', "http://www.libert-fr.com"),
#          ('Zubin Mithra', "http://zubin71.wordpress.com/"),)

# SOCIAL = (('twitter', 'http://twitter.com/ametaireau'),
#           ('lastfm', 'http://lastfm.com/user/akounet'),
#           ('github', 'http://github.com/ametaireau'),)

# global metadata to all the contents
# DEFAULT_METADATA = {'yeah': 'it is'}

# path-specific metadata
EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    }

# static paths will be copied without parsing their contents
STATIC_PATHS = [
    'images',
    'extra/robots.txt',
    ]

# custom page generated with a jinja2 template
TEMPLATE_PAGES = {'pages/jinja2_template.html': 'jinja2_template.html'}

# there is no other HTML content
READERS = {'html': None}

# code blocks with line numbers
PYGMENTS_RST_OPTIONS = {'linenos': 'table'}

# foobar will not be used, because it's not in caps. All configuration keys
# have to be in caps
foobar = "barbaz"

ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{slug}/index.html'

# Custom Home page
DIRECT_TEMPLATES = (('index', 'tags', 'categories', 'archives'))
PAGINATED_DIRECT_TEMPLATES = (('articles',))
TEMPLATE_PAGES = {'home.html': 'index.html',}

# MARKDOWN = {
#     'extension_configs': {
#         'markdown.extensions.codehilite': {'css_class': 'highlight'},
#         'markdown.extensions.extra': {},
#         'markdown.extensions.meta': {},
#     },
#     'output_format': 'html5',
# }