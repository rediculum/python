#!/usr/bin/python3
#
# This is a PRTG Python custom sensor for Netflix' Eureka Service Discovery
# It comes with no warranty, so use at your own risk

import urllib.request
import sys
import datetime
import json
import xml.etree.ElementTree as ET

space = ' '
data = json.loads(sys.argv[1])
prtg_params = data['params']
url = prtg_params.replace("\\", "")
result = []
failText = ''
finalResult = []
error = 0
failed = False

def prtg_error(rc, msg):
  print(json.dumps({'prtg': {'error': rc, 'text': msg}}))
  exit(rc)

def request():
  global error
  global finalResult
  global failed
  global failText
  count = 0
  failCount = 0
  root = ET.fromstring(urllib.request.urlopen(url).read())

  for app in root.iter('application'):
    value = 1
    appName =  app.find('name').text
    for inst in app.iter('instance'):
      count += 1
      instId =  inst.find('instanceId').text
      status =  inst.find('status').text
      for lease in inst.iter('leaseInfo'):
        lastRenew =  lease.find('lastRenewalTimestamp').text
        if status != "UP":
          lastEpoch = datetime.datetime.fromtimestamp(int(lastRenew)/1000)
          lastTime = lastEpoch.strftime('%d.%m.%Y %H:%M:%S')
          failedInst = ("InstanceID",instId,"of application",appName,"absent. Last seen:",lastTime,"|")
          failText = failText + space.join(failedInst)
          failed = True
          failCount += 1
    if status != "UP":
      value = 0
    result.append({'channel': appName, 'value': value})

  if failed:
    error = 1

  statusValue = round((count - failCount) / count * 100)
  finalResult = [{'channel': 'Status', 'value': int(statusValue), 'unit': 'Percent'}]
  finalResult.extend(result)

try:
  result.append(request())
except Exception as e:
  prtg_error(3, str(e))

print(json.dumps({'prtg': {'error': error, 'text': failText, 'result': finalResult}}))
