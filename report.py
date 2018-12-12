from ringcentral import SDK
import time
import urllib2
import datetime
import os
from dotenv import Dotenv
dotenv = Dotenv(".env")
os.environ.update(dotenv)

platform = None

def login():
    global platform
    if os.environ.get("ENVIRONMENT_MODE") == "sandbox":
        sdk = SDK(os.environ.get("CLIENT_ID_SB"), os.environ.get("CLIENT_SECRET_SB"), 'https://platform.devtest.ringcentral.com')
        platform = sdk.platform()
        platform.login(os.environ.get("USERNAME_SB"), '', os.environ.get("PASSWORD_SB"))
    else:
        sdk = SDK(os.environ.get("CLIENT_ID_PROD"), os.environ.get("CLIENT_SECRET_PROD"), 'https://platform.ringcentral.com')
        platform = sdk.platform()
        platform.login(os.environ.get("USERNAME_PROD"), '', os.environ.get("PASSWORD_PROD"))
    CreateMessageStoreReport()

def CreateMessageStoreReport() :
    global platform
    print("create report task ...")
    endpoint = "/restapi/v1.0/account/~/message-store-report"
    dateTo = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    lessXXDays = time.time() - (84600 * 30)
    dateFrom = datetime.datetime.fromtimestamp(lessXXDays).strftime("%Y-%m-%dT00:00:00.000Z")
    params = {}
    params['dateFrom'] = dateFrom
    params['dateTo'] = dateTo
    response = platform.post(endpoint, params)
    json = response.json()
    if json.status == "Completed":
        GetMessageStoreReportArchive(json.id)
    else:
        GetMessageStoreReportTask(json.id)

def GetMessageStoreReportTask(taskId):
    global platform
    print("polling ...")
    endpoint = "/restapi/v1.0/account/~/message-store-report/" + taskId
    response = platform.get(endpoint)
    json = response.json()
    if json.status == "Completed":
        GetMessageStoreReportArchive(taskId)
    else:
        time.sleep(2)
        GetMessageStoreReportTask(taskId)

def GetMessageStoreReportArchive(taskId):
    global platform
    print("getting report uri ...")
    endpoint = "/restapi/v1.0/account/~/message-store-report/"+ taskId +"/archive"
    response = platform.get(endpoint)
    jsonObj = response.json()
    length = len(jsonObj.records)
    dateLog = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M")
    for i in range(length):
        fileName = "archives/" + dateLog + "_" + str(i) + ".zip"
        GetMessageStoreReportArchiveContent(jsonObj.records[i].uri, fileName)

def GetMessageStoreReportArchiveContent(contentUri, zipFile):
    global platform
    print("Save report zip file to archives folder.")
    uri = platform.create_url(contentUri, False, None, True);
    fileHandler = urllib2.urlopen(uri)
    with open(zipFile, 'wb') as output:
        output.write(fileHandler.read())

def main():
    login()

if __name__ == '__main__':
    main()
