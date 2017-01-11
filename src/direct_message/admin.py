from django.contrib import admin

from .models import DirectMessage, Convo

class DirectMessageAdmin(admin.ModelAdmin):
    
    class Meta:
        model = DirectMessage
        
admin.site.register(DirectMessage, DirectMessageAdmin)

class ConvoAdmin(admin.ModelAdmin):
    list_display = ( 'primary_user','secondary_user','timestamp')
    class Meta:
        model = Convo
        
admin.site.register(Convo, ConvoAdmin)