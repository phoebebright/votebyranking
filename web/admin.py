
from web.models import *


from django.contrib import admin
from django.contrib.admin import helpers
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth import get_user_model
# User = get_user_model()
#
#
# UserAdmin.list_display = ('email', 'username', 'paid_points', 'new_points', 'is_active', 'date_joined', 'last_login', 'is_staff')
#
#
# admin.site.register(User, UserAdmin)


class QuestionAdmin(admin.ModelAdmin):

    class Meta:
        model = Question



admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(GroupedAnswer)
admin.site.register(Submission)
admin.site.register(SubmissionSet)
