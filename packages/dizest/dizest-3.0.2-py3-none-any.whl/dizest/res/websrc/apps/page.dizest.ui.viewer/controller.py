wpid = wiz.request.segment.workflow_id
fid = wiz.request.segment.flow_id

Dizest = wiz.model("dizest/scheduler")

user_id = wiz.session.get("id")

if wpid == 'develop':
    db = wiz.model("dizest/db").use("app")
    app = db.get(id=fid)
    if app['user_id'] != user_id:
        wiz.response.status(401)
    dizest = Dizest.test(fid)
    flow = dizest.flow(fid)
else:
    db = wiz.model("dizest/db").use("workflow")
    workflow = db.get(id=wpid)
    if workflow['user_id'] != user_id:
        wiz.response.status(401)
    dizest = Dizest(wpid, workflow)
    flow = dizest.flow(fid)

kwargs['workflow_id'] = wpid
kwargs['flow_id'] = fid
kwargs['render'] = flow.render()