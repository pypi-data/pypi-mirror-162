# GoogleColabAudio

This is a Python package for easy building audio files by using a google colab microphone
 and saving it in wav format needed for any processing application 

## Installation

```
!pip install GoogleAudio==0.0.2

```

## Tutorial
from googleaudio import colabaudio as agoogle
audio_name='audio.wav'
audio,sr=agoogle.get_audio()
agoogle.saveaudio(audio_name,audio,sr)

[Colab Google Drivehttps://colab.research.google.com/drive/1Psbxt9VZQuY7odMbGF6Lezo7oGuyercl?usp=sharing
```
u can see tutorial in colab google drive

```
