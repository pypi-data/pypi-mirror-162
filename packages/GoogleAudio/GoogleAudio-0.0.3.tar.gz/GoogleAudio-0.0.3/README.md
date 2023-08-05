# GoogleColabAudio

This is a Python package for easy building audio files by using a google colab microphone
 and saving it in wav format needed for any processing application 

## Installation

```
!pip install GoogleAudio==0.0.3

```

## Tutorial
```
from googleaudio import colabaudio as agoogle #import modules
audio_name='audio.wav' # file audio name
audio,sr=agoogle.get_audio() #read audio data and simple rate
agoogle.saveaudio(audio_name,audio,sr)  # save it 
```

[Colab Google Drive](https://colab.research.google.com/drive/1Psbxt9VZQuY7odMbGF6Lezo7oGuyercl?usp=sharing)

```
u can see tutorial in colab google drive

```
