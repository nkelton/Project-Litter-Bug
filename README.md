# Project-Litter-Bug
## What is this?
Software to randomly generate content. It's built utilizing open source projects like [MoviePy](https://zulko.github.io/moviepy/) and [Channels](https://github.com/linuxlewis/channels-api) as well as [YouTube](https://github.com/ytdl-org/youtube-dl), [Giphy](https://github.com/Giphy/giphy-python-client), [Pixabay](https://github.com/momozor/python-pixabay), and [Freesound](https://github.com/MTG/freesound-python) APIs
## How it works?

1. Download 
    - The script begins by downloading content from the aforementioned APIs. It searches for content from these services by generating random search terms for each service. The number of content downloaded is also randomly selected within a defined range
2. Randomize
    - Once all the content has been downloaded, the script begins iterating through the downloaded videos. Each video is first cut into a randomly selected interval between 3-12 seconds. The clip is then modified by a series of (you guessed it) random effects made available by MoviePy. Next, the clips are decorated by adding “screens,” pictures, gifs, and sound effects.

    - The “screens” are resized and rotated versions of the initial clip. Each screen is once again sent through the modification process so that no two screens are alike. Finally, coordinates are generated and the screen is slapped onto the initial clip. The number of screens attached to a clip is randomly selected within a defined range.

    - Similarly, each gif and picture is resized then, with coordinates randomly generated, haphazardly slapped onto the initial clip, which creates the collage-style look. The sound effects, however, are fitted to the length of the clip and overlaid across the clips original audio, creating a composition of mangled sound.

    - Finally, when all the videos have been cut into clips and decorated, they are combined into a single video and the intro is created. The resulting video is then downloaded as an mp4 file.
3. Upload
    - Before the upload process can begin, the script determines the size of the newly generated video. Then, it creates a thumbnail and description for the video. Once these processes are complete, the video is uploaded to YouTube
4. Clean Up
    - Lastly, the downloaded content (including the newly generated video) are removed from the system and the process is ready to begin again!


[Check out the videos!](https://www.youtube.com/channel/UChAlnk3z4GbtQ_rFxgpu4Bw)

![](https://media.giphy.com/media/dsX6xSNT82kt3oGrOy/giphy.gif)

![](https://media.giphy.com/media/QTspD9iS0QNazjKmtV/giphy.gif)

![](https://media.giphy.com/media/M9lacZw9XbOkdrqHTU/giphy.gif)

