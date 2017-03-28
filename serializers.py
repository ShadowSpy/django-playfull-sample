from django.db import transaction

from rest_framework import serializers
from .models import League, Clan, ClanInvite, ClanMember, ClanContest, Participant
from playfull_mobile.models import InboxObject
from apps.user_profile.models import MobileProfile
from apps.user_profile.serializers import MobileProfileUsernameSerializer


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = League
        fields = ('id','name','description','image','facebook_link', 'twitter_link', 'is_public',)

class ClanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clan
        fields = ('id', 'name', 'motto', 'clan_population','is_public', 'primary_color', 'secondary_color',
                  'victory_points', 'total_victory_points', 'join_code', 'emblem_image', 'emblem_frame',
                  'emblem_pattern', 'emblem_colorflip', 'emblem_custom','league_id','league',)
        read_only = ('id', 'clan_population', 'victory_points', 'total_victory_points',
                            'join_code', 'league',)
    victory_points = serializers.IntegerField(source='total_victory_points', read_only=True)
    clan_population = serializers.SerializerMethodField()
    league_id = serializers.PrimaryKeyRelatedField(
        source='league', 
        queryset=League.objects.all(),
        allow_null=True,
        default=None,
    )
    league = LeagueSerializer(read_only=True)
    join_code = serializers.SerializerMethodField()

    def get_join_code(self,obj):
        if (obj.join_code is not None):
            return obj.join_code.referral_code
        else:
            return None
    def get_clan_population(self, obj):
        return ClanMember.objects.filter(clan=obj).count()

    def create(self, validated_data):
        with transaction.atomic():
            #Deduct 10 heartstones
            print(self.context['request'])
            mp = self.context['request'].user.mobile_profile
            mp.heartstones -= 10
            mp.save()

            #Create clan with creator as admin
            clan = super().create(validated_data)
            ClanMember.objects.create(user=mp, clan=clan, membership_type=ClanMember.CAPTAIN)
            return clan
# 
class ClanMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clan
        fields = ('id', 'name',)

class ClanInviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanInvite
        fields = ('id', 'users', 'clan',)
        read_only = ('id',)

    users = serializers.PrimaryKeyRelatedField(write_only=True, many=True, queryset=MobileProfile.objects.all()) 

    def validate_clan(self, clan):
        user = self.context['request'].user.mobile_profile
        is_captain = clan.clanmember_set.filter(
            user=user,
            membership_type=ClanMember.CAPTAIN,
        )
        if not is_captain:
            raise serializers.ValidationError('You must be a captain to invite members')
        return clan

    def create(self, validated_data):
        invite = ClanInvite.objects.create(
            from_user = self.context['request'].user.mobile_profile,
            clan = validated_data['clan']
        )
        obj = InboxObject.objects.create(
            inbox_object=invite,
        )
        for user in validated_data['users']:
            obj.users.add(user)
        return invite
        
class ClanInviteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanInvite
        fields = ('id', 'from_user', 'clan', 'is_accepted')
        read_only = ('id', 'clan',)

    from_user = MobileProfileUsernameSerializer(read_only=True)
    clan = ClanSerializer(read_only=True)

    def update(self, instance, validated_data):
        instance.is_accepted = validated_data['is_accepted']
        if instance.is_accepted:
            user = self.context['request'].user.mobile_profile
            if instance.clan.league_id:
                is_in_league = ClanMember.objects.filter(clan__league_id=instance.clan.league_id, user=user).exists()
            else:
                is_in_league = False

            #Validate that user can join clan
            if is_in_league:
                raise serializers.ValidationError("You can only join one team per league")

            #Place user into the appropriate clan
            ClanMember.objects.create(
                user=user,
                membership_type=ClanMember.MEMBER,
                clan=instance.clan,
            )

        instance.save()
        return instance

class ClanMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanMember
        fields = ('id','user_id','membership_type', 'is_primary', 'username', 'display_name', 'profile_picture', 'progress_points', 'victory_points',)
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    display_name = serializers.ReadOnlyField(source='user.display_name')
    profile_picture = serializers.ReadOnlyField(source='user.avatar_to_show')
    victory_points = serializers.ReadOnlyField(source='progress_points')

class ClanMembershipWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanMember
        fields = ('id', 'is_primary',)
    def update(self, instance, validated_data):
        try:
            select = validated_data['is_primary']
            if select:
                instance.set_primary()
        except KeyError:
            pass
        return instance


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ('id', 'name', 'primary_color', 'emblem_image', 'emblem_frame', 'emblem_pattern',
                  'emblem_colorflip', 'emblem_custom', 'progress_points',)

    id = serializers.ReadOnlyField(source='clan_id')
    name = serializers.ReadOnlyField(source='clan.name')
    primary_color = serializers.ReadOnlyField(source='clan.primary_color')
    emblem_image = serializers.ReadOnlyField(source='clan.emblem_image')
    emblem_frame = serializers.ReadOnlyField(source='clan.emblem_frame')
    emblem_pattern = serializers.ReadOnlyField(source='clan.emblem_pattern')
    emblem_colorflip = serializers.ReadOnlyField(source='clan.emblem_colorflip')
    emblem_custom = serializers.ReadOnlyField(source='clan.emblem_custom')

class ContestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClanContest
        fields = ('name', 'contest_type', 'description', 'brief_description', 'description_image',
                  'participants', 'start_date', 'end_date', 'progress_points', 'progress_point_goal',
                  'victory_point_reward', 'milestone_start', 'milestone_bonus', 'milestone_intervals',
                  'challenge_ladder', 'item')

    participants = ParticipantSerializer(many=True, read_only=True, source='participant_set')
    challenge_ladder = serializers.SerializerMethodField(allow_null=True)
    vendor_item = serializers.SerializerMethodField(allow_null=True)

    def get_challenge_ladder(self, obj):
        if hasattr(obj, 'laddercontest'):
            from playfull_api.serializers import LadderSerializer
            return LadderSerializer(obj.laddercontest.challenge_ladder).data
        return None

    def get_item(self, obj):
        if hasattr(obj, 'itemcontest'):
            from apps.item.serializers import ItemSerializer
            return ItemSerializer(obj.itemcontest.item).data
        return None
