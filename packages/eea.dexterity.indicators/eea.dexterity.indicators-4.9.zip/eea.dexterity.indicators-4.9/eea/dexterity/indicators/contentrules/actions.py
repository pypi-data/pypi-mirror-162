""" EEAContentTypes actions for plone.app.contentrules
"""

import logging
from time import time

from AccessControl import SpecialUsers
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from plone import api
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapter
from zope.interface import Interface, implementer

logger = logging.getLogger("eea.dexterity.indicators")


class IRetractAndRenameOldVersionAction(Interface):
    """ Retract and rename old version
    """


@implementer(IRetractAndRenameOldVersionAction, IRuleElementData)
class RetractAndRenameOldVersionAction(SimpleItem):
    """ Retract and rename old version action
    """

    element = 'eea.dexterity.indicators.retract_and_rename_old_version'
    summary = (
        "Will retract and rename older version of this Indicator. "
        "Then rename current Indicator (remove copy_of_ from id)"
    )


@implementer(IExecutable)
@adapter(Interface, IRetractAndRenameOldVersionAction, Interface)
class RetractAndRenameOldVersionExecutor(object):
    """ Retract and rename old version executor
    """
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        oid = obj.getId()
        parent = obj.getParentNode()

        old_id = new_id = None
        if oid.startswith('copy_of_'):
            old_id = oid.replace('copy_of_', '', 1)
            new_id = old_id + '-%d' % time()
        elif oid.endswith('.1'):
            old_id = oid.replace('.1', '', 1)
            new_id = old_id + '-%d' % time()

        if not (old_id and new_id):
            return True

        try:
            old_version = parent[old_id]
            api.content.transition(
                obj=old_version,
                transition='markForDeletion',
                comment="Auto archive item due to new version being published")

            # Bypass user roles in order to rename old version
            oldSecurityManager = getSecurityManager()
            newSecurityManager(None, SpecialUsers.system)

            api.content.rename(obj=old_version, new_id=new_id)
            api.content.rename(obj=obj, new_id=old_id)
            obj.setEffectiveDate(DateTime())

            # Switch back to the current user
            setSecurityManager(oldSecurityManager)
        except Exception as err:
            logger.exception(err)
            return True
        return True


class RetractAndRenameOldVersionAddForm(NullAddForm):
    """ Retract and rename old version addform
    """
    def create(self):
        """ Create content-rule
        """
        return RetractAndRenameOldVersionAction()
