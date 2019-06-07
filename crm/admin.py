from django.contrib import admin

from crm import models
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'qq', 'source', 'consultant', 'content', 'status', 'date')
    list_filter = ('source', 'consultant', 'date')
    search_fields = ('qq', 'name')
    raw_id_fields = ('consult_course',)
    filter_horizontal = ('tags',)
    list_editable = ('status',)

#######################自定义用户管理（用来替代admin的用户管理）######################
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        models = models.UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Password don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return  user



class UserChangeForm(forms.ModelForm):
    '''
    "A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    '''
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']


class UserProfileAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin', 'is_active', 'is_staff')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields':('email', 'password')}),
        ('Personal', {'fields':('name',)}),
        ('Permissions', {'fields':('is_admin',"is_active", "roles", "user_permissions", "groups")}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {'classes':('wide',),
                'fields': ('email', 'name', 'password1', 'password2')
                }),
    )

    search_fields = ('email',)
    ordering = ('email',)

    filter_horizontal = ("roles", "user_permissions", "groups")
    #filter_horizontal = ()

admin.site.register(models.UserProfile, UserProfileAdmin)
##############################################自定义用户管理#######################

admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.Enrollment)
admin.site.register(models.Course)
admin.site.register(models.ClassList)
admin.site.register(models.CourseRecord)
admin.site.register(models.Branch)
admin.site.register(models.Role)
admin.site.register(models.Payment)
admin.site.register(models.StudyRecord)
#admin.site.register(models.UserProfile)
admin.site.register(models.Tag)
admin.site.register(models.Menu)
admin.site.register(models.ContractTemplate)
