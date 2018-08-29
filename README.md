# VideoGameEngineLearning
Code and example for video game engine learning as described in the 2017 IJCAI paper "Game Engine Learning from Gameplay Video"

Step 0: Setup (Starting file sample, e.g. n number of PNGs or video
    - e.g. Moorio.MP4, or even better, the play-through from Mario
    - any version of Python will work 
    - need to have ffmpeg, numpy, and pillow installed as described https://github.com/mguzdial3/VideoParser

 Step 1: VideoParser.py
    - there are no parameters by default, but there are commented places in the code to change (e.g. line 16) for slower, more accurate results
    - run-time is dependent on the length of the video and computer, but fairly quick (<<1 second per frame)
    - the file outputs will be saved directly to file, each frame of the input video (e.g. image-00000001.png)

 Step 2: findChanges.py 
    - any switches/parameters? you'll need to make sure the folder name(s) at the top of the file are accurate to wherever the frame images were saved, lines 5 to 13
    - expected run-time? Dependent on the length of the video and computer, but slightly slower than before (<1 second per frame)
    - file outputs? longplay5/frame5Descriptions1-1.csv on the github VideoGameEngineLearning

 Step 3: EngineLearning.py
    - any switches/parameters? lines 10 through 17, each should be self-evident or commented
    - expected run-time? Right now a very long time, the exact amount will vary video to video and based on minVal but can range up to a week on an older CPU for a five minute value
    - file outputs? Engines/partialEngine455.p (attached)

Step 3b: parallelEngineLearning.py
    - Run this as an alternative if you have multiple videos to learn from (not currently set up for multi threading but should be straight forward
    - same as above

 Step 5: mergeEngines.py (only necessary if you run Step 3b or Step 3 over different start/end frame subsections otherwise just take the final output)
    - any switches/parameters? Ensure that line 10 is set to the directory with all the engines
    - expected run-time? Dependent on the number of engines to merge and rules learned, O(engines*rules*rules)
    - file outputs? line 78, a merged pickle representation of a single set of learned rule
