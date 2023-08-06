import unittest

from .context import yfc_cache_manager as yfcm
from .context import yfc_dat as yfcd
from .context import yfc_utils as yfcu

import os, shutil, tempfile
import json, pickle

from time import sleep
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from pprint import pprint

class Test_Yfc_Cache(unittest.TestCase):

    def setUp(self):
        self.tempCacheDir = tempfile.TemporaryDirectory()
        yfcm.SetCacheDirpath(self.tempCacheDir.name)


    def tearDown(self):
        self.tempCacheDir.cleanup()


    def test_cache_store(self):
        cat = "test1"
        var = "value"
        value = 123

        ft = "json"

        yfcm.StoreCacheDatum(cat, var, value)
        fp = os.path.join(yfcm.GetCacheDirpath(), cat, var+"."+ft)
        try:
            self.assertTrue(os.path.isfile(fp))
        except:
            print("Does not exist: "+fp)
            raise

        obj = yfcm.ReadCacheDatum(cat, var)
        self.assertEqual(obj, value)

        with open(fp, 'r') as inData:
            js = json.load(inData, object_hook=yfcu.JsonDecodeDict)
            self.assertEqual(js["data"], value)


    def test_cache_store_expiry(self):
        cat = "test1"
        var = "value"
        value = 123

        ft = "json"

        dt = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        exp = dt + timedelta(seconds=1)

        yfcm.StoreCacheDatum(cat, var, value, expiry=exp)
        fp = os.path.join(yfcm.GetCacheDirpath(), cat, var+"."+ft)
        self.assertTrue(os.path.isfile(fp))

        obj = yfcm.ReadCacheDatum(cat, var)
        self.assertEqual(obj, value)

        with open(fp, 'r') as inData:
            js = json.load(inData, object_hook=yfcu.JsonDecodeDict)

        sleep(1)
        obj = yfcm.ReadCacheDatum(cat, var)
        self.assertIsNone(obj)
        self.assertFalse(os.path.isfile(fp))


    def test_cache_store_packed(self):
        cat = "test1"
        var = "balance_sheet"
        var_grp = "annuals"
        value = 123

        ft = "pkl"

        yfcm.StoreCachePackedDatum(cat, var, value)
        fp = os.path.join(yfcm.GetCacheDirpath(), cat, var_grp+"."+ft)
        try:
            self.assertTrue(os.path.isfile(fp))
        except:
            print("Does not exist: "+fp)
            raise

        obj = yfcm.ReadCachePackedDatum(cat, var)
        self.assertEqual(obj, value)


    def test_cache_store_packed_expiry(self):
        cat = "test1"
        var = "balance_sheet"
        var_grp = "annuals"
        value = 123

        ft = "pkl"

        dt = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        exp = dt + timedelta(seconds=1)

        yfcm.StoreCachePackedDatum(cat, var, value, expiry=exp)
        fp = os.path.join(yfcm.GetCacheDirpath(), cat, var_grp+"."+ft)
        self.assertTrue(os.path.isfile(fp))

        obj = yfcm.ReadCachePackedDatum(cat, var)
        self.assertEqual(obj, value)

        ft = os.path.join(yfcm.GetCacheDirpath(), cat, var+".metadata")
        self.assertEqual(ft, ft)

        sleep(1)
        # sleep(2)
        obj = yfcm.ReadCachePackedDatum(cat, var)
        self.assertIsNone(obj)
        with open(fp, 'rb') as inData:
            pkl = pickle.load(inData)
            self.assertFalse(cat in pkl.keys())


    def test_cache_store_types(self):
        cat = "test1"
        var = "value"

        json_values = []
        json_values.append(int(1))
        json_values.append(float(1))
        json_values.append([1, 3])
        json_values.append(datetime.utcnow().replace(tzinfo=ZoneInfo("UTC")))
        json_values.append(timedelta(seconds=2.01))

        pkl_values = []
        pkl_values.append(set([1, 3]))
        pkl_values.append({'a':1, 'b':2})

        for value in json_values+pkl_values:
            # print("")
            # print("testing value = {0} (type={1})".format(value, type(value)))

            if value in json_values:
                ext = "json"
            else:
                ext = "pkl"
            # print("ext = {0}".format(ext))

            fp = os.path.join(yfcm.GetCacheDirpath(), cat, var+"."+ext)
            # if os.path.isfile(fp):
            #     os.remove(fp)

            # print("value = {0}".format(value))
            yfcm.StoreCacheDatum(cat, var, value)
            # print("value = {0}".format(value))
            try:
                self.assertTrue(os.path.isfile(fp))
            except:
                print("Does not exist: "+fp)
                raise

            obj = yfcm.ReadCacheDatum(cat, var)
            self.assertEqual(obj, value)


if __name__ == '__main__':
    unittest.main()
