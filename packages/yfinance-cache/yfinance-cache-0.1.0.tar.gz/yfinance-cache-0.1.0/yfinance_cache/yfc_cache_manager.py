import os
import pickle, json
from pprint import pprint
from enum import Enum

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from . import yfc_dat as yfcd
from . import yfc_utils as yfcu

# To reduce #files in cache, store some YF objects together into same file (including metadata)
packed_data_cats = {}
# packed_data_cats["info"] = ["info"]
packed_data_cats["quarterlys"] = ["quarterly_balance_sheet", "quarterly_cashflow", "quarterly_earnings", "quarterly_financials"]
packed_data_cats["annuals"]    = ["balance_sheet", "cashflow", "earnings", "financials"]

quarterly_objects = packed_data_cats["quarterlys"]
annual_objects    = packed_data_cats["annuals"]

verbose=False
# verbose=True

## TODO: store DataFrames as CSV, don't need the metadata

global cacheDirpath

class Attributes(Enum):
	Write = 1
	Expiry = 2


def GetCacheDirpath():
	global cacheDirpath
	return cacheDirpath


def ResetCacheDirpath():
	global cacheDirpath
	cacheDirpath = os.path.join(yfcu.GetUserCacheDirpath(), "yfinance-cache")


def SetCacheDirpath(dp):
	global cacheDirpath
	cacheDirpath = dp
	if verbose:
		print("Set cache dir to {0}".format(cacheDirpath))


def IsObjectInPackedData(objectName):
	for k in packed_data_cats.keys():
		if objectName in packed_data_cats[k]:
			return True
	return False


def GetPackedDataCat(objectName):
	for k in packed_data_cats.keys():
		if objectName in packed_data_cats[k]:
			return k
	return None


def IsDatumCached(ticker, objectName):
	if verbose:
		print("IsDatumCached({0}, {1})".format(ticker, objectName))

	if IsObjectInPackedData(objectName):
		f = GetPackedDataCat(objectName)
		fp = os.path.join(GetCacheDirpath(), ticker, f+".pkl")
		if os.path.isfile(fp):
			with open(fp, 'rb') as inData:
				packedData = pickle.load(inData)
			return objectName in packedData.keys()
	else:
		fp_base = os.path.join(GetCacheDirpath(), ticker, objectName)
		return os.path.isfile(fp_base+".json") or os.path.isfile(fp_base+".pkl")


def ReadCacheDatum(ticker, objectName):
	if verbose:
		print("ReadCacheDatum({0}, {1})".format(ticker, objectName))

	if IsObjectInPackedData(objectName):
		return ReadCachePackedDatum(ticker, objectName)

	fp_base = os.path.join(GetCacheDirpath(), ticker, objectName)
	if os.path.isfile(fp_base+".json") and os.path.isfile(fp_base+".pkl"):
		raise Exception("For cached datum '{0}', both a .json and .pkl file exist. Should only be one.".format(objectName))

	exists = False
	md = None
	if os.path.isfile(fp_base+".json"):
		exists = True
		fp = fp_base+".json"
		with open(fp, 'r') as inData:
			js = json.load(inData, object_hook=yfcu.JsonDecodeDict)
			data = js["data"]
			if "metadata" in js:
				md = js["metadata"]
	else:
		fp = fp_base+".pkl"
		if os.path.isfile(fp):
			exists = True
			with open(fp, 'rb') as inData:
				pkl = pickle.load(inData)
				if isinstance(pkl, dict):
					if not "data" in pkl.keys():
						print(fp)
						raise Exception("Pickled dict missing 'data' key ({0}) - {1}".format(pkl.keys()))
					data = pkl["data"]
					md   = pkl["metadata"]
				else:
					raise Exception("Pickle missing metadata: "+fp)
					# data = pkl
	if not exists:
		return None

	if (not md is None) and "Expiry" in md.keys():
		dt = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
		if dt >= md["Expiry"]:
			if verbose:
				print("Deleting expired datum '{0}/{1}'".format(ticker, objectName))
			os.remove(fp)
			return None

	return data


def ReadCachePackedDatum(ticker, objectName):
	if verbose:
		print("ReadCachePackedDatum({0}, {1})".format(ticker, objectName))

	if not IsObjectInPackedData(objectName):
		raise Exception("Don't call packed-data function on non-packed data '{0}'".format(objectName))

	data = None

	f = GetPackedDataCat(objectName)
	fp_base = os.path.join(GetCacheDirpath(), ticker, f)
	fp = fp_base+".pkl"
	if os.path.isfile(fp):
		with open(fp, 'rb') as inData:
			packedData = pickle.load(inData)
			if not packedData is None:
				data = packedData[objectName]["data"]
				md   = packedData[objectName]["metadata"]

	if "Expiry" in md.keys():
		dt = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
		if dt >= md["Expiry"]:
			if verbose:
				print("Deleting expired packed datum '{0}/{1}'".format(ticker, objectName))
			del packedData[objectName]
			with open(fp, 'wb') as outData:
				pickle.dump(packedData, outData, 4)
			return None

	return data


def StoreCacheDatum(ticker, objectName, datum, expiry=None):
	if verbose:
		print("StoreCacheDatum({0}, {1})".format(ticker, objectName))

	if isinstance(expiry, yfcd.Interval):
		expiry = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC")) + yfcd.intervalToTimedelta[expiry]

	if IsObjectInPackedData(objectName):
		StoreCachePackedDatum(ticker, objectName, datum, expiry)
		return

	td = os.path.join(GetCacheDirpath(), ticker)
	if not os.path.isdir(td):
		os.makedirs(td)
	fp_base = os.path.join(td, objectName)

	if isinstance(datum, (list,int,float,str,datetime,date,timedelta)):
		ext = "json"
		## Ensure only one of json or pkl exists:
		if os.path.isfile(fp_base+".pkl"):
			os.remove(fp_base+".pkl")
	else:
		ext = "pkl"
		## Ensure only one of json or pkl exists:
		if os.path.isfile(fp_base+".json"):
			os.remove(fp_base+".json")
	# print("StoreCacheDatum() - {0} ext = {1}".format(datum, ext))

	fp = fp_base+"."+ext

	if verbose:
		print("- storing {} as {} at {}".format(objectName, ext, fp))

	md = None
	if not os.path.isfile(fp):
		if verbose:
			print("- doesn't exist: "+fp)
	else:
		if ext == "json":
			with open(fp, 'r') as inData:
				d = json.load(inData, object_hook=yfcu.JsonDecodeDict)
				if "metadata" in d:
					md = d["metadata"]
		else:
			with open(fp, 'rb') as inData:
				pkl = pickle.load(inData)
				if not "metadata" in pkl.keys():
					raise Exception("Pickled file lacks metadata: {0}".format(fp))
				md = pkl["metadata"]

	if not expiry is None:
		if md is None:
			md = {}
		md["Expiry"] = expiry

	if ext == "json":
		with open(fp, 'w') as outData:
			if not md is None:
				jdata = {"data":datum,"metadata":md}
			else:
				jdata = {"data":datum}
			json.dump(jdata, outData, default=yfcu.JsonEncodeValue)
	else:
		with open(fp, 'wb') as outData:
			pickle.dump({"data":datum,"metadata":md}, outData, 4)


def StoreCachePackedDatum(ticker, objectName, datum, expiry=None):
	if verbose:
		print("StoreCachePackedDatum({0}, {1})".format(ticker, objectName))

	if not IsObjectInPackedData(objectName):
		raise Exception("Don't call packed-data function on non-packed data '{0}'".format(objectName))

	td = os.path.join(GetCacheDirpath(), ticker)
	if not os.path.isdir(td):
		os.makedirs(td)

	f = GetPackedDataCat(objectName)
	fp = os.path.join(GetCacheDirpath(), ticker, f+".pkl")
	if os.path.isfile(fp):
		with open(fp, 'rb') as inData:
			packedData = pickle.load(inData)
	else:
		packedData = {}

	dt = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
	if not objectName in packedData.keys():
		packedData[objectName] = {"data":datum, "metadata":{}}
	else:
		packedData[objectName]["data"] = datum
	if not expiry is None:
		packedData[objectName]["metadata"]["Expiry"] = expiry
	with open(fp, 'wb') as outData:
		pickle.dump(packedData, outData, 4)


ResetCacheDirpath()
