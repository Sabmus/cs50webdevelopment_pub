from django.test import TestCase
from django.core.exceptions import ValidationError

from . import models


class FollowerTestCase(TestCase):

    def setUp(self):
        # create users
        models.User.objects.create_user(username="user1", email="user1@email.com", password="MyTesting321654987")
        models.User.objects.create_user(username="user2", email="user2@email.com", password="MyTesting321654987")
        models.User.objects.create_user(username="user3", email="user3@email.com", password="MyTesting321654987")
        models.User.objects.create_user(username="user4", email="user4@email.com", password="MyTesting321654987")
        models.User.objects.create_user(username="user5", email="user5@email.com", password="MyTesting321654987")

    def test_create_user(self):
        user1 = models.User.objects.get(username="user1")
        self.assertEqual(user1.pk, 1)

    def test_follow(self):
        user1 = models.User.objects.get(username="user1")
        user2 = models.User.objects.get(username="user2")
        user1.follower.add(user2)
        self.assertEqual(user1.follower.count(), 1)

    def test_follow_self(self):
        user1 = models.User.objects.get(username="user1")
        user1.follower.add(user1)
        self.assertEqual(user1.follower.count(), 0)

    def test_get_followers(self):
        user1 = models.User.objects.get(username="user1")
        user2 = models.User.objects.get(username="user2")
        user3 = models.User.objects.get(username="user3")
        user4 = models.User.objects.get(username="user4")
        user5 = models.User.objects.get(username="user5")

        user1.follower.add(user1)  # this should not be saved, because is a self-follow
        user2.follower.add(user1)
        user3.follower.add(user1)
        user4.follower.add(user1)
        user5.follower.add(user1)

        user_following = models.User.objects.filter(follower__exact=user1)
 
        self.assertEqual(user_following.count(), 4)
