#!/usr/bin/env python3
import houndify
import argparse
import sys
import time
import wave
import json

BUFFER_SIZE = 256

#
# Simplest HoundListener; just print out what we receive.
# You can use these callbacks to interact with your UI.
#
class MyListener(houndify.HoundListener):
  def __init__(self):
    pass
  def onPartialTranscript(self, transcript):
    print("Partial transcript: " + transcript)
  def onFinalResponse(self, response):
    print("Final response:")
    print(json.dumps(response, indent=2, sort_keys=True, ensure_ascii=False))
  def onError(self, err):
    print("Error: " + str(err))

def check_audio_compatibility(audio):
  if audio.getsampwidth() != 2:
    print("{}: wrong sample width (must be 16-bit)".format(fname))
    sys.exit()
  if audio.getframerate() != 8000 and audio.getframerate() != 16000:
    print("{}: unsupported sampling frequency (must be either 8 or 16 khz)".format(fname))
    sys.exit()
  if audio.getnchannels() != 1:
    print("{}: must be single channel (mono)".format(fname))
    sys.exit()


def send_audio_file(audio_file, client_id, client_key):
  audio = wave.open(audio_file)
  check_audio_compatibility(audio)


  client = houndify.StreamingHoundClient(client_id, client_key, "test_user")
  client.setLocation(37.388309, -121.973968)
  client.setSampleRate(audio.getframerate())
  
  client.start(MyListener())
  
  while True:
    chunk_start = time.time()
  
    samples = audio.readframes(BUFFER_SIZE)
    chunk_duration = float(len(samples)) / (audio.getframerate() * audio.getsampwidth())
    if len(samples) == 0: break
    if client.fill(samples): break
  
    # # Uncomment the line below to simulate real-time request
    # time.sleep(chunk_duration - time.time() + chunk_start)

  audio.close()
  response = client.finish() # returns either final response or error
  return response


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('AUDIO_FILE', type=str,
                      help='Audio .wav file to be sent to the server')
  parser.add_argument('--endpoint', '-e', default='https://api.houndify.com/v1/audio',
                      help="The endpoint the SDK will hit to query Houndify.")
  parser.add_argument('--client-id', '-id', required=True,
                      help="Houndify client ID")
  parser.add_argument('--client-key', '-key', required=True,
                      help="Houndify client Key")

  args = parser.parse_args()

  response = send_audio_file(args.AUDIO_FILE, args.client_id, args.client_key)

