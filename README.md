# witcher3-maya-animation
These Maya tools allow the creation of json files that describe Witcher 3 animations. [Wolven-kit](https://github.com/Traderain/Wolven-kit) can then be used to import the json animations into Witcher 3 formats.
![](https://i.imgur.com/KM1cfrR.jpg)

## Features

In particular you can : 
- Import and export w2anims.json (bone and track animation)
- Import and export w2cutscene.json (multipart bone and track animation that describe full cutscenes) (Exporting ability in progress)
- Import and export w2rig.json (skeletons)
- Import and export w3fac.json (face skeleton and face pose library)


## Tutorials and Links
- [Mega folder with example json animations](https://mega.nz/folder/KMBHBQzZ#aLQCsUk0OZ50QSCJzWeuIw)
- [Viewing and Exporting Witcher 3 Animations in Maya 2020](https://github.com/dingdio/witcher3-maya-animation/wiki/Viewing-and-Exporting-Witcher-3-Animations-in-Maya-2020)
- [Importing JSON Animations With Wolven kit](https://github.com/dingdio/witcher3-maya-animation/wiki/Importing-JSON-Animations-With-Wolven-kit)
- [Wolven-kit](https://github.com/Traderain/Wolven-kit)

## Installation

1. Download and unzip the *witcher3.zip* file from [github releases](https://github.com/dingdio/witcher3-maya-animation/releases) or clone this git.

2. Drag and drop the "witcher3/install.mel" file onto the Maya viewport.

3. Click the Witcher 3 Tools icon on the shelf to run.


## Manual Installation

Add src/witcher3 folder to your maya scripts directory, start Maya and run the following code in the Python script editor.

```
import witcher3
reload(witcher3)
witcher3.w3tool.RedManager(dock=False)
```


