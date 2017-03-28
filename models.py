from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from playfull_mobile.models import Ladder, ReferralCode, InboxObject
from apps.user_profile.models import MobileProfile

class Clan(models.Model):
    name = models.CharField(max_length=50)
    motto = models.CharField(max_length=140, default='', blank=True)
    primary_color = models.CharField(max_length=6, default='56AAFF')
    secondary_color = models.CharField(max_length=6, default='DEEEFF')
    total_victory_points = models.IntegerField(default=0)
    join_code = models.ForeignKey(ReferralCode, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    league = models.ForeignKey('League', default=None, null=True, blank=True, on_delete=models.SET_NULL) #Clans must be in the same league to view one another
    emblem_image = models.IntegerField(default=0)
    emblem_frame = models.IntegerField(default=0)
    emblem_pattern = models.IntegerField(default=0)
    emblem_colorflip = models.IntegerField(default=0)
    emblem_custom = models.CharField(max_length=200, default='', blank=True)

    members = models.ManyToManyField(MobileProfile, through='ClanMember', related_name='clans')

    class Meta:
        ordering = ('-total_victory_points', )

    def __str__(self):
        return self.name

class ClanMember(models.Model):
    CAPTAIN='captain'
    MEMBER='member'
    MEMBERSHIP_TYPE_CHOICES = (
        tuple([CAPTAIN]*2),
        tuple([MEMBER]*2),
    )
    
    user = models.ForeignKey(MobileProfile, related_name='clan_members')
    membership_type = models.CharField(max_length=10, default=MEMBER, choices=MEMBERSHIP_TYPE_CHOICES)
    clan = models.ForeignKey(Clan)
    progress_points = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    def set_primary(self):
        self.user.clan_members.update(is_primary=False)
        self.is_primary=True
        self.save()
    class Meta:
        ordering = ('-progress_points',)

    def __str__(self):
        return "Clan: {} | User: {} | Active: {}".format(
            str(self.clan), self.user.id, "Yes" if self.is_primary else "No")

    def __repr__(self):
        return self.__str__()

class ClanInvite(models.Model):
    inbox_object = GenericRelation(InboxObject,
                                   content_type_field='content_type',
                                   object_id_field='object_id',
                                   related_query_name='clan_invites')
    from_user = models.ForeignKey(MobileProfile, related_name='sent_clan_invites')
    clan = models.ForeignKey('Clan', related_name='invites')
    is_accepted = models.NullBooleanField(default=None)

# Provides various ways to earn victory points for a clan
class ClanContest(models.Model):
    VENDOR_CONTEST = 'vendor_contest'
    MYSTERY_ITEM = 'mystery_item'
    SOCIAL_MEDIA = 'social_media'
    ITEM_SPOTLIGHT = 'item_spotlight'
    RESTAURANT_SPOTLIGHT = 'restaurant_spotlight'
    GAME_TOURNAMENT = 'game_tournament'
    POWER_UP = 'power_up'
    HAPPY_HOUR = 'happy_hour'
    VERSUS = 'versus'
    CONTEST_TYPE_CHOICES = (
        tuple([VENDOR_CONTEST] * 2),
        tuple([MYSTERY_ITEM] * 2),
        tuple([SOCIAL_MEDIA] * 2),
        tuple([ITEM_SPOTLIGHT] * 2),
        tuple([RESTAURANT_SPOTLIGHT] * 2),
        tuple([GAME_TOURNAMENT] * 2),
        tuple([POWER_UP] * 2),
        tuple([HAPPY_HOUR] * 2),
        tuple([VERSUS] * 2),
    )

    name = models.CharField(max_length=50)
    contest_type = models.CharField(max_length=30, default=VENDOR_CONTEST, choices=CONTEST_TYPE_CHOICES)
    description = models.CharField(max_length=1000, default='', blank=True)
    brief_description = models.CharField(max_length=200, default='', blank=True)
    description_image = models.ImageField(upload_to='contest_description_images', default=None, blank=True, null=True)
    progress_points = models.IntegerField(default=0)
    progress_point_goal = models.IntegerField(default=0) #0 means there is no set goal and progress is equivalent to victory points
    vp_per_progress_point = models.IntegerField(default=1)
    victory_point_reward = models.IntegerField(default=0)
    milestone_start = models.IntegerField(default=0)
    milestone_bonus = models.IntegerField(default=0)
    milestone_intervals = models.IntegerField(default=25)
    participants = models.ManyToManyField(Clan, related_name='contests', through='Participant')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def add_progress(self, amount, user):
        # Check that contest is not over yet
        current_time = timezone.now()
        if (self.progress_point_goal != 0 and self.progress_points >= self.progress_point_goal) or \
           current_time < self.start_date or current_time >= self.end_date :
            return 0

        member = user.clanmember
        clan = member.clan

        clan_participant = self.participant_set.get(clan=clan)
        clan_participant.progress_points += amount
        clan_participant.save()

        vp_earned = amount*self.vp_per_progress_point

        #Add extra points if milestone is enabled
        if self.milestone_bonus > 0 and self.milestone_interval > 0:
            threshold = clan_participant.progress_points - self.milestone_start
            if threshold > 0:
                tiers = int(threshold / self.milestone_interval)
                vp_earned += tiers * self.milestone_bonus

        member.progress_points += vp_earned
        member.save()

        clan.total_victory_points += vp_earned
        clan.save()

        if self.progress_point_goal == 0:
            self.progress_points += amount
            self.save()

        # Race style contests, where first clan to reach a goal wins
        elif self.contest_type == self.MYSTERY_ITEM:
            if clan_participant.progress_points >= self.progress_point_goal:
                clan.total_victory_points += self.victory_point_reward
                clan.save()
            if clan_participant.progress_points > self.progress_points:
                self.progress_points = clan_participant.progress_points
                self.save()

        # Milestone style contests, where all participating clans work towards common goal
        else:
            self.progress_points += amount
            self.save()
            if self.progress_points >= self.progress_point_goal: 
                all_participants = self.participant_set.all()
                for c in all_participants:
                    c.clan.total_victory_points += self.victory_point_reward
                    c.clan.save()

        return vp_earned

    def __str__(self):
        return self.name

# Earn points for this contest by scanning QR codes at vendor locations    
class VendorContest(ClanContest):
    store_sponsor = models.ForeignKey('store.Store', related_name='clan_contests')
    qr_code = models.ForeignKey(ReferralCode, blank=True, null=True, default=None)

class LadderContest(ClanContest):
    challenge_ladder = models.OneToOneField(Ladder, related_name='clan_contest')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contest_type = 'challenge_ladder'

class ItemContest(ClanContest):
    item = models.ForeignKey('item.Item', related_name='item_contests')

class Participant(models.Model):
    clan_contest = models.ForeignKey(ClanContest)
    clan = models.ForeignKey(Clan)
    progress_points = models.IntegerField(default=0)

    class Meta:
        ordering = ('-progress_points',)

#Only clans within the same leagues can see each other
class League(models.Model):
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=200, default='', blank=True)
    description = models.CharField(max_length=200, default='', blank=True)
    facebook_link = models.CharField(max_length=200, default='', blank=True)
    twitter_link = models.CharField(max_length=200, default='', blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.name
