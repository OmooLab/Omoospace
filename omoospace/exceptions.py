class NotFoundError(Exception):
    def __init__(self,  item: str = None, scope: str = None):
        item_str = '%s ' % item if item else ""
        scope_str = ' in "%s"' % scope if scope else ""
        message = 'No %sfound%s.' % (item_str, scope_str)
        super().__init__(message)


class ExistsError(Exception):
    def __init__(self,  item: str = None, scope: str = None):
        item_str = '%s ' % item if item else ""
        scope_str = ' in "%s"' % scope if scope else ""
        message = '%salready exists%s.' % (item_str, scope_str)
        super().__init__(message)


class NotIncludeError(Exception):
    def __init__(self,  item: str = None, scope: str = None):
        item_str = '%s is ' % item if item else ""
        scope_str = ' in "%s"' % scope if scope else ""
        message = '%snot include%s.' % (item_str, scope_str)
        super().__init__(message)


class InvalidError(Exception):
    def __init__(self,  item: str = None, type: str = None):
        item_str = '%s ' % item if item else ""
        type_str = ' %s' % type if type else ""
        message = '%sis invalid%s.' % (item_str, type_str)
        super().__init__(message)


class EmptyError(Exception):
    def __init__(self,  item: str = None):
        item_str = '%s ' % item if item else ""
        message = '%scannot be empty.' % item_str
        super().__init__(message)


class CreateFailed(Exception):
    def __init__(self, item: str = None):
        item_str = ' %s' % item if item else ""
        message = 'Fail to create%s.' % item_str
        super().__init__(message)

class MoveFailed(Exception):
    def __init__(self, item: str = None):
        item_str = ' %s' % item if item else ""
        message = 'Fail to move%s.' % item_str
        super().__init__(message)