import delune
import os
from ..helpers import dpath
import codecs
import json

def __mount__ (context, app, opts):
    @app.route ("/<alias>", methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    @app.permission_required (["replica", "index"])
    def collection (was, alias, side_effect = "", **_data):
        fn = dpath.getdir ("config", alias)
        if was.request.method == "GET":
            if not delune.get (alias):
                return was.Fault ("404 Not Found", "resource %s not exist" % alias, 40401)
            status = delune.status (alias)
            conf = dpath.getdir ("config", alias)
            if not os.path.isfile (conf):
                return was.Fault ("404 Not Found", "resource not exist", 40401)
            with codecs.open (conf, "r", "utf8") as f:
                colopt = json.loads (f.read ())
                status ['colopt'] = {
                    'data': colopt,
                    'mtime': os.path.getmtime (conf),
                    'size': os.path.getsize (conf),
                    'path': conf
                }
            return was.API (status)

        if was.request.method == "DELETE":
            if not os.path.isfile (fn):
                return was.Fault ("404 Not Found", "resource not exist", 40401)
            a, b = os.path.split (fn)
            if side_effect.find ("data") != -1:
                newfn = os.path.join (a, "-" + b)
            else:
                newfn = os.path.join (a, "#" + b)
            if os.path.isfile (newfn):
                os.remove (newfn)
            os.rename (fn, newfn)
            was.setlu (delune.SIG_UPD)
            if side_effect.find ("now") != -1:
                delune.close (alias)
                app.emit ('delune:delete', alias)
                return was.API ("204 No Content")
            return was.API ("202 Accepted")

        if was.request.method == "POST" and delune.get (alias):
            return was.Fault ("406 Conflict", "resource already exists", 40601)

        elif was.request.method in ("PUT", "PATCH") and not delune.get (alias):
            return was.Fault ("404 Not Found", "resource not exist", 40401)

        if was.request.method == "PATCH":
            with open (fn) as f:
                config = json.load (f)
            data = was.request.JSON
            section = data ["section"]
            for k, v in data ["data"].items ():
                if k not in config [section]:
                    return was.Fault ("400 Bad Request", "{} is not propety of {}".format (k, section), 40001)
                config [section][k] = v
        else:
            config = was.request.JSON

        with open (fn, "w") as f:
            json.dump (config, f)
        was.setlu (delune.SIG_UPD)
        app.emit ('delune:reconfigure', alias)

        if was.request.method == "POST":
            if side_effect == "now":
                dpath.load_data (alias, app.config.numthreads, was.plock)
                app.emit ('delune:create', alias)
                return was.API ("201 Created", **config)
            return was.API ("202 Accepted", **config)

        return was.API (**config)

    # replica -------------------------------------------------------
    @app.route ("/<alias>/config", methods = ["GET"])
    @app.permission_required (["index", "replica"])
    def config (was, alias):
        fn = dpath.getdir ("config", alias)
        return was.response.file (fn, "application/json")

    @app.route ("/<alias>/locks", methods = ["GET"])
    @app.permission_required ("replica")
    def locks (was, alias):
        return was.API ({"locks": delune.get (alias).si.lock.locks ()})

    @app.route ("/<alias>/locks/<name>", methods = ["POST", "DELETE", "OPTIONS"])
    @app.permission_required ("replica")
    def lock (was, alias, name, **_data):
        if was.request.command == "post":
            delune.get (alias).si.lock.lock (name)
            app.emit ('delune:lock', alias, name)
            return was.API ("201 Created")
        delune.get (alias).si.lock.unlock (name)
        app.emit ('delune:unlock', alias, name)
        return was.API ("205 No Content")

    @app.route ("/<alias>/commit", methods = ["POST"])
    @app.permission_required ("index")
    def commit (was, alias):
        delune.get (alias).queue.commit ()
        app.emit ('delune:commit', alias)
        return was.API ("205 No Content")

    @app.route ("/<alias>/rollback", methods = ["POST"])
    @app.permission_required ("index")
    def rollback (was, alias):
        delune.get (alias).queue.rollback ()
        app.emit ('delune:rollback', alias)
        return was.API ("205 No Content")

    # utilities ------------------------------------------
    @app.route ("/<alias>/stem", methods = ["GET", "POST", "OPTIONS"])
    def stem (was, alias, **args):
        q = args.get ("q")
        if not q:
            returnwas.Fault ("400 Bad Request", 'parameter q required', 40003)
        if isinstance (q, str):
            q = q.split (",")
        l = args.get ("lang", 'en')
        return was.API (dict ([(eq, " ".join (delune.stem (alias, eq, l))) for eq in q]))

    @app.route ("/<alias>/analyze", methods = ["GET", "POST", "OPTIONS"])
    def analyze (was, alias, **args):
        q = args.get ("q")
        if not q:
            return was.Fault ("400 Bad Request", 'parameter q required', 40003)
        l = args.get ("lang", 'en')
        return was.API (delune.analyze (alias, q, l))

    # segments ------------------------------------------
    @app.route ("/<alias>/devices/<group>/<fn>", methods = ["GET"])
    @app.permission_required ("replica")
    def getfile (was, alias, group, fn):
        s = delune.status (alias)
        if group == "primary":
            path = os.path.join (s ["indexdirs"][0], fn)
        else:
            path = os.path.join (s ["indexdirs"][0], group, fn)
        return was.response.file (path)

    @app.route ("/<alias>/devices/<group>/segments/<fn>", methods = ["GET"])
    @app.permission_required ("replica")
    def getsegfile (was, alias, group, fn):
        s = delune.status (alias)
        seg = fn.split (".") [0]
        if group == "primary":
            if seg not in s ["segmentsizes"]:
                return was.Fault ("404 Not Found", "resource not exist", 40401)
            path = os.path.join (s ["segmentsizes"][seg][0], fn)
        else:
            path = os.path.join (s ["indexdirs"][0], group, fn)
        return was.response.file (path)

