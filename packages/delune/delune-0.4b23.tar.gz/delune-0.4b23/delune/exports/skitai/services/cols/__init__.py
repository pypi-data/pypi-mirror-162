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

def __umounted__ (context, app, opts):
    delune.shutdown ()

def __setup__ (context, app, opts):
    app.mount ("/", collection, document)

    app.config.numthreads = context.numthreads
    app.config.plock = context.get_lock (__name__)

    delune.configure (app.config.numthreads, context.logger.get ("app"), 16384, 128)

    @app.before_request
    def before_request (context):
        if context.request.args.get ('alias') and not (context.request.routed.__name__ == "collection" and context.request.method == "POST"):
            alias = context.request.args.get ('alias')
            if not delune.get (alias):
                return context.response.Fault ("404 Not Found", 40401, "resource %s not exist" % alias)

    @app.maintain (1, threading = False)
    def maintain_collections (context, now, count):
        if not os.path.exists (dpath.getdir ("config")):
            return
        configs = os.listdir (dpath.getdir ("config"))
        for alias in configs:
            if os.path.getmtime (dpath.getdir ("config", alias)) <= app.g [delune.SIG_UPD]:
                continue
            # force reload if config is changed
            delune.close (alias)
            dpath.load_data (alias, app.config.numthreads, app.config.plock)
            context.setlu (delune.SIG_UPD)
            app.emit ('delune:reload', alias)

        if context.getlu (delune.SIG_UPD) <= app.g.get (delune.SIG_UPD):
            return

        context.log ('collection changed, maintern ({}th)...' .format (count))
        for alias in configs:
            if alias [0] in "#-" and delune.get (alias [1:]):
                delune.close (alias [1:])
                app.emit ('delune:close', alias)
            elif not delune.get (alias):
                dpath.load_data (alias, app.config.numthreads, app.config.plock)
                app.emit ('delune:load', alias)

        app.g.set (delune.SIG_UPD, context.getlu (delune.SIG_UPD))

    @app.permission_check_handler
    def permission_check_handler (context, perms):
        raddr = context.request.get_remote_addr ()
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
        if otp_key and context.verify_otp (context.request.get_header ('x-opt'), otp_key):
            return

        raise context.HttpError ("403 Permission Denied")


def __mount__ (context, app, opts):
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
    def collections (context, alias = None, side_effect = ""):
        return context.API (
            collections = list (delune.status ().keys ()),
            mounted_dir = "@" + app.config.resource_dir.replace (context.env.get ("HOME", ""), ""),
            n_threads = app.config.numthreads
        )


