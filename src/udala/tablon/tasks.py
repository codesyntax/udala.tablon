from collective.taskqueue2.huey_config import huey_taskqueue
from collective.taskqueue2.huey_logger import LOG
from plone import api
from Testing.makerequest import makerequest
from zope.component.hooks import setSite

import time
import transaction
import Zope2


@huey_taskqueue.task()
def schedule_browser_view_with_traversal(
    view_name: str,
    username: str,
    site_path: str,
    context_path: str,
    params: dict,
    traversal: str = "",
):
    LOG.info(
        f"SCHEDULE {view_name=} {username=} {site_path=}  {context_path=} {params=}"
    )

    ts = time.time()

    t = transaction.manager
    t.begin()
    app = Zope2.app()

    site = app.restrictedTraverse(site_path, None)
    if site is None:
        raise ValueError(f"No site {site_path}")
    setSite(site)
    site = makerequest(site)

    result = None
    with api.env.adopt_user(username=username):
        try:
            try:
                context = site.restrictedTraverse(context_path)
                if context is None:
                    raise ValueError(f"Unknown context {context_path}")
                context = makerequest(context)
                context.REQUEST.form.update(params)

                view = context.restrictedTraverse(view_name, None)
                if view is None:
                    raise ValueError(f"Unknown view {view_name}")

                if traversal:
                    for traversal_item in traversal.split("/"):
                        view = view.publishTraverse(context.REQUEST, traversal_item)

                result = view()
                # LOG.info(view_name, safe_text(result))

                t.commit()
                LOG.info("Transaction committed")
            except Exception as e:
                LOG.exception(e)
                t.abort()
                LOG.error("Transaction aborted", exc_info=True)
                raise
        finally:
            setSite(None)
            app._p_jar.close()

    duration = time.time() - ts
    LOG.debug(f"{duration=}")
    return result
