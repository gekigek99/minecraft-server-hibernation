# Minecraft Server Hibernation

[![mvsh - license](https://img.shields.io/github/license/gekigek99/minecraft-server-hibernation?color=6fff00)](https://github.com/gekigek99/minecraft-vanilla-server-hibernation)
[![mvsh - stars](https://img.shields.io/github/stars/gekigek99/minecraft-server-hibernation?color=ffbd19)](https://github.com/gekigek99/minecraft-vanilla-server-hibernation)
[![mvsh - release](https://img.shields.io/github/release/gekigek99/minecraft-server-hibernation?color=05aefc)](https://github.com/gekigek99/minecraft-vanilla-server-hibernation)  

[![mvsh - logo](https://user-images.githubusercontent.com/53654579/90397372-09a9df80-e098-11ea-925c-29e9bdfc0b48.png)](https://github.com/gekigek99/minecraft-server-hibernation)  

version: v2.0.0 (Go)  
Copyright (C) 2019-2020 [gekigek99](https://github.com/gekigek99)  

This program supports minecraft vanilla and modded on linux and windows!

Check the [releases](https://github.com/gekigek99/minecraft-server-hibernation/releases) to download the binaries (for linux and windows)

-----
#### Vote for adding optional financial support possibilities:
https://linkto.run/p/BXYKPR5Y \
Results: https://linkto.run/r/BXYKPR5Y

-----
### INSTRUCTIONS:
This is a Golang script to start a minecraft server on request and stop it when there are no players online.
How to use:
1. Install your desired minecraft server
2. "server-port" parameter in "server.properties" should be 25565
3. Edit the parameters in config.json as needed (*check definitions*):
    - serverDirPath
    - serverFileName
    - startMinecraftServerLin or startMinecraftServerWin
    - stopMinecraftServerLin or stopMinecraftServerWin
    - *hibernationInfo and startingInfo
    - *minecraftServerStartupTime
    - *timeBeforeStoppingEmptyServer
4. *put the frozen icon you want in "path/to/server.jar/folder" (must be 64x64 and called "server-icon-frozen.png")
5. on the server: open port 25555 (example: [ufw firewall](https://www.configserverfirewall.com/ufw-ubuntu-firewall/ubuntu-firewall-open-port/))
6. on the router: forward port 25555 to server ([tutorial](https://www.wikihow.com/Open-Ports#Opening-Router-Firewall-Ports))
7. you can connect to the server through port 25555

\* = this step is NOT strictly necessary

(remember to run the script at reboot)

### DEFINITIONS:
Commands to start and stop minecraft server:
```yaml
# only text in parethesis needs to be modified
"serverDirPath": "{path/to/server/folder}",
"serverFileName": "{server.jar}",
"startMinecraftServerLin": "screen -dmS minecraftServer java {-Xmx1024M -Xms1024M} -jar serverFileName nogui",
"stopMinecraftServerLin": "screen -S minecraftServer -X stuff 'stop\\n'",
"startMinecraftServerWin": "java {-Xmx1024M -Xms1024M} -jar serverFileName nogui",
"stopMinecraftServerWin": "stop",

# if you are on linux you can access the minecraft server console with "sudo screen -r minecraftServer"
```
Personally I set up a systemctl minecraft server service (called "minecraft-server") therefore I use:
```yaml
"startMinecraftServerLin": "sudo systemctl start minecraft-server",
"stopMinecraftServerLin": "sudo systemctl stop minecraft-server",
```
Hibernation and warming up server description
```yaml
"hibernationInfo": "                   &fserver status:\n                   &b&lHIBERNATING",
"startingInfo": "                   &fserver status:\n                    &6&lWARMING UP",
```
If you are the first to access to minecraft world you will have to wait *20 seconds* and then try to connect again.
```yaml
"minecraftServerStartupTime": 20,       #any parameter more than 10s is recommended
```
*60 seconds* is the time (after the last player disconnected) that the script waits before shutting down the minecraft server
```yaml
"timeBeforeStoppingEmptyServer": 60     #any parameter more than 30s is recommended
```
-----
### CREDITS:  

Author: [gekigek99](https://github.com/gekigek99)  
Contributors: [najtin](https://github.com/najtin/minecraft-server-hibernation)  
Docker branch: [lubocode](https://github.com/gekigek99/minecraft-server-hibernation/tree/docker)  

#### If you like what I do please consider having a cup of coffee with me at:  

<a href="https://www.buymeacoffee.com/gekigek99" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

#### And remember to give a star to this repository [here](https://github.com/gekigek99/minecraft-server-hibernation)!
