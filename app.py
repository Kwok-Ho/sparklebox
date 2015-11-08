import tornado.httpserver
import tornado.ioloop
import tornado.web
import os
import json
import ipaddress
import functools
import subprocess
from collections import namedtuple

import tl_models
import dispatch
import endpoints
import enums
import starlight
import analytics
from starlight import private_data_path, cached_keyed_db

version_t = namedtuple("version_t", ["git_ref", "masters_version"])

def executable(name, *args):
    for p in os.getenv("PATH").split(":"):
        maybe_exec = os.path.join(p, name)
        if os.path.exists(maybe_exec):
            which = maybe_exec
            break
    else:
        return None

    try:
        return subprocess.check_output((which,) + args).decode("utf8").strip()
    except subprocess.CalledProcessError:
        return None

git = functools.partial(executable, "git")

def get_ssdb_version():
    gr = git("rev-list", "-n", "1", "HEAD")
    if not gr:
        gr = os.environ.get("DEP_VERSION", "???")

    with open(os.path.join("_data", "private", "masters_version.txt"), "r") as mv_f:
        masters_version = mv_f.read().strip()

    return version_t(gr, masters_version)


def early_init():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if os.environ.get("CRED_FILE", ""):
        with open(os.environ.get("CRED_FILE"), "r") as f:
            for k, v in json.load(f)["CONFIG"]["CONFIG_VARS"].items():
                os.environ[k] = v

    if os.environ.get("DEV", ""):
        # load template from disk every time it's rendered.
        # helpful for development, but is slow.
        def _swizzle_BaseLoader_load(self, name, parent_path=None):
            name = self.resolve_path(name, parent_path=parent_path)
            return self._create_template(name)

        def _swizzle_StaticFileHandler_should_return_304(self):
            return 0
        tornado.template.BaseLoader.load = _swizzle_BaseLoader_load
        tornado.web.StaticFileHandler.should_return_304 = _swizzle_StaticFileHandler_should_return_304
    elif not os.environ.get("DISABLE_HTTPS_ENFORCEMENT", ""):
        # production mode: force https usage due to local storage issues
        # also we don't want the NSA knowing you play chinese cartoon games
        def _swizzle_RequestHandler_prepare(self):
            if self.request.protocol != "https":
                self.redirect(
                    "https://{0}{1}".format(self.request.host, self.request.uri))
        tornado.web.RequestHandler.prepare = _swizzle_RequestHandler_prepare

    if os.environ.get("BEHIND_CLOUDFLARE") == "1":
        cloudflare_ranges = []

        with open("cloudflare.txt", "r") as cf:
            for line in cf:
                cloudflare_ranges.append(ipaddress.ip_network(line.strip()))

        _super_RequestHandler_prepare = tornado.web.RequestHandler.prepare

        def _swizzle_RequestHandler_prepare(self):
            for net in cloudflare_ranges:
                if ipaddress.ip_address(self.request.remote_ip) in net:
                    if "CF-Connecting-IP" in self.request.headers:
                        self.request.remote_ip = self.request.headers[
                            "CF-Connecting-IP"]
                    break
            _super_RequestHandler_prepare(self)

        tornado.web.RequestHandler.prepare = _swizzle_RequestHandler_prepare


def main():
    early_init()
    in_dev_mode = os.environ.get("DEV")
    image_server = os.environ.get("IMAGE_HOST", "")
    version = get_ssdb_version()
    application = tornado.web.Application(dispatch.ROUTES,
                                          template_path="webui",
                                          static_path="static",
                                          image_host=image_server,
                                          autoreload=1 if in_dev_mode else 0,
                                          is_dev=in_dev_mode,

                                          tle=tl_models.TranslationEngine(cached_keyed_db(
                                              private_data_path("names.csv")), use_satellite=1),
                                          enums=enums,
                                          starlight=starlight,
                                          tlable=endpoints.tlable,
                                          icon=endpoints.icon,
                                          analytics=analytics.Analytics(),
                                          version=version)
    http_server = tornado.httpserver.HTTPServer(application, xheaders=1)

    addr = os.environ.get("ADDRESS", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))

    http_server.listen(port, addr)
    print("Ready.")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()