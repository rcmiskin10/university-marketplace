from django.db import models
from accounts.models import MyUser
from django.contrib.auth.signals import user_logged_in

class DirectMessage(models.Model):
    
    body = models.CharField(max_length=3000)
    sender = models.ForeignKey(MyUser, related_name='sent_direct_messages', null=True, blank=True)
    receiver = models.ForeignKey(MyUser, related_name='received_direct_messages', null=True, blank=True )
    sent = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)
    read_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    read = models.BooleanField(default=False)
    parent = models.ForeignKey('self', related_name='parent_message', null=True, blank=True)
    replied = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    
    
    
    def __unicode__(self):
        return str(self.receiver)

class Convo(models.Model):
    primary_user = models.ForeignKey(MyUser, related_name='primary', null=True, blank=True)
    secondary_user = models.ForeignKey(MyUser, related_name='secondary', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False,null=True, blank=True)
    def __unicode__(self):
        return str(self.primary_user)