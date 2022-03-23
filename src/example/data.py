<HTML>
    <STYLE>
    SMALL { color: #AAAAFF; font-size: 75% }
    BIG { color: #3333FF; font-size: 150%; font-weight: bold}
    </STYLE><BODY><PRE>
<BIG>data.py</BIG>
<SMALL>  1  </SMALL>"""Gruyere - Default data for Gruyere, a web application with holes.
<SMALL>  2  </SMALL>
<SMALL>  3  </SMALL>Copyright 2017 Google Inc. All rights reserved.
<SMALL>  4  </SMALL>
<SMALL>  5  </SMALL>This code is licensed under the https://creativecommons.org/licenses/by-nd/3.0/us/
<SMALL>  6  </SMALL>Creative Commons Attribution-No Derivative Works 3.0 United States license.
<SMALL>  7  </SMALL>
<SMALL>  8  </SMALL>DO NOT COPY THIS CODE!
<SMALL>  9  </SMALL>
<SMALL> 10  </SMALL>This application is a small self-contained web application with numerous
<SMALL> 11  </SMALL>security holes. It is provided for use with the Web Application Exploits and
<SMALL> 12  </SMALL>Defenses codelab. You may modify the code for your own use while doing the
<SMALL> 13  </SMALL>codelab but you may not distribute the modified code. Brief excerpts of this
<SMALL> 14  </SMALL>code may be used for educational or instructional purposes provided this
<SMALL> 15  </SMALL>notice is kept intact. By using Gruyere you agree to the Terms of Service
<SMALL> 16  </SMALL>https://www.google.com/intl/en/policies/terms/
<SMALL> 17  </SMALL>"""
<SMALL> 18  </SMALL>
<SMALL> 19  </SMALL>__author__ = 'Bruce Leban'
<SMALL> 20  </SMALL>
<SMALL> 21  </SMALL># system modules
<SMALL> 22  </SMALL>import copy
<SMALL> 23  </SMALL>
<SMALL> 24  </SMALL>DEFAULT_DATA = {
<SMALL> 25  </SMALL>    'administrator': {
<SMALL> 26  </SMALL>        'name': 'Admin',
<SMALL> 27  </SMALL>        'pw': 'secret',
<SMALL> 28  </SMALL>        'is_author': False,
<SMALL> 29  </SMALL>        'is_admin': True,
<SMALL> 30  </SMALL>        'private_snippet': 'My password is secret. Get it?',
<SMALL> 31  </SMALL>        'web_site': 'https://www.google.com/contact/',
<SMALL> 32  </SMALL>    },
<SMALL> 33  </SMALL>    'cheddar': {
<SMALL> 34  </SMALL>        'name': 'Cheddar Mac',
<SMALL> 35  </SMALL>        'pw': 'orange',
<SMALL> 36  </SMALL>        'is_author': True,
<SMALL> 37  </SMALL>        'is_admin': False,
<SMALL> 38  </SMALL>        'private_snippet': 'My SSN is &lt;a href="https://www.google.com/' +
<SMALL> 39  </SMALL>                           'search?q=078-05-1120"&gt;078-05-1120&lt;/a&gt;.',
<SMALL> 40  </SMALL>        'web_site': 'https://images.google.com/?q=cheddar+cheese',
<SMALL> 41  </SMALL>        'color': 'blue',
<SMALL> 42  </SMALL>        'snippets': [
<SMALL> 43  </SMALL>            'Gruyere is the cheesiest application on the web.',
<SMALL> 44  </SMALL>            'I wonder if there are any security holes in this....'
<SMALL> 45  </SMALL>        ],
<SMALL> 46  </SMALL>    },
<SMALL> 47  </SMALL>    'sardo': {
<SMALL> 48  </SMALL>        'name': 'Miss Sardo',
<SMALL> 49  </SMALL>        'pw': 'odras',
<SMALL> 50  </SMALL>        'is_author': True,
<SMALL> 51  </SMALL>        'is_admin': False,
<SMALL> 52  </SMALL>        'private_snippet': 'I hate my brother Romano.',
<SMALL> 53  </SMALL>        'web_site': 'https://www.google.com/search?q="pecorino+sardo"',
<SMALL> 54  </SMALL>        'color': 'red',
<SMALL> 55  </SMALL>        'snippets': [],
<SMALL> 56  </SMALL>    },
<SMALL> 57  </SMALL>    'brie': {
<SMALL> 58  </SMALL>        'name': 'Brie',
<SMALL> 59  </SMALL>        'pw': 'briebrie',
<SMALL> 60  </SMALL>        'is_author': True,
<SMALL> 61  </SMALL>        'is_admin': False,
<SMALL> 62  </SMALL>        'private_snippet': 'I use the same password for all my accounts.',
<SMALL> 63  </SMALL>        'web_site': 'https://news.google.com/news/search?q=brie',
<SMALL> 64  </SMALL>        'color': 'red; text-decoration:underline',
<SMALL> 65  </SMALL>        'snippets': [
<SMALL> 66  </SMALL>            'Brie is the queen of the cheeses&lt;span style=color:red&gt;!!!&lt;/span&gt;'
<SMALL> 67  </SMALL>        ],
<SMALL> 68  </SMALL>    },
<SMALL> 69  </SMALL>}
<SMALL> 70  </SMALL>
<SMALL> 71  </SMALL>
<SMALL> 72  </SMALL>def DefaultData():
<SMALL> 73  </SMALL>  """Provides default data for Gruyere."""
<SMALL> 74  </SMALL>  return copy.deepcopy(DEFAULT_DATA)
</PRE></BODY></HTML>