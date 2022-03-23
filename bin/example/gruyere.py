<HTML>
    <STYLE>
    SMALL { color: #AAAAFF; font-size: 75% }
    BIG { color: #3333FF; font-size: 150%; font-weight: bold}
    </STYLE><BODY><PRE>
<BIG>gruyere.py</BIG>
<SMALL>  1  </SMALL>#!/usr/bin/env python2.7
<SMALL>  2  </SMALL>
<SMALL>  3  </SMALL>"""Gruyere - a web application with holes.
<SMALL>  4  </SMALL>
<SMALL>  5  </SMALL>Copyright 2017 Google Inc. All rights reserved.
<SMALL>  6  </SMALL>
<SMALL>  7  </SMALL>This code is licensed under the
<SMALL>  8  </SMALL>https://creativecommons.org/licenses/by-nd/3.0/us/
<SMALL>  9  </SMALL>Creative Commons Attribution-No Derivative Works 3.0 United States license.
<SMALL> 10  </SMALL>
<SMALL> 11  </SMALL>DO NOT COPY THIS CODE!
<SMALL> 12  </SMALL>
<SMALL> 13  </SMALL>This application is a small self-contained web application with numerous
<SMALL> 14  </SMALL>security holes. It is provided for use with the Web Application Exploits and
<SMALL> 15  </SMALL>Defenses codelab. You may modify the code for your own use while doing the
<SMALL> 16  </SMALL>codelab but you may not distribute the modified code. Brief excerpts of this
<SMALL> 17  </SMALL>code may be used for educational or instructional purposes provided this
<SMALL> 18  </SMALL>notice is kept intact. By using Gruyere you agree to the Terms of Service
<SMALL> 19  </SMALL>https://www.google.com/intl/en/policies/terms/
<SMALL> 20  </SMALL>"""
<SMALL> 21  </SMALL>
<SMALL> 22  </SMALL>__author__ = 'Bruce Leban'
<SMALL> 23  </SMALL>
<SMALL> 24  </SMALL># system modules
<SMALL> 25  </SMALL>from BaseHTTPServer import BaseHTTPRequestHandler
<SMALL> 26  </SMALL>from BaseHTTPServer import HTTPServer
<SMALL> 27  </SMALL>import cgi
<SMALL> 28  </SMALL>import cPickle
<SMALL> 29  </SMALL>import os
<SMALL> 30  </SMALL>import random
<SMALL> 31  </SMALL>import sys
<SMALL> 32  </SMALL>import threading
<SMALL> 33  </SMALL>import urllib
<SMALL> 34  </SMALL>from urlparse import urlparse
<SMALL> 35  </SMALL>
<SMALL> 36  </SMALL>try:
<SMALL> 37  </SMALL>  sys.dont_write_bytecode = True
<SMALL> 38  </SMALL>except AttributeError:
<SMALL> 39  </SMALL>  pass
<SMALL> 40  </SMALL>
<SMALL> 41  </SMALL># our modules
<SMALL> 42  </SMALL>import data
<SMALL> 43  </SMALL>import gtl
<SMALL> 44  </SMALL>
<SMALL> 45  </SMALL>
<SMALL> 46  </SMALL>DB_FILE = '/stored-data.txt'
<SMALL> 47  </SMALL>SECRET_FILE = '/secret.txt'
<SMALL> 48  </SMALL>
<SMALL> 49  </SMALL>INSTALL_PATH = '.'
<SMALL> 50  </SMALL>RESOURCE_PATH = 'resources'
<SMALL> 51  </SMALL>
<SMALL> 52  </SMALL>SPECIAL_COOKIE = '_cookie'
<SMALL> 53  </SMALL>SPECIAL_PROFILE = '_profile'
<SMALL> 54  </SMALL>SPECIAL_DB = '_db'
<SMALL> 55  </SMALL>SPECIAL_PARAMS = '_params'
<SMALL> 56  </SMALL>SPECIAL_UNIQUE_ID = '_unique_id'
<SMALL> 57  </SMALL>
<SMALL> 58  </SMALL>COOKIE_UID = 'uid'
<SMALL> 59  </SMALL>COOKIE_ADMIN = 'is_admin'
<SMALL> 60  </SMALL>COOKIE_AUTHOR = 'is_author'
<SMALL> 61  </SMALL>
<SMALL> 62  </SMALL>
<SMALL> 63  </SMALL># Set to True to cause the server to exit after processing the current url.
<SMALL> 64  </SMALL>quit_server = False
<SMALL> 65  </SMALL>
<SMALL> 66  </SMALL># A global copy of the database so that _GetDatabase can access it.
<SMALL> 67  </SMALL>stored_data = None
<SMALL> 68  </SMALL>
<SMALL> 69  </SMALL># The HTTPServer object.
<SMALL> 70  </SMALL>http_server = None
<SMALL> 71  </SMALL>
<SMALL> 72  </SMALL># A secret value used to generate hashes to protect cookies from tampering.
<SMALL> 73  </SMALL>cookie_secret = ''
<SMALL> 74  </SMALL>
<SMALL> 75  </SMALL># File extensions of resource files that we recognize.
<SMALL> 76  </SMALL>RESOURCE_CONTENT_TYPES = {
<SMALL> 77  </SMALL>    '.css': 'text/css',
<SMALL> 78  </SMALL>    '.gif': 'image/gif',
<SMALL> 79  </SMALL>    '.htm': 'text/html',
<SMALL> 80  </SMALL>    '.html': 'text/html',
<SMALL> 81  </SMALL>    '.js': 'application/javascript',
<SMALL> 82  </SMALL>    '.jpeg': 'image/jpeg',
<SMALL> 83  </SMALL>    '.jpg': 'image/jpeg',
<SMALL> 84  </SMALL>    '.png': 'image/png',
<SMALL> 85  </SMALL>    '.ico': 'image/x-icon',
<SMALL> 86  </SMALL>    '.text': 'text/plain',
<SMALL> 87  </SMALL>    '.txt': 'text/plain',
<SMALL> 88  </SMALL>}
<SMALL> 89  </SMALL>
<SMALL> 90  </SMALL>
<SMALL> 91  </SMALL>def main():
<SMALL> 92  </SMALL>  _SetWorkingDirectory()
<SMALL> 93  </SMALL>
<SMALL> 94  </SMALL>  global quit_server
<SMALL> 95  </SMALL>  quit_server = False
<SMALL> 96  </SMALL>
<SMALL> 97  </SMALL>  # Normally, Gruyere only accepts connections to/from localhost. If you
<SMALL> 98  </SMALL>  # would like to allow access from other ip addresses, you can change to
<SMALL> 99  </SMALL>  # operate in a less secure mode. Set insecure_mode to True to serve on the
<SMALL>100  </SMALL>  # hostname instead of localhost and add the addresses of the other machines
<SMALL>101  </SMALL>  # to allowed_ips below.
<SMALL>102  </SMALL>
<SMALL>103  </SMALL>  insecure_mode = False
<SMALL>104  </SMALL>
<SMALL>105  </SMALL>  # WARNING! DO NOT CHANGE THE FOLLOWING SECTION OF CODE!
<SMALL>106  </SMALL>
<SMALL>107  </SMALL>  # This application is very exploitable. It takes several precautions to
<SMALL>108  </SMALL>  # limit the risk from a real attacker:
<SMALL>109  </SMALL>  #   (1) Serve requests on localhost so that it will not be accessible
<SMALL>110  </SMALL>  # from other machines.
<SMALL>111  </SMALL>  #   (2) If a request is received from any IP other than localhost, quit.
<SMALL>112  </SMALL>  # (This protection is implemented in do_GET/do_POST.)
<SMALL>113  </SMALL>  #   (3) Inject a random identifier as the first part of the path and
<SMALL>114  </SMALL>  # quit if a request is received without this identifier (except for an
<SMALL>115  </SMALL>  # empty path which redirects and /favicon.ico).
<SMALL>116  </SMALL>  #   (4) Automatically exit after 2 hours (7200 seconds) to mitigate against
<SMALL>117  </SMALL>  # accidentally leaving the server running.
<SMALL>118  </SMALL>
<SMALL>119  </SMALL>  quit_timer = threading.Timer(7200, lambda: _Exit('Timeout'))   # DO NOT CHANGE
<SMALL>120  </SMALL>  quit_timer.start()                                             # DO NOT CHANGE
<SMALL>121  </SMALL>
<SMALL>122  </SMALL>  if insecure_mode:                                              # DO NOT CHANGE
<SMALL>123  </SMALL>    server_name = os.popen('hostname').read().replace('\n', '')  # DO NOT CHANGE
<SMALL>124  </SMALL>  else:                                                          # DO NOT CHANGE
<SMALL>125  </SMALL>    server_name = '127.0.0.1'                                    # DO NOT CHANGE
<SMALL>126  </SMALL>  server_port = 8008                                             # DO NOT CHANGE
<SMALL>127  </SMALL>
<SMALL>128  </SMALL>  # The unique id is created from a CSPRNG.
<SMALL>129  </SMALL>  try:                                                           # DO NOT CHANGE
<SMALL>130  </SMALL>    r = random.SystemRandom()                                    # DO NOT CHANGE
<SMALL>131  </SMALL>  except NotImplementedError:                                    # DO NOT CHANGE
<SMALL>132  </SMALL>    _Exit('Could not obtain a CSPRNG source')                    # DO NOT CHANGE
<SMALL>133  </SMALL>
<SMALL>134  </SMALL>  global server_unique_id                                        # DO NOT CHANGE
<SMALL>135  </SMALL>  server_unique_id = str(r.randint(2**128, 2**(128+1)))          # DO NOT CHANGE
<SMALL>136  </SMALL>
<SMALL>137  </SMALL>  # END WARNING!
<SMALL>138  </SMALL>
<SMALL>139  </SMALL>  global http_server
<SMALL>140  </SMALL>  http_server = HTTPServer((server_name, server_port),
<SMALL>141  </SMALL>                           GruyereRequestHandler)
<SMALL>142  </SMALL>
<SMALL>143  </SMALL>  print &gt;&gt;sys.stderr, '''
<SMALL>144  </SMALL>      Gruyere started...
<SMALL>145  </SMALL>          http://%s:%d/
<SMALL>146  </SMALL>          http://%s:%d/%s/''' % (
<SMALL>147  </SMALL>              server_name, server_port, server_name, server_port,
<SMALL>148  </SMALL>              server_unique_id)
<SMALL>149  </SMALL>
<SMALL>150  </SMALL>  global stored_data
<SMALL>151  </SMALL>  stored_data = _LoadDatabase()
<SMALL>152  </SMALL>
<SMALL>153  </SMALL>  while not quit_server:
<SMALL>154  </SMALL>    try:
<SMALL>155  </SMALL>      http_server.handle_request()
<SMALL>156  </SMALL>      _SaveDatabase(stored_data)
<SMALL>157  </SMALL>    except KeyboardInterrupt:
<SMALL>158  </SMALL>      print &gt;&gt;sys.stderr, '\nReceived KeyboardInterrupt'
<SMALL>159  </SMALL>      quit_server = True
<SMALL>160  </SMALL>
<SMALL>161  </SMALL>  print &gt;&gt;sys.stderr, '\nClosing'
<SMALL>162  </SMALL>  http_server.socket.close()
<SMALL>163  </SMALL>  _Exit('quit_server')
<SMALL>164  </SMALL>
<SMALL>165  </SMALL>
<SMALL>166  </SMALL>def _Exit(reason):
<SMALL>167  </SMALL>  # use os._exit instead of sys.exit because this can't be trapped
<SMALL>168  </SMALL>  print &gt;&gt;sys.stderr, '\nExit: ' + reason
<SMALL>169  </SMALL>  os._exit(0)
<SMALL>170  </SMALL>
<SMALL>171  </SMALL>
<SMALL>172  </SMALL>def _SetWorkingDirectory():
<SMALL>173  </SMALL>  """Set the working directory to the directory containing this file."""
<SMALL>174  </SMALL>  if sys.path[0]:
<SMALL>175  </SMALL>    os.chdir(sys.path[0])
<SMALL>176  </SMALL>
<SMALL>177  </SMALL>
<SMALL>178  </SMALL>def _LoadDatabase():
<SMALL>179  </SMALL>  """Load the database from stored-data.txt.
<SMALL>180  </SMALL>
<SMALL>181  </SMALL>  Returns:
<SMALL>182  </SMALL>    The loaded database.
<SMALL>183  </SMALL>  """
<SMALL>184  </SMALL>
<SMALL>185  </SMALL>  try:
<SMALL>186  </SMALL>    f = _Open(INSTALL_PATH, DB_FILE)
<SMALL>187  </SMALL>    stored_data = cPickle.load(f)
<SMALL>188  </SMALL>    f.close()
<SMALL>189  </SMALL>  except (IOError, ValueError):
<SMALL>190  </SMALL>    _Log('Couldn\'t load data; expected the first time Gruyere is run')
<SMALL>191  </SMALL>    stored_data = None
<SMALL>192  </SMALL>
<SMALL>193  </SMALL>  f = _Open(INSTALL_PATH, SECRET_FILE)
<SMALL>194  </SMALL>  global cookie_secret
<SMALL>195  </SMALL>  cookie_secret = f.readline()
<SMALL>196  </SMALL>  f.close()
<SMALL>197  </SMALL>
<SMALL>198  </SMALL>  return stored_data
<SMALL>199  </SMALL>
<SMALL>200  </SMALL>
<SMALL>201  </SMALL>def _SaveDatabase(save_database):
<SMALL>202  </SMALL>  """Save the database to stored-data.txt.
<SMALL>203  </SMALL>
<SMALL>204  </SMALL>  Args:
<SMALL>205  </SMALL>    save_database: the database to save.
<SMALL>206  </SMALL>  """
<SMALL>207  </SMALL>
<SMALL>208  </SMALL>  try:
<SMALL>209  </SMALL>    f = _Open(INSTALL_PATH, DB_FILE, 'w')
<SMALL>210  </SMALL>    cPickle.dump(save_database, f)
<SMALL>211  </SMALL>    f.close()
<SMALL>212  </SMALL>  except IOError:
<SMALL>213  </SMALL>    _Log('Couldn\'t save data')
<SMALL>214  </SMALL>
<SMALL>215  </SMALL>
<SMALL>216  </SMALL>def _Open(location, filename, mode='rb'):
<SMALL>217  </SMALL>  """Open a file from a specific location.
<SMALL>218  </SMALL>
<SMALL>219  </SMALL>  Args:
<SMALL>220  </SMALL>    location: The directory containing the file.
<SMALL>221  </SMALL>    filename: The name of the file.
<SMALL>222  </SMALL>    mode: File mode for open().
<SMALL>223  </SMALL>
<SMALL>224  </SMALL>  Returns:
<SMALL>225  </SMALL>    A file object.
<SMALL>226  </SMALL>  """
<SMALL>227  </SMALL>  return open(location + filename, mode)
<SMALL>228  </SMALL>
<SMALL>229  </SMALL>
<SMALL>230  </SMALL>class GruyereRequestHandler(BaseHTTPRequestHandler):
<SMALL>231  </SMALL>  """Handle a http request."""
<SMALL>232  </SMALL>
<SMALL>233  </SMALL>  # An empty cookie
<SMALL>234  </SMALL>  NULL_COOKIE = {COOKIE_UID: None, COOKIE_ADMIN: False, COOKIE_AUTHOR: False}
<SMALL>235  </SMALL>
<SMALL>236  </SMALL>  # Urls that can only be accessed by administrators.
<SMALL>237  </SMALL>  _PROTECTED_URLS = [
<SMALL>238  </SMALL>      '/quit',
<SMALL>239  </SMALL>      '/reset'
<SMALL>240  </SMALL>  ]
<SMALL>241  </SMALL>
<SMALL>242  </SMALL>  def _GetDatabase(self):
<SMALL>243  </SMALL>    """Gets the database."""
<SMALL>244  </SMALL>    global stored_data
<SMALL>245  </SMALL>    if not stored_data:
<SMALL>246  </SMALL>      stored_data = data.DefaultData()
<SMALL>247  </SMALL>    return stored_data
<SMALL>248  </SMALL>
<SMALL>249  </SMALL>  def _ResetDatabase(self):
<SMALL>250  </SMALL>    """Reset the database."""
<SMALL>251  </SMALL>    # global stored_data
<SMALL>252  </SMALL>    stored_data = data.DefaultData()
<SMALL>253  </SMALL>
<SMALL>254  </SMALL>  def _DoLogin(self, cookie, specials, params):
<SMALL>255  </SMALL>    """Handles the /login url: validates the user and creates a cookie.
<SMALL>256  </SMALL>
<SMALL>257  </SMALL>    Args:
<SMALL>258  </SMALL>      cookie: The cookie for this request.
<SMALL>259  </SMALL>      specials: Other special values for this request.
<SMALL>260  </SMALL>      params: Cgi parameters.
<SMALL>261  </SMALL>    """
<SMALL>262  </SMALL>    database = self._GetDatabase()
<SMALL>263  </SMALL>    message = ''
<SMALL>264  </SMALL>    if 'uid' in params and 'pw' in params:
<SMALL>265  </SMALL>      uid = self._GetParameter(params, 'uid')
<SMALL>266  </SMALL>      if uid in database:
<SMALL>267  </SMALL>        if database[uid]['pw'] == self._GetParameter(params, 'pw'):
<SMALL>268  </SMALL>          (cookie, new_cookie_text) = (
<SMALL>269  </SMALL>              self._CreateCookie('GRUYERE', uid))
<SMALL>270  </SMALL>          self._DoHome(cookie, specials, params, new_cookie_text)
<SMALL>271  </SMALL>          return
<SMALL>272  </SMALL>      message = 'Invalid user name or password.'
<SMALL>273  </SMALL>    # not logged in
<SMALL>274  </SMALL>    specials['_message'] = message
<SMALL>275  </SMALL>    self._SendTemplateResponse('/login.gtl', specials, params)
<SMALL>276  </SMALL>
<SMALL>277  </SMALL>  def _DoLogout(self, cookie, specials, params):
<SMALL>278  </SMALL>    """Handles the /logout url: clears the cookie.
<SMALL>279  </SMALL>
<SMALL>280  </SMALL>    Args:
<SMALL>281  </SMALL>      cookie: The cookie for this request.
<SMALL>282  </SMALL>      specials: Other special values for this request.
<SMALL>283  </SMALL>      params: Cgi parameters.
<SMALL>284  </SMALL>    """
<SMALL>285  </SMALL>    (cookie, new_cookie_text) = (
<SMALL>286  </SMALL>        self._CreateCookie('GRUYERE', None))
<SMALL>287  </SMALL>    self._DoHome(cookie, specials, params, new_cookie_text)
<SMALL>288  </SMALL>
<SMALL>289  </SMALL>  def _Do(self, cookie, specials, params):
<SMALL>290  </SMALL>    """Handles the home page (http://localhost/).
<SMALL>291  </SMALL>
<SMALL>292  </SMALL>    Args:
<SMALL>293  </SMALL>      cookie: The cookie for this request.
<SMALL>294  </SMALL>      specials: Other special values for this request.
<SMALL>295  </SMALL>      params: Cgi parameters.
<SMALL>296  </SMALL>    """
<SMALL>297  </SMALL>    self._DoHome(cookie, specials, params)
<SMALL>298  </SMALL>
<SMALL>299  </SMALL>  def _DoHome(self, cookie, specials, params, new_cookie_text=None):
<SMALL>300  </SMALL>    """Renders the home page.
<SMALL>301  </SMALL>
<SMALL>302  </SMALL>    Args:
<SMALL>303  </SMALL>      cookie: The cookie for this request.
<SMALL>304  </SMALL>      specials: Other special values for this request.
<SMALL>305  </SMALL>      params: Cgi parameters.
<SMALL>306  </SMALL>      new_cookie_text: New cookie.
<SMALL>307  </SMALL>    """
<SMALL>308  </SMALL>    database = self._GetDatabase()
<SMALL>309  </SMALL>    specials[SPECIAL_COOKIE] = cookie
<SMALL>310  </SMALL>    if cookie and cookie.get(COOKIE_UID):
<SMALL>311  </SMALL>      specials[SPECIAL_PROFILE] = database.get(cookie[COOKIE_UID])
<SMALL>312  </SMALL>    else:
<SMALL>313  </SMALL>      specials.pop(SPECIAL_PROFILE, None)
<SMALL>314  </SMALL>    self._SendTemplateResponse(
<SMALL>315  </SMALL>        '/home.gtl', specials, params, new_cookie_text)
<SMALL>316  </SMALL>
<SMALL>317  </SMALL>  def _DoBadUrl(self, path, cookie, specials, params):
<SMALL>318  </SMALL>    """Handles invalid urls: displays an appropriate error message.
<SMALL>319  </SMALL>
<SMALL>320  </SMALL>    Args:
<SMALL>321  </SMALL>      path: The invalid url.
<SMALL>322  </SMALL>      cookie: The cookie for this request.
<SMALL>323  </SMALL>      specials: Other special values for this request.
<SMALL>324  </SMALL>      params: Cgi parameters.
<SMALL>325  </SMALL>    """
<SMALL>326  </SMALL>    self._SendError('Invalid request: %s' % (path,), cookie, specials, params)
<SMALL>327  </SMALL>
<SMALL>328  </SMALL>  def _DoQuitserver(self, cookie, specials, params):
<SMALL>329  </SMALL>    """Handles the /quitserver url for administrators to quit the server.
<SMALL>330  </SMALL>
<SMALL>331  </SMALL>    Args:
<SMALL>332  </SMALL>      cookie: The cookie for this request. (unused)
<SMALL>333  </SMALL>      specials: Other special values for this request. (unused)
<SMALL>334  </SMALL>      params: Cgi parameters. (unused)
<SMALL>335  </SMALL>    """
<SMALL>336  </SMALL>    global quit_server
<SMALL>337  </SMALL>    quit_server = True
<SMALL>338  </SMALL>    self._SendTextResponse('Server quit.', None)
<SMALL>339  </SMALL>
<SMALL>340  </SMALL>  def _AddParameter(self, name, params, data_dict, default=None):
<SMALL>341  </SMALL>    """Transfers a value (with a default) from the parameters to the data."""
<SMALL>342  </SMALL>    if params.get(name):
<SMALL>343  </SMALL>      data_dict[name] = params[name][0]
<SMALL>344  </SMALL>    elif default is not None:
<SMALL>345  </SMALL>      data_dict[name] = default
<SMALL>346  </SMALL>
<SMALL>347  </SMALL>  def _GetParameter(self, params, name, default=None):
<SMALL>348  </SMALL>    """Gets a parameter value with a default."""
<SMALL>349  </SMALL>    if params.get(name):
<SMALL>350  </SMALL>      return params[name][0]
<SMALL>351  </SMALL>    return default
<SMALL>352  </SMALL>
<SMALL>353  </SMALL>  def _GetSnippets(self, cookie, specials, create=False):
<SMALL>354  </SMALL>    """Returns all of the user's snippets."""
<SMALL>355  </SMALL>    database = self._GetDatabase()
<SMALL>356  </SMALL>    try:
<SMALL>357  </SMALL>      profile = database[cookie[COOKIE_UID]]
<SMALL>358  </SMALL>      if create and 'snippets' not in profile:
<SMALL>359  </SMALL>        profile['snippets'] = []
<SMALL>360  </SMALL>      snippets = profile['snippets']
<SMALL>361  </SMALL>    except (KeyError, TypeError):
<SMALL>362  </SMALL>      _Log('Error getting snippets')
<SMALL>363  </SMALL>      return None
<SMALL>364  </SMALL>    return snippets
<SMALL>365  </SMALL>
<SMALL>366  </SMALL>  def _DoNewsnippet2(self, cookie, specials, params):
<SMALL>367  </SMALL>    """Handles the /newsnippet2 url: actually add the snippet.
<SMALL>368  </SMALL>
<SMALL>369  </SMALL>    Args:
<SMALL>370  </SMALL>      cookie: The cookie for this request.
<SMALL>371  </SMALL>      specials: Other special values for this request.
<SMALL>372  </SMALL>      params: Cgi parameters.
<SMALL>373  </SMALL>    """
<SMALL>374  </SMALL>    snippet = self._GetParameter(params, 'snippet')
<SMALL>375  </SMALL>    if not snippet:
<SMALL>376  </SMALL>      self._SendError('No snippet!', cookie, specials, params)
<SMALL>377  </SMALL>    else:
<SMALL>378  </SMALL>      snippets = self._GetSnippets(cookie, specials, True)
<SMALL>379  </SMALL>      if snippets is not None:
<SMALL>380  </SMALL>        snippets.insert(0, snippet)
<SMALL>381  </SMALL>    self._SendRedirect('/snippets.gtl', specials[SPECIAL_UNIQUE_ID])
<SMALL>382  </SMALL>
<SMALL>383  </SMALL>  def _DoDeletesnippet(self, cookie, specials, params):
<SMALL>384  </SMALL>    """Handles the /deletesnippet url: delete the indexed snippet.
<SMALL>385  </SMALL>
<SMALL>386  </SMALL>    Args:
<SMALL>387  </SMALL>      cookie: The cookie for this request.
<SMALL>388  </SMALL>      specials: Other special values for this request.
<SMALL>389  </SMALL>      params: Cgi parameters.
<SMALL>390  </SMALL>    """
<SMALL>391  </SMALL>    index = self._GetParameter(params, 'index')
<SMALL>392  </SMALL>    snippets = self._GetSnippets(cookie, specials)
<SMALL>393  </SMALL>    try:
<SMALL>394  </SMALL>      del snippets[int(index)]
<SMALL>395  </SMALL>    except (IndexError, TypeError, ValueError):
<SMALL>396  </SMALL>      self._SendError(
<SMALL>397  </SMALL>          'Invalid index (%s)' % (index,),
<SMALL>398  </SMALL>          cookie, specials, params)
<SMALL>399  </SMALL>      return
<SMALL>400  </SMALL>    self._SendRedirect('/snippets.gtl', specials[SPECIAL_UNIQUE_ID])
<SMALL>401  </SMALL>
<SMALL>402  </SMALL>  def _DoSaveprofile(self, cookie, specials, params):
<SMALL>403  </SMALL>    """Saves the user's profile.
<SMALL>404  </SMALL>
<SMALL>405  </SMALL>    Args:
<SMALL>406  </SMALL>      cookie: The cookie for this request.
<SMALL>407  </SMALL>      specials: Other special values for this request.
<SMALL>408  </SMALL>      params: Cgi parameters.
<SMALL>409  </SMALL>
<SMALL>410  </SMALL>    If the 'action' cgi parameter is 'new', then this is creating a new user
<SMALL>411  </SMALL>    and it's an error if the user already exists. If action is 'update', then
<SMALL>412  </SMALL>    this is editing an existing user's profile and it's an error if the user
<SMALL>413  </SMALL>    does not exist.
<SMALL>414  </SMALL>    """
<SMALL>415  </SMALL>
<SMALL>416  </SMALL>    # build new profile
<SMALL>417  </SMALL>    profile_data = {}
<SMALL>418  </SMALL>    uid = self._GetParameter(params, 'uid', cookie[COOKIE_UID])
<SMALL>419  </SMALL>    newpw = self._GetParameter(params, 'pw')
<SMALL>420  </SMALL>    self._AddParameter('name', params, profile_data, uid)
<SMALL>421  </SMALL>    self._AddParameter('pw', params, profile_data)
<SMALL>422  </SMALL>    self._AddParameter('is_author', params, profile_data)
<SMALL>423  </SMALL>    self._AddParameter('is_admin', params, profile_data)
<SMALL>424  </SMALL>    self._AddParameter('private_snippet', params, profile_data)
<SMALL>425  </SMALL>    self._AddParameter('icon', params, profile_data)
<SMALL>426  </SMALL>    self._AddParameter('web_site', params, profile_data)
<SMALL>427  </SMALL>    self._AddParameter('color', params, profile_data)
<SMALL>428  </SMALL>
<SMALL>429  </SMALL>    # Each case below has to set either error or redirect
<SMALL>430  </SMALL>    database = self._GetDatabase()
<SMALL>431  </SMALL>    message = None
<SMALL>432  </SMALL>    new_cookie_text = None
<SMALL>433  </SMALL>    action = self._GetParameter(params, 'action')
<SMALL>434  </SMALL>    if action == 'new':
<SMALL>435  </SMALL>      if uid in database:
<SMALL>436  </SMALL>        message = 'User already exists.'
<SMALL>437  </SMALL>      else:
<SMALL>438  </SMALL>        profile_data['pw'] = newpw
<SMALL>439  </SMALL>        database[uid] = profile_data
<SMALL>440  </SMALL>        (cookie, new_cookie_text) = self._CreateCookie('GRUYERE', uid)
<SMALL>441  </SMALL>        message = 'Account created.'  # error message can also indicates success
<SMALL>442  </SMALL>    elif action == 'update':
<SMALL>443  </SMALL>      if uid not in database:
<SMALL>444  </SMALL>        message = 'User does not exist.'
<SMALL>445  </SMALL>      elif (newpw and database[uid]['pw'] != self._GetParameter(params, 'oldpw')
<SMALL>446  </SMALL>            and not cookie.get(COOKIE_ADMIN)):
<SMALL>447  </SMALL>        # must be admin or supply old pw to change password
<SMALL>448  </SMALL>        message = 'Incorrect password.'
<SMALL>449  </SMALL>      else:
<SMALL>450  </SMALL>        if newpw:
<SMALL>451  </SMALL>          profile_data['pw'] = newpw
<SMALL>452  </SMALL>        database[uid].update(profile_data)
<SMALL>453  </SMALL>        redirect = '/'
<SMALL>454  </SMALL>    else:
<SMALL>455  </SMALL>      message = 'Invalid request'
<SMALL>456  </SMALL>    _Log('SetProfile(%s, %s): %s' %(str(uid), str(action), str(message)))
<SMALL>457  </SMALL>    if message:
<SMALL>458  </SMALL>      self._SendError(message, cookie, specials, params, new_cookie_text)
<SMALL>459  </SMALL>    else:
<SMALL>460  </SMALL>      self._SendRedirect(redirect, specials[SPECIAL_UNIQUE_ID])
<SMALL>461  </SMALL>
<SMALL>462  </SMALL>  def _SendHtmlResponse(self, html, new_cookie_text=None):
<SMALL>463  </SMALL>    """Sends the provided html response with appropriate headers.
<SMALL>464  </SMALL>
<SMALL>465  </SMALL>    Args:
<SMALL>466  </SMALL>      html: The response.
<SMALL>467  </SMALL>      new_cookie_text: New cookie to set.
<SMALL>468  </SMALL>    """
<SMALL>469  </SMALL>    self.send_response(200)
<SMALL>470  </SMALL>    self.send_header('Content-type', 'text/html')
<SMALL>471  </SMALL>    self.send_header('Pragma', 'no-cache')
<SMALL>472  </SMALL>    if new_cookie_text:
<SMALL>473  </SMALL>      self.send_header('Set-Cookie', new_cookie_text)
<SMALL>474  </SMALL>    self.send_header('X-XSS-Protection', '0')
<SMALL>475  </SMALL>    self.end_headers()
<SMALL>476  </SMALL>    self.wfile.write(html)
<SMALL>477  </SMALL>
<SMALL>478  </SMALL>  def _SendTextResponse(self, text, new_cookie_text=None):
<SMALL>479  </SMALL>    """Sends a verbatim text response."""
<SMALL>480  </SMALL>
<SMALL>481  </SMALL>    self._SendHtmlResponse('&lt;pre&gt;' + cgi.escape(text) + '&lt;/pre&gt;',
<SMALL>482  </SMALL>                           new_cookie_text)
<SMALL>483  </SMALL>
<SMALL>484  </SMALL>  def _SendTemplateResponse(self, filename, specials, params,
<SMALL>485  </SMALL>                            new_cookie_text=None):
<SMALL>486  </SMALL>    """Sends a response using a gtl template.
<SMALL>487  </SMALL>
<SMALL>488  </SMALL>    Args:
<SMALL>489  </SMALL>      filename: The template file.
<SMALL>490  </SMALL>      specials: Other special values for this request.
<SMALL>491  </SMALL>      params: Cgi parameters.
<SMALL>492  </SMALL>      new_cookie_text: New cookie to set.
<SMALL>493  </SMALL>    """
<SMALL>494  </SMALL>    f = None
<SMALL>495  </SMALL>    try:
<SMALL>496  </SMALL>      f = _Open(RESOURCE_PATH, filename)
<SMALL>497  </SMALL>      template = f.read()
<SMALL>498  </SMALL>    finally:
<SMALL>499  </SMALL>      if f: f.close()
<SMALL>500  </SMALL>    self._SendHtmlResponse(
<SMALL>501  </SMALL>        gtl.ExpandTemplate(template, specials, params),
<SMALL>502  </SMALL>        new_cookie_text)
<SMALL>503  </SMALL>
<SMALL>504  </SMALL>  def _SendFileResponse(self, filename, cookie, specials, params):
<SMALL>505  </SMALL>    """Sends the contents of a file.
<SMALL>506  </SMALL>
<SMALL>507  </SMALL>    Args:
<SMALL>508  </SMALL>      filename: The file to send.
<SMALL>509  </SMALL>      cookie: The cookie for this request.
<SMALL>510  </SMALL>      specials: Other special values for this request.
<SMALL>511  </SMALL>      params: Cgi parameters.
<SMALL>512  </SMALL>    """
<SMALL>513  </SMALL>    content_type = None
<SMALL>514  </SMALL>    if filename.endswith('.gtl'):
<SMALL>515  </SMALL>      self._SendTemplateResponse(filename, specials, params)
<SMALL>516  </SMALL>      return
<SMALL>517  </SMALL>
<SMALL>518  </SMALL>    name_only = filename[filename.rfind('/'):]
<SMALL>519  </SMALL>    extension = name_only[name_only.rfind('.'):]
<SMALL>520  </SMALL>    if '.' not in extension:
<SMALL>521  </SMALL>      content_type = 'text/plain'
<SMALL>522  </SMALL>    elif extension in RESOURCE_CONTENT_TYPES:
<SMALL>523  </SMALL>      content_type = RESOURCE_CONTENT_TYPES[extension]
<SMALL>524  </SMALL>    else:
<SMALL>525  </SMALL>      self._SendError(
<SMALL>526  </SMALL>          'Unrecognized file type (%s).' % (filename,),
<SMALL>527  </SMALL>          cookie, specials, params)
<SMALL>528  </SMALL>      return
<SMALL>529  </SMALL>    f = None
<SMALL>530  </SMALL>    try:
<SMALL>531  </SMALL>      f = _Open(RESOURCE_PATH, filename, 'rb')
<SMALL>532  </SMALL>      self.send_response(200)
<SMALL>533  </SMALL>      self.send_header('Content-type', content_type)
<SMALL>534  </SMALL>      # Always cache static resources
<SMALL>535  </SMALL>      self.send_header('Cache-control', 'public, max-age=7200')
<SMALL>536  </SMALL>      self.send_header('X-XSS-Protection', '0')
<SMALL>537  </SMALL>      self.end_headers()
<SMALL>538  </SMALL>      self.wfile.write(f.read())
<SMALL>539  </SMALL>    finally:
<SMALL>540  </SMALL>      if f: f.close()
<SMALL>541  </SMALL>
<SMALL>542  </SMALL>  def _SendError(self, message, cookie, specials, params, new_cookie_text=None):
<SMALL>543  </SMALL>    """Sends an error message (using the error.gtl template).
<SMALL>544  </SMALL>
<SMALL>545  </SMALL>    Args:
<SMALL>546  </SMALL>      message: The error to display.
<SMALL>547  </SMALL>      cookie: The cookie for this request. (unused)
<SMALL>548  </SMALL>      specials: Other special values for this request.
<SMALL>549  </SMALL>      params: Cgi parameters.
<SMALL>550  </SMALL>      new_cookie_text: New cookie to set.
<SMALL>551  </SMALL>    """
<SMALL>552  </SMALL>    specials['_message'] = message
<SMALL>553  </SMALL>    self._SendTemplateResponse(
<SMALL>554  </SMALL>        '/error.gtl', specials, params, new_cookie_text)
<SMALL>555  </SMALL>
<SMALL>556  </SMALL>  def _CreateCookie(self, cookie_name, uid):
<SMALL>557  </SMALL>    """Creates a cookie for this user.
<SMALL>558  </SMALL>
<SMALL>559  </SMALL>    Args:
<SMALL>560  </SMALL>      cookie_name: Cookie to create.
<SMALL>561  </SMALL>      uid: The user.
<SMALL>562  </SMALL>
<SMALL>563  </SMALL>    Returns:
<SMALL>564  </SMALL>      (cookie, new_cookie_text).
<SMALL>565  </SMALL>
<SMALL>566  </SMALL>    The cookie contains all the information we need to know about
<SMALL>567  </SMALL>    the user for normal operations, including whether or not the user
<SMALL>568  </SMALL>    should have access to the authoring pages or the admin pages.
<SMALL>569  </SMALL>    The cookie is signed with a hash function.
<SMALL>570  </SMALL>    """
<SMALL>571  </SMALL>    if uid is None:
<SMALL>572  </SMALL>      return (self.NULL_COOKIE, cookie_name + '=; path=/')
<SMALL>573  </SMALL>    database = self._GetDatabase()
<SMALL>574  </SMALL>    profile = database[uid]
<SMALL>575  </SMALL>    if profile.get('is_author', False):
<SMALL>576  </SMALL>      is_author = 'author'
<SMALL>577  </SMALL>    else:
<SMALL>578  </SMALL>      is_author = ''
<SMALL>579  </SMALL>    if profile.get('is_admin', False):
<SMALL>580  </SMALL>      is_admin = 'admin'
<SMALL>581  </SMALL>    else:
<SMALL>582  </SMALL>      is_admin = ''
<SMALL>583  </SMALL>
<SMALL>584  </SMALL>    c = {COOKIE_UID: uid, COOKIE_ADMIN: is_admin, COOKIE_AUTHOR: is_author}
<SMALL>585  </SMALL>    c_data = '%s|%s|%s' % (uid, is_admin, is_author)
<SMALL>586  </SMALL>
<SMALL>587  </SMALL>    # global cookie_secret; only use positive hash values
<SMALL>588  </SMALL>    h_data = str(hash(cookie_secret + c_data) &amp; 0x7FFFFFF)
<SMALL>589  </SMALL>    c_text = '%s=%s|%s; path=/' % (cookie_name, h_data, c_data)
<SMALL>590  </SMALL>    return (c, c_text)
<SMALL>591  </SMALL>
<SMALL>592  </SMALL>  def _GetCookie(self, cookie_name):
<SMALL>593  </SMALL>    """Reads, verifies and parses the cookie.
<SMALL>594  </SMALL>
<SMALL>595  </SMALL>    Args:
<SMALL>596  </SMALL>      cookie_name: The cookie to get.
<SMALL>597  </SMALL>
<SMALL>598  </SMALL>    Returns:
<SMALL>599  </SMALL>      a dict containing user, is_admin, and is_author if the cookie
<SMALL>600  </SMALL>      is present and valid. Otherwise, None.
<SMALL>601  </SMALL>    """
<SMALL>602  </SMALL>    cookies = self.headers.get('Cookie')
<SMALL>603  </SMALL>    if isinstance(cookies, str):
<SMALL>604  </SMALL>      for c in cookies.split(';'):
<SMALL>605  </SMALL>        matched_cookie = self._MatchCookie(cookie_name, c)
<SMALL>606  </SMALL>        if matched_cookie:
<SMALL>607  </SMALL>          return self._ParseCookie(matched_cookie)
<SMALL>608  </SMALL>    return self.NULL_COOKIE
<SMALL>609  </SMALL>
<SMALL>610  </SMALL>  def _MatchCookie(self, cookie_name, cookie):
<SMALL>611  </SMALL>    """Matches the cookie.
<SMALL>612  </SMALL>
<SMALL>613  </SMALL>    Args:
<SMALL>614  </SMALL>      cookie_name: The name of the cookie.
<SMALL>615  </SMALL>      cookie: The full cookie (name=value).
<SMALL>616  </SMALL>
<SMALL>617  </SMALL>    Returns:
<SMALL>618  </SMALL>      The cookie if it matches or None if it doesn't match.
<SMALL>619  </SMALL>    """
<SMALL>620  </SMALL>    try:
<SMALL>621  </SMALL>      (cn, cd) = cookie.strip().split('=', 1)
<SMALL>622  </SMALL>      if cn != cookie_name:
<SMALL>623  </SMALL>        return None
<SMALL>624  </SMALL>    except (IndexError, ValueError):
<SMALL>625  </SMALL>      return None
<SMALL>626  </SMALL>    return cd
<SMALL>627  </SMALL>
<SMALL>628  </SMALL>  def _ParseCookie(self, cookie):
<SMALL>629  </SMALL>    """Parses the cookie and returns NULL_COOKIE if it's invalid.
<SMALL>630  </SMALL>
<SMALL>631  </SMALL>    Args:
<SMALL>632  </SMALL>      cookie: The text of the cookie.
<SMALL>633  </SMALL>
<SMALL>634  </SMALL>    Returns:
<SMALL>635  </SMALL>      A map containing the values in the cookie.
<SMALL>636  </SMALL>    """
<SMALL>637  </SMALL>    try:
<SMALL>638  </SMALL>      (hashed, cookie_data) = cookie.split('|', 1)
<SMALL>639  </SMALL>      # global cookie_secret
<SMALL>640  </SMALL>      if hashed != str(hash(cookie_secret + cookie_data) &amp; 0x7FFFFFF):
<SMALL>641  </SMALL>        return self.NULL_COOKIE
<SMALL>642  </SMALL>      values = cookie_data.split('|')
<SMALL>643  </SMALL>      return {
<SMALL>644  </SMALL>          COOKIE_UID: values[0],
<SMALL>645  </SMALL>          COOKIE_ADMIN: values[1] == 'admin',
<SMALL>646  </SMALL>          COOKIE_AUTHOR: values[2] == 'author',
<SMALL>647  </SMALL>      }
<SMALL>648  </SMALL>    except (IndexError, ValueError):
<SMALL>649  </SMALL>      return self.NULL_COOKIE
<SMALL>650  </SMALL>
<SMALL>651  </SMALL>  def _DoReset(self, cookie, specials, params):  # debug only; resets this db
<SMALL>652  </SMALL>    """Handles the /reset url for administrators to reset the database.
<SMALL>653  </SMALL>
<SMALL>654  </SMALL>    Args:
<SMALL>655  </SMALL>      cookie: The cookie for this request. (unused)
<SMALL>656  </SMALL>      specials: Other special values for this request. (unused)
<SMALL>657  </SMALL>      params: Cgi parameters. (unused)
<SMALL>658  </SMALL>    """
<SMALL>659  </SMALL>    self._ResetDatabase()
<SMALL>660  </SMALL>    self._SendTextResponse('Server reset to default values...', None)
<SMALL>661  </SMALL>
<SMALL>662  </SMALL>  def _DoUpload2(self, cookie, specials, params):
<SMALL>663  </SMALL>    """Handles the /upload2 url: finish the upload and save the file.
<SMALL>664  </SMALL>
<SMALL>665  </SMALL>    Args:
<SMALL>666  </SMALL>      cookie: The cookie for this request.
<SMALL>667  </SMALL>      specials: Other special values for this request.
<SMALL>668  </SMALL>      params: Cgi parameters. (unused)
<SMALL>669  </SMALL>    """
<SMALL>670  </SMALL>    (filename, file_data) = self._ExtractFileFromRequest()
<SMALL>671  </SMALL>    directory = self._MakeUserDirectory(cookie[COOKIE_UID])
<SMALL>672  </SMALL>
<SMALL>673  </SMALL>    message = None
<SMALL>674  </SMALL>    url = None
<SMALL>675  </SMALL>    try:
<SMALL>676  </SMALL>      f = _Open(directory, filename, 'wb')
<SMALL>677  </SMALL>      f.write(file_data)
<SMALL>678  </SMALL>      f.close()
<SMALL>679  </SMALL>      (host, port) = http_server.server_address
<SMALL>680  </SMALL>      url = 'http://%s:%d/%s/%s/%s' % (
<SMALL>681  </SMALL>          host, port, specials[SPECIAL_UNIQUE_ID], cookie[COOKIE_UID], filename)
<SMALL>682  </SMALL>    except IOError, ex:
<SMALL>683  </SMALL>      message = 'Couldn\'t write file %s: %s' % (filename, ex.message)
<SMALL>684  </SMALL>      _Log(message)
<SMALL>685  </SMALL>
<SMALL>686  </SMALL>    specials['_message'] = message
<SMALL>687  </SMALL>    self._SendTemplateResponse(
<SMALL>688  </SMALL>        '/upload2.gtl', specials,
<SMALL>689  </SMALL>        {'url': url})
<SMALL>690  </SMALL>
<SMALL>691  </SMALL>  def _ExtractFileFromRequest(self):
<SMALL>692  </SMALL>    """Extracts the file from an upload request.
<SMALL>693  </SMALL>
<SMALL>694  </SMALL>    Returns:
<SMALL>695  </SMALL>      (filename, file_data)
<SMALL>696  </SMALL>    """
<SMALL>697  </SMALL>    form = cgi.FieldStorage(
<SMALL>698  </SMALL>        fp=self.rfile,
<SMALL>699  </SMALL>        headers=self.headers,
<SMALL>700  </SMALL>        environ={'REQUEST_METHOD': 'POST',
<SMALL>701  </SMALL>                 'CONTENT_TYPE': self.headers.getheader('content-type')})
<SMALL>702  </SMALL>
<SMALL>703  </SMALL>    upload_file = form['upload_file']
<SMALL>704  </SMALL>    file_data = upload_file.file.read()
<SMALL>705  </SMALL>    return (upload_file.filename, file_data)
<SMALL>706  </SMALL>
<SMALL>707  </SMALL>  def _MakeUserDirectory(self, uid):
<SMALL>708  </SMALL>    """Creates a separate directory for each user to avoid upload conflicts.
<SMALL>709  </SMALL>
<SMALL>710  </SMALL>    Args:
<SMALL>711  </SMALL>      uid: The user to create a directory for.
<SMALL>712  </SMALL>
<SMALL>713  </SMALL>    Returns:
<SMALL>714  </SMALL>      The new directory path (/uid/).
<SMALL>715  </SMALL>    """
<SMALL>716  </SMALL>
<SMALL>717  </SMALL>    directory = RESOURCE_PATH + os.sep + str(uid) + os.sep
<SMALL>718  </SMALL>    try:
<SMALL>719  </SMALL>      print 'mkdir: ', directory
<SMALL>720  </SMALL>      os.mkdir(directory)
<SMALL>721  </SMALL>      # throws an exception if directory already exists,
<SMALL>722  </SMALL>      # however exception type varies by platform
<SMALL>723  </SMALL>    except Exception:
<SMALL>724  </SMALL>      pass  # just ignore it if it already exists
<SMALL>725  </SMALL>    return directory
<SMALL>726  </SMALL>
<SMALL>727  </SMALL>  def _SendRedirect(self, url, unique_id):
<SMALL>728  </SMALL>    """Sends a 302 redirect.
<SMALL>729  </SMALL>
<SMALL>730  </SMALL>    Automatically adds the unique_id.
<SMALL>731  </SMALL>
<SMALL>732  </SMALL>    Args:
<SMALL>733  </SMALL>      url: The location to redirect to which must start with '/'.
<SMALL>734  </SMALL>      unique_id: The unique id to include in the url.
<SMALL>735  </SMALL>    """
<SMALL>736  </SMALL>    if not url:
<SMALL>737  </SMALL>      url = '/'
<SMALL>738  </SMALL>    url = '/' + unique_id + url
<SMALL>739  </SMALL>    self.send_response(302)
<SMALL>740  </SMALL>    self.send_header('Location', url)
<SMALL>741  </SMALL>    self.send_header('Pragma', 'no-cache')
<SMALL>742  </SMALL>    self.send_header('Content-type', 'text/html')
<SMALL>743  </SMALL>    self.send_header('X-XSS-Protection', '0')
<SMALL>744  </SMALL>    self.end_headers()
<SMALL>745  </SMALL>    self.wfile.write(
<SMALL>746  </SMALL>        '''&lt;!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML//EN'&gt;
<SMALL>747  </SMALL>        &lt;html&gt;&lt;body&gt;
<SMALL>748  </SMALL>        &lt;title&gt;302 Redirect&lt;/title&gt;
<SMALL>749  </SMALL>        Redirected &lt;a href="%s"&gt;here&lt;/a&gt;
<SMALL>750  </SMALL>        &lt;/body&gt;&lt;/html&gt;'''
<SMALL>751  </SMALL>        % (url,))
<SMALL>752  </SMALL>
<SMALL>753  </SMALL>  def _GetHandlerFunction(self, path):
<SMALL>754  </SMALL>    try:
<SMALL>755  </SMALL>      return getattr(GruyereRequestHandler, '_Do' + path[1:].capitalize())
<SMALL>756  </SMALL>    except AttributeError:
<SMALL>757  </SMALL>      return None
<SMALL>758  </SMALL>
<SMALL>759  </SMALL>  def do_POST(self):  # part of BaseHTTPRequestHandler interface
<SMALL>760  </SMALL>    self.DoGetOrPost()
<SMALL>761  </SMALL>
<SMALL>762  </SMALL>  def do_GET(self):  # part of BaseHTTPRequestHandler interface
<SMALL>763  </SMALL>    self.DoGetOrPost()
<SMALL>764  </SMALL>
<SMALL>765  </SMALL>  def DoGetOrPost(self):
<SMALL>766  </SMALL>    """Validate an http get or post request and call HandleRequest."""
<SMALL>767  </SMALL>
<SMALL>768  </SMALL>    url = urlparse(self.path)
<SMALL>769  </SMALL>    path = url[2]
<SMALL>770  </SMALL>    query = url[4]
<SMALL>771  </SMALL>
<SMALL>772  </SMALL>    # Normally, Gruyere only accepts connections to/from localhost. If you
<SMALL>773  </SMALL>    # would like to allow access from other ip addresses, add the addresses
<SMALL>774  </SMALL>    # of the other machines to allowed_ips and change insecure_mode to True
<SMALL>775  </SMALL>    # above. This makes the application more vulnerable to a real attack so
<SMALL>776  </SMALL>    # you should only add ips of machines you completely control and make
<SMALL>777  </SMALL>    # sure that you are not using them to access any other web pages while
<SMALL>778  </SMALL>    # you are using Gruyere.
<SMALL>779  </SMALL>
<SMALL>780  </SMALL>    allowed_ips = ['127.0.0.1']
<SMALL>781  </SMALL>
<SMALL>782  </SMALL>    # WARNING! DO NOT CHANGE THE FOLLOWING SECTION OF CODE!
<SMALL>783  </SMALL>
<SMALL>784  </SMALL>    # This application is very exploitable. See main for details. What we're
<SMALL>785  </SMALL>    # doing here is (2) and (3) on the previous list:
<SMALL>786  </SMALL>    #   (2) If a request is received from any IP other than localhost, quit.
<SMALL>787  </SMALL>    # An external attacker could still mount an attack on this IP by putting
<SMALL>788  </SMALL>    # an attack on an external web page, e.g., a web page that redirects to
<SMALL>789  </SMALL>    # a vulnerable url on 127.0.0.1 (which is why we use a random number).
<SMALL>790  </SMALL>    #   (3) Inject a random identifier as the first part of the path and
<SMALL>791  </SMALL>    # quit if a request is received without this identifier (except for an
<SMALL>792  </SMALL>    # empty path which redirects and /favicon.ico).
<SMALL>793  </SMALL>
<SMALL>794  </SMALL>    request_ip = self.client_address[0]                      # DO NOT CHANGE
<SMALL>795  </SMALL>    if request_ip not in allowed_ips:                        # DO NOT CHANGE
<SMALL>796  </SMALL>      print &gt;&gt;sys.stderr, (                                  # DO NOT CHANGE
<SMALL>797  </SMALL>          'DANGER! Request from bad ip: ' + request_ip)      # DO NOT CHANGE
<SMALL>798  </SMALL>      _Exit('bad_ip')                                        # DO NOT CHANGE
<SMALL>799  </SMALL>
<SMALL>800  </SMALL>    if (server_unique_id not in path                         # DO NOT CHANGE
<SMALL>801  </SMALL>        and path != '/favicon.ico'):                         # DO NOT CHANGE
<SMALL>802  </SMALL>      if path == '' or path == '/':                          # DO NOT CHANGE
<SMALL>803  </SMALL>        self._SendRedirect('/', server_unique_id)            # DO NOT CHANGE
<SMALL>804  </SMALL>        return                                               # DO NOT CHANGE
<SMALL>805  </SMALL>      else:                                                  # DO NOT CHANGE
<SMALL>806  </SMALL>        print &gt;&gt;sys.stderr, (                                # DO NOT CHANGE
<SMALL>807  </SMALL>            'DANGER! Request without unique id: ' + path)    # DO NOT CHANGE
<SMALL>808  </SMALL>        _Exit('bad_id')                                      # DO NOT CHANGE
<SMALL>809  </SMALL>
<SMALL>810  </SMALL>    path = path.replace('/' + server_unique_id, '', 1)       # DO NOT CHANGE
<SMALL>811  </SMALL>
<SMALL>812  </SMALL>    # END WARNING!
<SMALL>813  </SMALL>
<SMALL>814  </SMALL>    self.HandleRequest(path, query, server_unique_id)
<SMALL>815  </SMALL>
<SMALL>816  </SMALL>  def HandleRequest(self, path, query, unique_id):
<SMALL>817  </SMALL>    """Handles an http request.
<SMALL>818  </SMALL>
<SMALL>819  </SMALL>    Args:
<SMALL>820  </SMALL>      path: The path part of the url, with leading slash.
<SMALL>821  </SMALL>      query: The query part of the url, without leading question mark.
<SMALL>822  </SMALL>      unique_id: The unique id from the url.
<SMALL>823  </SMALL>    """
<SMALL>824  </SMALL>
<SMALL>825  </SMALL>    path = urllib.unquote(path)
<SMALL>826  </SMALL>
<SMALL>827  </SMALL>    if not path:
<SMALL>828  </SMALL>      self._SendRedirect('/', server_unique_id)
<SMALL>829  </SMALL>      return
<SMALL>830  </SMALL>    params = cgi.parse_qs(query)  # url.query
<SMALL>831  </SMALL>    specials = {}
<SMALL>832  </SMALL>    cookie = self._GetCookie('GRUYERE')
<SMALL>833  </SMALL>    database = self._GetDatabase()
<SMALL>834  </SMALL>    specials[SPECIAL_COOKIE] = cookie
<SMALL>835  </SMALL>    specials[SPECIAL_DB] = database
<SMALL>836  </SMALL>    specials[SPECIAL_PROFILE] = database.get(cookie.get(COOKIE_UID))
<SMALL>837  </SMALL>    specials[SPECIAL_PARAMS] = params
<SMALL>838  </SMALL>    specials[SPECIAL_UNIQUE_ID] = unique_id
<SMALL>839  </SMALL>
<SMALL>840  </SMALL>    if path in self._PROTECTED_URLS and not cookie[COOKIE_ADMIN]:
<SMALL>841  </SMALL>      self._SendError('Invalid request', cookie, specials, params)
<SMALL>842  </SMALL>      return
<SMALL>843  </SMALL>
<SMALL>844  </SMALL>    try:
<SMALL>845  </SMALL>      handler = self._GetHandlerFunction(path)
<SMALL>846  </SMALL>      if callable(handler):
<SMALL>847  </SMALL>        (handler)(self, cookie, specials, params)
<SMALL>848  </SMALL>      else:
<SMALL>849  </SMALL>        try:
<SMALL>850  </SMALL>          self._SendFileResponse(path, cookie, specials, params)
<SMALL>851  </SMALL>        except IOError:
<SMALL>852  </SMALL>          self._DoBadUrl(path, cookie, specials, params)
<SMALL>853  </SMALL>    except KeyboardInterrupt:
<SMALL>854  </SMALL>      _Exit('KeyboardInterrupt')
<SMALL>855  </SMALL>
<SMALL>856  </SMALL>
<SMALL>857  </SMALL>def _Log(message):
<SMALL>858  </SMALL>  print &gt;&gt;sys.stderr, message
<SMALL>859  </SMALL>
<SMALL>860  </SMALL>
<SMALL>861  </SMALL>if __name__ == '__main__':
<SMALL>862  </SMALL>  main()
</PRE></BODY></HTML>