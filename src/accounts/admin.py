from django.contrib import admin
from django.shortcuts import HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .forms import UserChangeForm, UserCreationForm
from .models import MyUser, UserProfile, Rating, University, UserPicture, Contact

class MyUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ( 'id','username','email', 'first_name', 'last_name', 'referral', 'is_admin', 'is_active')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password','referral')}),
        ('Personal info', {'fields': ('first_name','last_name','university')}),
        ('Permissions', {'fields': ('is_admin','is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'first_name', 'last_name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email','referral')
    ordering = ('email',)
    filter_horizontal = ()

# Now register the new UserAdmin...
admin.site.register(MyUser, MyUserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    
    class Meta:
        model = UserProfile
        
admin.site.register(UserProfile, UserProfileAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


class RatingAdmin(admin.ModelAdmin):
    
    class Meta:
        model = Rating
        
admin.site.register(Rating, RatingAdmin)

def export_csv(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=mymodel.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    writer.writerow([
        smart_str(u"ID"),
        smart_str(u"name"),
        smart_str(u"web_page"),
    ])
    for obj in queryset:
        writer.writerow([
            smart_str(obj.pk),
            smart_str(obj.name),
            smart_str(obj.web_page),
        ])
    return response
export_csv.short_description = u"Export CSV"

class UniversityAdmin(admin.ModelAdmin):
    actions = [export_csv]
    list_display = ( 'name','domain')
    class Meta:
        model = University
    search_fields = ('domain',)    
admin.site.register(University, UniversityAdmin)

class UserPictureAdmin(admin.ModelAdmin):
    
    class Meta:
        model = UserPicture
        
admin.site.register(UserPicture, UserPictureAdmin)

class ContactAdmin(admin.ModelAdmin):
    
    class Meta:
        model = Contact
        
admin.site.register(Contact, ContactAdmin)