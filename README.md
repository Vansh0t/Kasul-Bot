# Kasul-Bot



Kasul Bot is easy to deploy audio bot made with [discord.py](https://github.com/Rapptz/discord.py) and [pytube](https://github.com/pytube/pytube). It has a convenient web ui controls feature, check it out [here](https://github.com/Vansh0t/Kasul-Bot-Web-Controls)

Kasul Bot doesn't depend on the single bot instance to serve audio. In fact you create your own bot on Discord Developer Portal (see 'Installation' below) and just pass its id to config.ini of Kasul Bot, that's all, no coding required. This means you use your own dedicated server or PC only for your discord servers to avoid performance and stability issues of many popular servers.

## Features
- Playing audio from YouTube url
- Audio queue management
- Timecodes support
- Slash Commands support
- (Opt) [Web Controls UI](https://github.com/Vansh0t/Kasul-Bot-Web-Controls)

## Installation
Discord treats all bots individualy so in order to be able to host a personal bot on your on server or PC you have to register it first on Discord Developer Portal.
1. Go to https://discord.com/developers/applications
2. Create 'New Application'
3. (Opt) Add tags and description
4. Go to 'Bot' tab, 'Add Bot'
5. 'Copy' Bot Token and paste it in config.ini file in 'Token' field
6. Go to 'OAuth2'->'General' tab
7. Set 'Scopes' as shown below
![image](https://user-images.githubusercontent.com/35566242/148388614-94eb7869-29f0-459f-9ca2-d9e63e20de3b.png)
8. Set 'Bot Permissions' as shown below
![image](https://user-images.githubusercontent.com/35566242/148388794-484f6ec9-0f81-4400-83a2-419c7f11f896.png)
9. Go to 'OAuth2'->'URL Generator' tab
10. In 'Scopes' check 'bot' and 'applications.commands'
11. In 'Bot Permissions' set everything as shown in step 8
12. Copy link and save it somewhere, then open the link in your browser and add bot to a server
13. Launch Kasul Bot, it should be ready for use
14. (Opt) Install [Web Controls UI](https://github.com/Vansh0t/Kasul-Bot-Web-Controls)
