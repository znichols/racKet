racKet
=======

A library to transform events into sounds 


RacKet is a library for transforming data events into audio. The purpose of this library is to provide a simiple and usuable tool that empowers developers and scientists to hear their data. This could be useful in multiple ways:


1) Bring your attention to a process running in the background. Think of it as an advanced bell feature that is availible at run time instead of at the completion of a process. 
1) Find clusters or paterns of events in a large data set. 
  * token replacement might be useful. Use language instead of tones
  * a data event that makes a threshold could fire multiple sounds to give a better context

# Setup dependencies:

```bash
# pre requisites for pygame
brew install sdl sdl_image sdl_mixer sdl_ttf portmidi 
# smpeg is at tap homebrew/headonly
brew tap homebrew/headonly
brew install --HEAD smpeg

pip install hg+http://bitbucket.org/pygame/pygame

# install open cv
brew tap homebrew/science
# this is kinda big
brew install opencv
```

# running racKet Server Instructions
```bash
cd SoundEngine/
python SoundEngine.py ../resources/config.json
# stop with ctrl-C

```

# To run the Video Capture Client
```bash
cd ../DataProcessor
python VideoClient.py ../resources/config.json

```

# To run a csv client interactively
## start at the root of the project and run ipython or python
```bash
ipython
```
## In python you can run the following script
```python
# See DataProcessor.py for the csv data client

from DataProcessor import DataProcessor
# instantiate a data processor client
ds=DataProcessor.DataProcessor('resources/config.json')
# use the import_csv_file method to load the data
ds.import_csv_file('../resources/mock_data.csv');
# send the data to the server
ds.send_data(4)
```


