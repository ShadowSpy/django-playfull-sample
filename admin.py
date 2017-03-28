from django.contrib import admin

from .models import *

class ClanAdmin(admin.ModelAdmin):
    model = Clan
    list_display = ('id', 'name', 'motto', 'total_victory_points', 'join_code', 'is_active',)

class ClanInviteAdmin(admin.ModelAdmin):
    model = ClanInvite
    list_display = ('clan', 'from_user', 'is_accepted',)

class ClanMemberAdmin(admin.ModelAdmin):
    model = ClanMember
    list_display = ('clan', 'user', 'progress_points',)

class ClanContestAdmin(admin.ModelAdmin):
    model = ClanContest
    list_display = ('id', 'name', 'progress_point_goal', 'start_date', 'end_date',)

class VendorContestAdmin(admin.ModelAdmin):
    model = VendorContest
    list_display = ('id', 'name', 'progress_point_goal', 'start_date', 'end_date', 'store_sponsor', 'qr_code',)

class ItemContestAdmin(admin.ModelAdmin):
    model = ItemContest
    list_display = ('id', 'name', 'progress_point_goal', 'start_date', 'end_date',)

class ParticipantAdmin(admin.ModelAdmin):
    model = Participant
    list_display = ('clan', 'clan_contest', 'progress_points',)

admin.site.register(Clan, ClanAdmin)
admin.site.register(ClanInvite, ClanInviteAdmin)
admin.site.register(ClanMember, ClanMemberAdmin)
admin.site.register(ClanContest, ClanContestAdmin)
admin.site.register(VendorContest, VendorContestAdmin)
admin.site.register(LadderContest, ClanContestAdmin)
admin.site.register(ItemContest, ItemContestAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(League)
