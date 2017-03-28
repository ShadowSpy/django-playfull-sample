import factory
from faker import Factory as FakerFactory
from playfull_mobile.factory import MobileProfileFactory
from .models import *

faker = FakerFactory().create()

class ClanFactory(factory.DjangoModelFactory):
    class Meta:
        model = Clan

    name = factory.LazyAttribute(lambda o: faker.company())

class ClanMemberFactory(factory.DjangoModelFactory):
    class Meta:
        model = ClanMember

    clan = factory.SubFactory(ClanFactory)
    user = factory.SubFactory(MobileProfileFactory)

class ClanContestFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda o: '%s Contest' % faker.company)
    #start_date = factory.
