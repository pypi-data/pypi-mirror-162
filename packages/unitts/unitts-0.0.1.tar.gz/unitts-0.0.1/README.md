# unitts
a integrated tts api for difference platform and difference tts driver

## Dependents

* [text2sentences](https://pypi.org/project/text2sentences/)

## Installation

```
pip install unitts
```

## Usage

```
import unitts

tts = unitts.init(driverName)
tts.say(text, pos=0)

```
if the tts driver need a setup parameters like appkey, 
you should do it before unitts.init() is called

## supported drivers

* [macosx_tts](https://pypi.org/project/macos_tts/)

* [baidu_tts](https://pypi.org/project/baidu_tts/)

* [android_tts](https://pypi.org/project/android_tts/)

* [ios_tts](https://pypi.org/project/ios_tts/)

Some of the drivers need setup it owns parameters before 
unitts.init() called, please refer to the drivers documents for detail


