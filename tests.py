from apps.helpers import pftest
from .factory import *

class GetClansEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:clans'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class GetLeaguesEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:leagues'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class GetMyClansEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:my_clans'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class GetFeedEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:clan_feed'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class PostFeedLikeEndpointTest(pftest.PostEndpointAPITestCase):
    url_name = 'clans:clan_feed_like' 
    kwargs = {'feed_item_id':1, 'clan_id': 1}
    parameters = {'like':True}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class PostFeedlkeEndpointTest(pftest.PostEndpointAPITestCase):
    url_name = 'clans:clan_feed_like'
    kwargs = {'feed_item_id':1, 'clan_id': 1}
    parameters = {'like':False}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)


class GetClanDetailEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:clan_detail'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class GetClanMembersEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:clan_members'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class PatchFavoriteEndpointTest(pftest.PatchEndpointAPITestCase):
    url_name = 'clans:clan_set_primary'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class GetClanChallengesEndpointTest(pftest.GetEndpointAPITestCase):
    url_name = 'clans:clan_challenges'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class PostClanInviteEndpointTest(pftest.PostEndpointAPITestCase):
    url_name = 'clans:clan_invites'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        ClanMemberFactory.create(user=self.mobile_profile)

class AcceptClanInviteEndpointTest(pftest.PatchEndpointAPITestCase):
    url_name = 'clans:clan_invites_detail'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

class DeclineClanInviteEndpointTest(pftest.pftest.PatchEndpointAPITestCase):
    url_name = 'clans:clan_invites_detail'
    kwargs = {'clan_id':1}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

