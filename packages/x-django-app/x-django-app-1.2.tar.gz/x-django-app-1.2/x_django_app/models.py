from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext_lazy as _

from django.contrib.admin.options import get_content_type_for_model


# Create your models here.


class ActivityManager(models.Manager):
    '''
    Activiy Manager
    '''
    use_in_migrations = True

    def create_activity(self, activity_object, activity, message, user):
        '''
        Create activity record
        '''
        return self.model.objects.create(
                            user=user,
                            activity_object=activity_object,
                            activity=activity,
                            message=message,
                            model=activity_object.__class__.__name__
        )


class XActivity(models.Model):
    '''
    Store all user activities
    '''
    # Choices
    CREATE = 'CR'
    EDIT = 'ED'
    DELETE = 'DE'
    RESET = 'RE'
    DOWNLOAD = 'DW'
    BACKUP = 'BC'
    RESTORE = 'RS'
    EXPORT = 'EX'
    IMPORT = 'IM'
    PUBLISH = 'PU'
    ACCEPT = 'AC'
    REJECT = 'RJ'
    ENABLE = 'EN'
    DISABLE = 'DI'
    ACTIVATE = 'AV'
    DEACTIVATE = 'DV'
    BLOCK = 'BL'
    APPROVE = 'AP'
    LIKE = 'LK'
    UNLIKE = 'UL'
    RECOMMEND = 'RC'
    UNRECOMMEND = 'UC'
    activity_choices = [
                        (CREATE, _('Create')),
                        (EDIT, _('Edit')),
                        (DELETE, _('Delete')),
                        (RESET, _('Reset Password')),
                        (DOWNLOAD, _('Download')),
                        (BACKUP, _('Backup')),
                        (RESTORE, _('Restore')),
                        (EXPORT, _('Export')),
                        (IMPORT, _('Import')),
                        (PUBLISH, _('Publish')),
                        (ACCEPT, _('Accept')),
                        (REJECT, _('Reject')),
                        (ENABLE, _('Enable')),
                        (DISABLE, _('Disable')),
                        (ACTIVATE, _('Activate')),
                        (DEACTIVATE, _('Deactivate')),
                        (BLOCK, _('Block')),
                        (APPROVE, _('Approve')),
                        (LIKE, _('Like')),
                        (UNLIKE, _('Unlike')),
                        (RECOMMEND, _('Recommend')),
                        (UNRECOMMEND, _('Unrecommend')),
    ]
    #####################
    user = models.ForeignKey(
                        get_user_model(),
                        related_name='x_user_activity',
                        verbose_name=_('User'),
                        on_delete=models.CASCADE,
                        blank=False,
                        null=False
    )
    activity = models.CharField(
                        verbose_name=_('Activity'),
                        max_length=2,
                        choices=activity_choices,
                        null=False,
                        blank=False
    )
    model = models.CharField(
                        verbose_name=_('Activity model'),
                        max_length=50,
                        blank=False,
                        null=False
    )
    message = models.CharField(
                        verbose_name=_('Activity message'),
                        max_length=128,
                        blank=False,
                        null=False
    )
    activity_type = models.ForeignKey(
                        ContentType,
                        on_delete=models.SET_NULL,
                        blank=True,
                        null=True
    )
    activity_id = models.PositiveIntegerField(
                        verbose_name=_('Activity object id'),
                        blank=False,
                        null=False
    )
    activity_object = GenericForeignKey('activity_type', 'activity_id')
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )

    objects = ActivityManager()

    def __str__(self):
        '''
        give the string representation
        '''
        return f"{self.user.id}-{self.activity_object}-{self.activity}"



class XModel():
    '''
    Add get activities method to model class
    '''
    def get_activities(self):
        '''
        Get all activities related to the selected object
        '''
        try:
            activities = XActivity.objects.filter(
                            activity_type=get_content_type_for_model(self),
                            activity_id=self.id).order_by('-created_at')
        except Exception:
            activities = None
        return activities