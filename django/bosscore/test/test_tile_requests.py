# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from rest_framework.test import APITestCase
from rest_framework.request import Request
from django.http import HttpRequest
from django.conf import settings
from django.contrib.auth.models import User

from bosscore.request import BossRequest
from bosscore.error import BossError
from bosscore.test.setup_db import SetupTestDB

version = settings.BOSS_VERSION


class BossTileRequestTests(APITestCase):
    """
    Class to test Boss tile requests and validation
    """

    def setUp(self):
        """
            Initialize the database
            :return:
        """
        user = User.objects.create_superuser(username='testuser', email='test@test.com', password='testuser')
        dbsetup = SetupTestDB()
        dbsetup.set_user(user)

        self.client.force_login(user)
        dbsetup.insert_test_data()

    def test_request_tile_init_channel(self):
        """
        Test initialization of tile requests for the datamodel with a channel
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/0/1'
        col = 'col1'
        exp = 'exp1'
        channel = 'channel1'
        boss_key = 'col1&exp1&channel1'
        boss_key_list = 'col1&exp1&channel1&2&0'


        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version

        ret = BossRequest(drfrequest)
        self.assertEqual(ret.get_collection(), col)
        self.assertEqual(ret.get_experiment(), exp)
        self.assertEqual(ret.get_channel(), channel)
        self.assertEqual(ret.get_boss_key(), boss_key)
        self.assertEqual(ret.get_boss_key_list()[0], boss_key_list)

    def test_request_tile_init_tileargs_channel(self):
        """
        Test initialization of tile arguments for a tile request for a channel
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/0/1'

        res = 2
        (x_start, x_stop) = (0, 512)
        (y_start, y_stop) = (0, 512)
        (z_start, z_stop) = (1, 2)

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version
        ret = BossRequest(drfrequest)

        self.assertEqual(ret.get_resolution(), res)
        self.assertEqual(ret.get_x_start(), x_start)
        self.assertEqual(ret.get_x_stop(), x_stop)
        self.assertEqual(ret.get_x_span(), x_stop - x_start)

        self.assertEqual(ret.get_y_start(), y_start)
        self.assertEqual(ret.get_y_stop(), y_stop)
        self.assertEqual(ret.get_y_span(), y_stop - y_start)

        self.assertEqual(ret.get_z_start(), z_start)
        self.assertEqual(ret.get_z_stop(), z_stop)
        self.assertEqual(ret.get_z_span(), z_stop - z_start)

    def test_request_tile_init_tileargs_no_time(self):
        """
        Test initialization of timesample arguments  without a specific timesample
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/0/1'

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        time = ret.get_time()
        self.assertEqual(time, range(0, 1))

    def test_request_tile_init_tileargs_time(self):
        """
        Test initialization of timesample arguments  with a single time
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/0/1/1/'

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        time = ret.get_time()
        self.assertEqual(time, range(1, 2))

    def test_request_tile_bosskey_time(self):
        """
        Test initialization of boss_key for a time sample range
        :return:
        """

        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/0/1/'
        exp_boss_keys = ['col1&exp1&channel1&2&0']

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        boss_keys = ret.get_boss_key_list()
        self.assertEqual(boss_keys, exp_boss_keys)

        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/0/1/1/'
        exp_boss_keys = ['col1&exp1&channel1&2&1']

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version
        ret = BossRequest(drfrequest)
        boss_keys = ret.get_boss_key_list()
        self.assertEqual(boss_keys, exp_boss_keys)


    def test_request_tile_invalid_xargs(self):
        """
        Test initialization of tile arguments for a invalid tile request. The x-args are outside the coordinate
        frame
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/7000/1/1/1/'

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version

        with self.assertRaises(BossError):
            BossRequest(drfrequest)

    def test_request_tile_invalid_yargs(self):
        """
        Test initialization of tile arguments for a invalid tile request. The y-args are outside the coordinate
        frame
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/7000/1/1/'

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version

        with self.assertRaises(BossError):
            BossRequest(drfrequest)

    def test_request_tile_invalid_zargs(self):
        """
        Test initialization of tile arguments for a invalid tile request. The z-args are outside the coordinate
        frame
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xy/512/2/0/1/7000/1/'

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version

        with self.assertRaises(BossError):
            BossRequest(drfrequest)

    def test_request_tile_invalid_orientation(self):
        """
        Test initialization of tile arguments for a invalid tile request. Unrecognized orientation
        :return:
        """
        url = '/' + version + '/tile/col1/exp1/channel1/xe/512/2/0/1/1/1/'

        # Create the request
        req = HttpRequest()
        req.META = {'PATH_INFO': url}
        drfrequest = Request(req)
        drfrequest.version = version

        with self.assertRaises(BossError):
            BossRequest(drfrequest)




