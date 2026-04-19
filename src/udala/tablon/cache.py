from plone import api
from plone.cachepurging.interfaces import ICachePurgingSettings
from plone.cachepurging.interfaces import IPurger
from plone.cachepurging.utils import getPathsToPurge
from plone.cachepurging.utils import getURLsToPurge
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.globalrequest import getRequest


def purge_urls(urls):  # noqa: C901
    request = getRequest()
    sync = True
    purger = getUtility(IPurger)
    purgeLog = []

    def purge(url):
        if sync:
            status, xcache, xerror = purger.purgeSync(url)

            log = url
            if xcache:
                log += " (X-Cache header: " + xcache + ")"
            if xerror:
                log += " -- " + xerror
            if not str(status).startswith("2"):
                log += " -- WARNING status " + str(status)
            purgeLog.append(log)
        else:
            purger.purgeAsync(url)
            purgeLog.append(url)

    serverURL = request["SERVER_URL"]
    portal = api.portal.get()
    portalPath = portal.getPhysicalPath()
    registry = getUtility(IRegistry)
    try:
        purgingSettings = registry.forInterface(ICachePurgingSettings)
        proxies = purgingSettings.cachingProxies
    except KeyError:
        return []

    for inputURL in urls:
        if not inputURL.startswith(serverURL):  # not in the site
            if "://" in inputURL:  # Full URL?
                purge(inputURL)
            else:  # Path?
                for newURL in getURLsToPurge(inputURL, proxies):
                    purge(newURL)
            continue

        physicalPath = relativePath = None
        try:
            physicalPath = request.physicalPathFromURL(inputURL)
        except ValueError:
            purge(inputURL)
            continue

        if not physicalPath:
            purge(inputURL)
            continue

        relativePath = physicalPath[len(portalPath) :]
        if not relativePath:
            purge(inputURL)
            continue

        obj = portal.unrestrictedTraverse(relativePath, None)
        if obj is None:
            purge(inputURL)
            continue

        for path in getPathsToPurge(obj, request):
            for newURL in getURLsToPurge(path, proxies):
                purge(newURL)

    return purgeLog
