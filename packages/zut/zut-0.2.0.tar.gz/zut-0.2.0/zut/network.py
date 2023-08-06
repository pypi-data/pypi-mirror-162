from __future__ import annotations
import logging, os, socket, base64, re, urllib.request, sys
from typing import Callable
if sys.platform == 'win32':
    import win32com.client, win32inetcon, pywintypes
from urllib.parse import unquote, urlparse
from contextlib import closing
from unittest import TestCase

logger = logging.getLogger(__name__)

def check_socket(host, port, timeout=1):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        try:
            returncode = sock.connect_ex((host, port))
            if returncode == 0:
                return True
            else:
                logger.debug("socket connnect_ex returned %d", returncode)
                return False
        except Exception as e:
            logger.debug("socket connnect_ex: %s", e)
            return False


class SimpleProxyHandler(urllib.request.BaseHandler):
    # Inspired from urllib.request.ProxyHandler   
    handler_order = 100 # Proxies must be in front

    def __init__(self, host: str, port: str, username: str = None, password: str | Callable[[], str] = None, scheme: str = "http"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.scheme = scheme


    def finalize(self) -> str:
        # Determine password if this is a callable
        if self.password and isinstance(self.password, Callable):
            self.password = self.password()
        
        # Build proxy url (complete, and safe for logging)
        proxy_url = self.scheme + "://"
        proxy_logurl = self.scheme + "://"

        if self.username:
            proxy_url += self.username
            proxy_logurl += self.username

            if self.password:
                proxy_url += ":" + self.password
                proxy_logurl += ":" + ("*" * len(self.password))

            proxy_url += "@"
            proxy_logurl += "@"

        proxy_url += f"{self.host}:{self.port}"
        proxy_logurl += f"{self.host}:{self.port}"
        logger.debug(f"use proxy for urllib: {proxy_logurl}")

        # Check proxy existency
        if not check_socket(self.host, self.port):
            logger.warning(f"cannot connect to proxy for urllib: {proxy_logurl}")

        # Prepare usefull variables for add_header and set_proxy
        self.hostport = unquote(f"{self.host}:{self.port}")

        if self.username:
            if not self.password:
                raise ValueError(f"missing password for urllib proxy: {proxy_logurl}")
            userpass = '%s:%s' % (unquote(self.username), unquote(self.password))
            self.authorization = "Basic " + base64.b64encode(userpass.encode()).decode("ascii")
        else:
            self.authorization = None

        return proxy_url


    def http_open(self, req):
        if not req.host:
            return None
        
        if urllib.request.proxy_bypass(req.host):
            # NOTE: because Proxy-Authorization header is not encrypted, we must add it ONLY when we're actually talking to the proxy
            return None

        if not hasattr(self, "authorization"):
            self.finalize()

        if self.authorization:
            req.add_header("Proxy-Authorization", self.authorization)
        req.set_proxy(self.hostport, self.scheme)
        return None
    

    def https_open(self, req):
        return self.http_open(req)


def detect_proxy_settings():
    # Detect proxy URL
    if "HTTP_PROXY" in os.environ:
        url = os.environ["HTTP_PROXY"]
    elif "http_proxy" in os.environ:
        url = os.environ["http_proxy"]
    else:
        return None

    # Detect proxy exclusions
    if "NO_PROXY" in os.environ:
        exclusions = os.environ["NO_PROXY"]
    elif "no_proxy" in os.environ:
        exclusions = os.environ["no_proxy"]
    else:
        exclusions = None

    # Parse proxy URL
    o = urlparse(url)
    m = re.match(r"^(?:(?P<username>[^\:]+)(?:\:(?P<password>[^\:]+))?@)?(?P<host>[^@\:]+)\:(?P<port>\d+)$", o.netloc)
    if not m:
        logger.error("cannot register proxy: invalid proxy netloc \"%s\"" % o.netloc)
        return None

    proxy_settings = {}
    proxy_settings["host"] = m.group("host")
    proxy_settings["port"] = int(m.group("port"))
    proxy_settings["username"] = m.group("username")
    proxy_settings["password"] = m.group("password")
    proxy_settings["scheme"] = o.scheme
    proxy_settings["exclusions"] = exclusions
    return proxy_settings            


_proxy_handler: SimpleProxyHandler = None
_proxy_winhttp_hostport: str = None
_proxy_winhttp_exclusions: str = None

def configure_proxy(**proxy_settings):
    """
    Configure proxy for urllib and winhttp (on windows) requests.
    """
    global _proxy_handler, _proxy_winhttp_hostport, _proxy_winhttp_exclusions

    if not proxy_settings:
        proxy_settings = detect_proxy_settings()

    # Stop here if no proxy
    if not proxy_settings:
        return

    host = proxy_settings["host"]
    port = proxy_settings["port"]
    username = proxy_settings.get("username", None)
    password = proxy_settings.get("password", None)
    scheme = proxy_settings.get("scheme", "http")
    exclusions = proxy_settings.get("exclusions", None)

    for key in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"]:
        if key in os.environ:
            del os.environ[key]

    # Ensure no_proxy is specified (must be passed as environment variable for urllib)
    if exclusions:
        if isinstance(exclusions, list):
            exclusions = ",".join(exclusions)
        os.environ["NO_PROXY"] = exclusions

    # Register proxy for urllib
    try:
        _proxy_handler = SimpleProxyHandler(host=host, port=port, username=username, password=password, scheme=scheme)
        opener = urllib.request.build_opener(_proxy_handler)
        urllib.request.install_opener(opener)
    except Exception as e:
        logger.error("cannot register proxy for urllib: %s", e)

    # Prepare for winhttp
    # See: https://docs.microsoft.com/en-us/windows/win32/winhttp/iwinhttprequest-setproxy
    # NOTE: no need to pass credentials, this is handled directly by Windows
    # NOTE: remove CIDR-block exclusions (not supported)
    if sys.platform == 'win32':
        _proxy_winhttp_hostport = f"{host}:{port}"
        if exclusions:
            _proxy_winhttp_exclusions = ",".join([exclusion for exclusion in exclusions.split(",") if not "/" in exclusion])
        else:
            logger.warning("no exclusions for proxy: missing NO_PROXY environment variable?")
            _proxy_winhttp_exclusions = "localhost"


def determine_proxy_url(url: str):
    """
    Determine proxy URL associated to the given target URL.
    """
    o = urlparse(url)
    if urllib.request.proxy_bypass(o.netloc if o.netloc else o.path):
        return None
    if not _proxy_handler:
        return None
    return _proxy_handler.finalize()


TEST_CONNECTIVITY_TIMEOUT = int(os.environ.get("TEST_CONNECTIVITY_TIMEOUT", 2))


def test_urllib_request(case: TestCase, url, msg) -> str:
    try:
        res = urllib.request.urlopen(url, timeout=TEST_CONNECTIVITY_TIMEOUT)
        text = res.read().decode('utf-8')
        return text
    except urllib.error.URLError as e:
        case.fail(f"{msg}: {e.reason}")


if sys.platform == 'win32':
    def create_winhttp_request(timeout=None):
        winhttp_req = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')

        if timeout:
            winhttp_req.SetTimeouts(str(timeout*1000), str(timeout*1000), str(timeout*1000), str(timeout*1000))

        if _proxy_winhttp_hostport:
            HTTPREQUEST_PROXYSETTING_DEFAULT   = 0
            HTTPREQUEST_PROXYSETTING_PRECONFIG = 0
            HTTPREQUEST_PROXYSETTING_DIRECT    = 1
            HTTPREQUEST_PROXYSETTING_PROXY     = 2
            winhttp_req.SetProxy(HTTPREQUEST_PROXYSETTING_PROXY, _proxy_winhttp_hostport, _proxy_winhttp_exclusions)
            winhttp_req.SetAutoLogonPolicy(HTTPREQUEST_PROXYSETTING_DEFAULT)

        return winhttp_req

    def test_winhttp_request(case: TestCase, url, msg) -> str:
        winhttp_req = create_winhttp_request(timeout=TEST_CONNECTIVITY_TIMEOUT)
        winhttp_req.Open('GET', url, False)
        try:
            winhttp_req.Send()
            winhttp_req.WaitForResponse()
            if winhttp_req.Status == 200:
                text = winhttp_req.ResponseText
                return text[0:20]
            else:
                case.fail(f"{msg}: {winhttp_req.Status} {winhttp_req.StatusText}")
        except pywintypes.com_error as e:
            if e.excepinfo[5] + 2**32 & 0xffff == win32inetcon.ERROR_INTERNET_TIMEOUT:
                details = "timed out"
            else:
                details = e.excepinfo[2].strip()
            case.fail(f"{msg}: {details}")


def test_request(case: TestCase, url, expected_regex, label=None) -> str:
    if label is None:
        label = url

    text = test_urllib_request(case, url, msg=f"{label} urllib")
    case.assertRegex(text, expected_regex, msg=f"{label} urllib")

    if sys.platform == "win32":
        test_winhttp_request(case, url, msg=f"{label} winhttp")
        case.assertRegex(text, expected_regex, msg=f"{label} winhttp")
