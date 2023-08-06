import delune
import json

def last_modified (alias):
    return delune.get (alias).si.last_updated

def __mount__ (context, app, opts):
    @app.route ("/<alias>/documents", methods = ["POST", "DELETE", "OPTIONS"])
    @app.permission_required ("index")
    def documents (context, alias, truncate_confirm = "", q = "", lang = "en", analyze = 1, **_data):
        if context.request.method == "DELETE":
            if q:
                delune.get (alias).queue (1, json.dumps ({"query": {'qs': q, 'lang': lang, 'analyze': analyze}}))
                return context.API ("202 Accepted")
            elif truncate_confirm != alias:
                return context.Fault ("400 Bad Request", 'parameter truncate_confirm=(alias name) required', 40003)
            delune.get (alias).queue.truncate ()
            return context.API ("202 Accepted")
        delune.get (alias).queue (0, context.request.body)
        return context.API ("202 Accepted")

    @app.route ("/<alias>/documents/<_id>", methods = ["DELETE", "PUT", "OPTIONS"])
    @app.permission_required ("index")
    def cud (context, alias, _id, nthdoc = 0, **_data):
        delune.get (alias).queue (1, json.dumps ({"query": {'qs': "_id:" + _id}}))
        if context.request.method == "PUT":
            delune.get (alias).queue (0, context.request.body)
        return context.API ("202 Accepted")

    # ------------------------------------------------
    @app.route ("/<alias>/documents/<_id>", methods = ["GET"])
    def get (context, alias, _id, nthdoc = 0):
        return query (context, alias, "_id:" + _id, nth_content = nth_content)

    @app.route ("/<alias>/documents", methods = ["GET", "PUT", "OPTIONS"])
    def query (context, alias, **args):
        q = args.get ("q")
        if not q:
            return context.Fault ("400 Bad Request", 'parameter q required', 40003)

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
            return context.API ({ eq: delune.query (alias, eq, *pargs, limit = 1) for eq in q })
        r = delune.query (alias, q, *pargs, limit = 1)
        context.response.set_etag ('{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}'.format (
            last_modified (alias), alias, q, *pargs
        ))
        return context.API (r)
