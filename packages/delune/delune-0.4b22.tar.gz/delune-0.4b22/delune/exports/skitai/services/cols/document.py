import delune
import json

def last_modified (alias):
    return delune.get (alias).si.last_updated

def __mount__ (app):
    @app.route ("/<alias>/documents", methods = ["POST", "DELETE", "OPTIONS"])
    @app.permission_required ("index")
    def documents (was, alias, truncate_confirm = "", q = "", lang = "en", analyze = 1, **_data):
        if was.request.method == "DELETE":
            if q:
                delune.get (alias).queue (1, json.dumps ({"query": {'qs': q, 'lang': lang, 'analyze': analyze}}))
                return was.API ("202 Accepted")
            elif truncate_confirm != alias:
                return was.Fault ("400 Bad Request", 'parameter truncate_confirm=(alias name) required', 40003)
            delune.get (alias).queue.truncate ()
            return was.API ("202 Accepted")
        delune.get (alias).queue (0, was.request.body)
        return was.API ("202 Accepted")

    @app.route ("/<alias>/documents/<_id>", methods = ["DELETE", "PUT", "OPTIONS"])
    @app.permission_required ("index")
    def cud (was, alias, _id, nthdoc = 0, **_data):
        delune.get (alias).queue (1, json.dumps ({"query": {'qs': "_id:" + _id}}))
        if was.request.method == "PUT":
            delune.get (alias).queue (0, was.request.body)
        return was.API ("202 Accepted")

    # ------------------------------------------------
    @app.route ("/<alias>/documents/<_id>", methods = ["GET"])
    def get (was, alias, _id, nthdoc = 0):
        return query (was, alias, "_id:" + _id, nth_content = nth_content)

    @app.route ("/<alias>/documents", methods = ["GET", "PUT", "OPTIONS"])
    def query (was, alias, **args):
        q = args.get ("q")
        if not q:
            return was.Fault ("400 Bad Request", 'parameter q required', 40003)

        o = args.get ("offset", 0)
        f = args.get ("limit", 10)
        s = args.get ("sort", "")
        w = args.get ("snippet", 30)
        r = args.get ("partial", "")
        n = args.get ("nth_content", 0)
        l = args.get ("lang", "en")
        a = args.get ("analyze", 1)
        d = args.get ("data", 1)

        pargs = (o, f, s, w, r, n, l, a, d)
        if type (q) is list:
            # put method need not etag
            return was.API ({ eq: delune.query (alias, eq, *pargs, limit = 1) for eq in q })
        r = delune.query (alias, q, *pargs, limit = 1)
        was.response.set_etag ('{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}'.format (
            last_modified (alias), alias, q, *pargs
        ))
        return was.API (r)
