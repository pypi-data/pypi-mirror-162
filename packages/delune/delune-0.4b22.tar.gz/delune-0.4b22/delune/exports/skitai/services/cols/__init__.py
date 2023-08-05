import delune
from . import collection, document
from ..helpers import dpath
import delune
from rs4 import pathtool
import os
import json
import codecs
import time
import shutil
from ipaddress import IPv4Address, IPv4Network

def __umounted__ (context, app, mntopt):
    delune.shutdown ()

def __setup__ (context, app, mntopt):
    app.mount ("/", collection, document)

    app.config.numthreads = context.numthreads
    app.config.plock = context.get_lock (__name__)

    delune.configure (app.config.numthreads, context.logger.get ("app"), 16384, 128)

    @app.before_request
    def before_request (was):
        if was.request.args.get ('alias') and not (was.request.routed.__name__ == "collection" and was.request.method == "POST"):
            alias = was.request.args.get ('alias')
            if not delune.get (alias):
                return was.response.Fault ("404 Not Found", 40401, "resource %s not exist" % alias)

    @app.maintain (1, threading = False)
    def maintain_collections (was, now, count):
        if not os.path.exists (dpath.getdir ("config")):
            return
        configs = os.listdir (dpath.getdir ("config"))
        for alias in configs:
            if os.path.getmtime (dpath.getdir ("config", alias)) <= app.g [delune.SIG_UPD]:
                continue
            # force reload if config is changed
            delune.close (alias)
            dpath.load_data (alias, app.config.numthreads, app.config.plock)
            was.setlu (delune.SIG_UPD)
            app.emit ('delune:reload', alias)

        if was.getlu (delune.SIG_UPD) <= app.g.get (delune.SIG_UPD):
            return

        was.log ('collection changed, maintern ({}th)...' .format (count))
        for alias in configs:
            if alias [0] in "#-" and delune.get (alias [1:]):
                delune.close (alias [1:])
                app.emit ('delune:close', alias)
            elif not delune.get (alias):
                dpath.load_data (alias, app.config.numthreads, app.config.plock)
                app.emit ('delune:load', alias)

        app.g.set (delune.SIG_UPD, was.getlu (delune.SIG_UPD))

    @app.permission_check_handler
    def permission_check_handler (was, perms):
        raddr = was.request.get_remote_addr ()
        if raddr == "127.0.0.1":
            return

        allowed = app.config.get ("ADMIN_IPS")
        if allowed:
            if '*' in allowed:
                return
            src = IPv4Address (raddr)
            for net in allowed:
                print (net)
                if src in IPv4Network (net):
                    return

        otp_key = app.config.get ("ADMIN_OTP_KEY")
        if otp_key and was.verify_otp (was.request.get_header ('x-opt'), otp_key):
            return

        raise was.Error ("403 Permission Denied")


def __mount__ (context, app, mntopt):
    dpath.RESOURCE_DIR = app.config.resource_dir
    pathtool.mkdir (dpath.getdir ("config"))
    for alias in os.listdir (dpath.getdir ("config")):
        if alias.startswith ("-"): # remove dropped col
            with app.config.plock:
                with codecs.open (dpath.getdir ("config", alias), "r", "utf8") as f:
                    colopt = json.loads (f.read ())
                for d in [dpath.getdir ("collections", dpath.normpath(d)) for d in colopt ['data_dir']]:
                    if os.path.isdir (d):
                        shutil.rmtree (d)
                os.remove (dpath.getdir ("config", alias))
        elif alias.startswith ("#"): # unused col
            continue
        else:
            dpath.load_data (alias, app.config.numthreads, app.config.plock)
    app.g.set (delune.SIG_UPD, time.time ())

    @app.route ("", methods = ["GET"])
    @app.permission_required (["replica", "index"])
    def collections (was, alias = None, side_effect = ""):
        return was.API (
            collections = list (delune.status ().keys ()),
            mounted_dir = "@" + app.config.resource_dir.replace (was.env.get ("HOME", ""), ""),
            n_threads = app.config.numthreads
        )


