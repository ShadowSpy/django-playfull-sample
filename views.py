from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics
from . import models, serializers
from playfull_api.permissions import IsUser
from .permissions import IsInvited

import datetime

class ClanView(generics.ListCreateAPIView):
    serializer_class = serializers.ClanSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        league_id = self.kwargs.get('league_id', None)
        return models.Clan.objects.filter(is_active=True, league_id=league_id)

class LeagueView(generics.ListAPIView):
    serializer_class = serializers.LeagueSerializer
    permission_classes = [IsUser]
    def get_queryset(self):
        return models.League.objects.filter(is_public=True)

class MyClanView(generics.ListAPIView):
    serializer_class = serializers.ClanSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        return self.request.user.mobile_profile.clans.all()

class ClanDetailView(generics.RetrieveAPIView):
    queryset = models.Clan.objects.filter(is_active=True)
    serializer_class = serializers.ClanSerializer
    permission_classes = [IsUser]
    lookup_url_kwarg = 'clan_id'

class ClanInviteView(generics.CreateAPIView):
    queryset = models.ClanInvite.objects.all()
    serializer_class = serializers.ClanInviteCreateSerializer
    permission_classes = [IsUser]

class ClanInviteUpdateView(generics.UpdateAPIView):
    queryset = models.ClanInvite.objects.filter(is_accepted__isnull=True)
    serializer_class = serializers.ClanInviteUpdateSerializer
    permission_classes = [IsInvited]

class ClanMemberView(generics.ListAPIView):
    serializer_class = serializers.ClanMemberSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        if 'clan_id' in self.kwargs:
            return models.ClanMember.objects.filter(clan_id=self.kwargs['clan_id'], clan__is_active=True)
        raise Http404

class MyClanMembershipWriteView(generics.UpdateAPIView):
    serializer_class = serializers.ClanMembershipWriteSerializer
    permission_classes = [IsUser]
    lookup_field = 'clan_id'

    def get_queryset(self):
        if 'clan_id' in self.kwargs:
            return models.ClanMember.objects.filter(
                user=self.request.user.mobile_profile,
                clan_id=self.kwargs['clan_id'], 
                clan__is_active=True
            )   

class MyClanMembershipView(generics.ListAPIView):
    serializer_class = serializers.ClanMemberSerializer
    permission_classes = [IsUser]
    def get_queryset(self):
        user = self.request.user.mobile_profile
        return models.ClanMember.objects.filter(user=user, clan__is_active=True)

    
class ClanChallengeView(generics.ListAPIView):
    serializer_class = serializers.ContestListSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        if 'clan_id' in self.kwargs:
            clan_id = self.kwargs['clan_id']
            challenges = models.ClanContest.objects.filter(participants__id=clan_id).exclude(contest_type='vendor_contest')
            challenges = challenges.filter(end_date__gt=timezone.now()-datetime.timedelta(days=3))
            challenges = challenges.exclude(contest_type='VC') #TODO 'VC' will be deprecated in this build
            challenges = challenges.prefetch_related('participants').select_related('laddercontest').select_related('itemcontest')
            return challenges
        raise Http404
