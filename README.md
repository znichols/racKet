tweeter
=======

A library to transform events into sounds 

Tweeter is a library for transforming data events into audio. The purpose of this library is to provide a simiple and usuable tool that empowers developers and scientists to hear their data. This could be useful in multiple ways:
1) Bring your attention to a process running in the background. Think of it as an advanced bell feature that is availible at run time instead of at the completion of a process. 
2) Find clusters or paterns of events in a large data set. 
  * token replacement might be useful. Use language instead of tones
  * a data event that makes a threshold could fire multiple sounds to give a better context


To get the server running:
    cd SoundEngine
    python SoundEngine.py ../resources/config.json

To run the Video Capture Client
    cd DataProcessor
    python VideoClient.py ../resources/config.json

stop with ctrl-C

See DataProcessor.py for the csv data client
