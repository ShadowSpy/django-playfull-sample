from rest_framework.permissions import BasePermission

class IsClanMember(BasePermission):
    def has_permission(self, request, view):
        try:
            clan_id = view.kwargs['clan_id']
            return request.user.mobile_profile.clanmember_set.filter(clan_id=clan_id).exists()
        except AttributeError:
            return False

class IsInvited(BasePermission):
    def has_object_permission(self, request, view, invite):
        if invite.inbox_object.first().users.filter(id=request.user.mobile_profile.id).exists():
            return True
        return False
