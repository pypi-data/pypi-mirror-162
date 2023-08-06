import youtube_dl

import Scripts.aparatLinksFinder as a


class AparatDlApi():
    '''
     an api for download videos from aparat.com
    Methods
    -------
    singleVideo(link)
                    Download Single video
    playList(link)
                    Download a play-list in order
    wholeChannel(link)
                    Download the whole Channel
    '''

    @staticmethod
    def singleVideo(link, res='720p'):
        '''
        Download Single video
        :param str link
        '''

        name = a.videoTitle(link)
        thelink = a.directLink(link, res)
        ydl_opts = {
            'outtmpl': name + ".mp4",
            'retries': 999,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(
                thelink,
                download=True)

    @staticmethod
    def playList(link, res='720p'):
        '''
        Download a play-list in order
        :param str link
        '''
        # grab the palylist name
        playlistname = a.playListTitle(link)
        links = a.playListVideos(link)
        print(links)
        for key, value in links.items():
            # grab name of videos
            name = a.videoTitle(value)
            # name = "hee"
            print(name)
            # grab links of videos
            thelink = a.directLink(value, res)
            print(thelink)

            # download videos one by one
            fname = f"{playlistname}/{str(int(key + 1))} - {name}.mp4"
            ydl_opts = {
                'outtmpl': fname,
                'retries': 999,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(
                    thelink,
                    download=True)

    @staticmethod
    def selectFromPlayList(link, start=0, end=100, res='720p'):
        '''
        Download videos by selection on a play-list
        :param str link
        :param start int
        "param end int
        '''
        # TODO: dictionary items() to get range
        # grab the palylist name
        playlistname = a.playListTitle(link)
        links = a.playListVideos(link)
        print(links)
        for key, value in links.items():
            if key >= start - 1 and key <= end - 1:
                # grab name of videos
                name = a.videoTitle(value)
                # name = "hee"
                print(name)
                # grab links of videos
                thelink = a.directLink(value, res)
                print(thelink)

                # download videos one by one
                fname = f"{playlistname}/{str(int(key + 1))} - {name}.mp4"
                ydl_opts = {
                    'outtmpl': fname,
                    'retries': 999,
                }

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(
                        thelink,
                        download=True)

    @staticmethod
    def fromFile(ifile, res='720p'):
        '''
            donwlaod single video from file unlimited!


        '''

        tlinks = []
        with open(ifile) as f:
            tlinks = [line.rstrip() for line in f]
        j = 1
        for i in tlinks:
            print(j)
            AparatDlApi.singleVideo(i, res)
            j += 1

    @staticmethod
    def fromFileForList(ifile, res="720p"):
        '''
            donwlaod single video from file unlimited!


        '''
        tlinks = []
        with open(ifile) as f:
            tlinks = [line.rstrip() for line in f]
        for i in tlinks:
            AparatDlApi.playList(i, res)
