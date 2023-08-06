from xperms.base import BasePerm
from xperms.managers import RelatedPermManager


class Perm(BasePerm):

    related_manager = RelatedPermManager()

    class Meta:
        base_manager_name = 'related_manager'
