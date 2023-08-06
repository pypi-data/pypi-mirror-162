#!/usr/bin/env python3
import houndify
import sys



CLIENT_ID = sys.argv[1]
CLIENT_KEY = sys.argv[2]
BUFFER_SIZE = 512

#
# Simplest HoundListener; just print out what we receive.
# You can use these callbacks to interact with your UI.
#
class MyListener(houndify.HoundListener):
  def onPartialTranscript(self, transcript):
    print("Partial transcript: " + transcript)
  def onFinalResponse(self, response):
    print("Final response: " + str(response))
  def onError(self, err):
    print("Error: " + str(err))


client = houndify.StreamingHoundClient(CLIENT_ID, CLIENT_KEY, "test_user", enableVAD = True)
client.setLocation(37.388309, -121.973968)

client.start(MyListener())

while True:
  samples = sys.stdin.buffer.read(BUFFER_SIZE)
  if len(samples) == 0: break
  if client.fill(samples): break
  
client.finish()
