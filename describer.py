from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import traceback
import tweepy
import requests
import urllib.parse
import datetime as dt
import os
import random
import config


def publish_to_describer(image_string):
    """Takes an image file name and publishes it to twitter with ComputerVision description"""
    # Generate the Image URL and local location
    remote_image_url = config.online_image_folder + image_string
    image_location = config.local_image_folder + image_string
    # Authenticate with Twitter
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)
    api = tweepy.API(auth)
    api.verify_credentials()
    print("Twitter Authentication OK")
    # Connect to ComputerVision
    subscription_key = config.subscription_key
    endpoint = config.endpoint
    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    description_results = computervision_client.describe_image(remote_image_url)
    # Get the captions (descriptions) from the response, with confidence level
    tweet = ''
    print("Description of remote image: ")
    if len(description_results.captions) == 0:
        print("No description detected.")
    else:
        for caption in description_results.captions:
            print("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))
            tweet = caption.text
    # Upload image
    media = api.media_upload(image_location)
    # Post tweet with image
    api.update_status(status=tweet, media_ids=[media.media_id])


def send_tel_update(message):
    parsetext = urllib.parse.quote_plus(message)
    requests.get("https://api.telegram.org/" + config.bot_id
                 + "/sendMessage?chat_id=" + config.chat_id + "&text={}".format(parsetext))


def update_error_log(message):
    with open("error_log.txt", "a") as f:
        f.write(str(dt.datetime.now()))
        f.write('\n')
        f.write(message + "\n")
    f.close()


def main():
    """Selects a random jpeg file, publishes it, logs it, deletes it"""
    file = ''
    count = 0
    while count < 10 and not file.endswith('.jpeg'):
        file = random.choice(os.listdir(config.local_image_folder))
        count += 1
    if count == 10:
        send_tel_update('An error occurred on Describer. You might need to upload more photos.')
        return
    t = str(dt.datetime.now())
    publish_to_describer(file)
    with open(config.local_image_folder + 'log_sent_photos.txt', 'a') as log:
        log.write(file + ' ' + t + '\n')
    os.remove(config.local_image_folder + file)


if __name__ == '__main__':
    current_hour = dt.datetime.utcnow().hour
    try:
        if current_hour in [1, 17]:  # Allows change of post frequency without updating cron (w/ cron calling hourly)
            main()
    except Exception as e:
        x = str(e)
        y = ''.join(traceback.format_exc())
        send_tel_update('Describer encountered an error.')
        update_error_log('Describer' + x+y)
