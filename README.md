# Twitter Photo Describer Bot
The Twitter Photo Describer Bot tweets photos you provide it with descriptions provided by Microsoft Azure
 ComputerVision.

## Installing
Install via git.
```bash
git clone https://github.com/coldbrewdev/twitter-photo-describer-bot
```
## Configuration
A config-sample.py file is provided. 
### File System Setup
You are required to maintain a folder of photos for the bot to post. The basic workflow for the bot is:
1. Select a random image from a local FOLDER
1. Pass a URL for that photo to the ComputerVision API to obtain a description
1. Upload the local FILE of the image with the description onto twitter
1. Delete the FILE and log that it was posted

Since the ComputerVision API requires a URL and the Twitter API requires a file upload, your system should be setup
 with the photos stored in a folder accessible via http.

### APIs
To complete the config file, you'll need access to the [Twitter API](https://developer.twitter.com/en/docs) and the
 [Microsoft Azure ComputerVision API](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/client-library?tabs=visual-studio&pivots=programming-language-python).

### Required Packages
The script requires tweepy,

```bash
pip install tweepy
```

and various modules for Microsoft Azure, 
```bash
pip install --upgrade azure-cognitiveservices-vision-computervision
```
which also require Pillow

```bash
pip install pillow
```

### Scheduling

The bot is currently configured to be called once an hour, with this code: 
```python:
current_hour = dt.utcnow().hour
...
if current_hour in [1, 17]:...
```
in the describer.py file to allow for easy
 changes to post frequency.

### Example
The bot can be seen in action on the [@Dis_Describer](https://twitter.com/dis_describer) twitter account.