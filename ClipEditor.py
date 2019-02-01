import glob
import logging
import random
import moviepy.video.fx.all as vfx
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.video.VideoClip import ImageClip, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

import config

logger = config.set_logger('ClipEditor.py')


class ClipEditor(object):
    def __init__(self, vid_num, gif_num, pic_num, sfx_num, result_path):
        self.vid_num = vid_num
        self.gif_num = gif_num
        self.pic_num = pic_num
        self.sfx_num = sfx_num
        self.result_path = result_path
        
        self.final_clip = None
        self.clips = []
        self.interval_lst = []

    def create_clip(self):
        logger.info('Creating clip...')

        def name(vid):
            return vid[vid.rfind('/') + 1:-4]

        vid_lst = glob.glob(config.VID_PATH + '*.mp4')
        for vid in vid_lst:
            vid_name = name(vid)
            for interval in self.interval_lst:
                if interval[0] == vid_name:
                    clip = VideoFileClip(vid).subclip(interval[1], interval[2]).resize((1280, 720))
                    clip = self.modify_clip(clip)
                    clip = self.decorate_clip(clip)
                    self.add_clip(clip)

    @staticmethod
    def modify_clip(clip):
        logger.info('Modifying clip...')
        m_type = random.randint(0, 3)

        if m_type == 0:
            m_clip = (clip.fx(vfx.mirror_y)
                      .fx(vfx.colorx, factor=random.randint(0, 50)))
            # .fx(vfx.painting, saturation=random.uniform(0, 5), black=random.uniform(0, 0.01)))
        elif m_type == 1:
            m_clip = (clip.fx(vfx.invert_colors)
                      .fx(vfx.colorx, factor=random.randint(0, 50))
                      .fx(vfx.gamma_corr, gamma=random.uniform(0, 5)))

        elif m_type == 2:
            m_clip = (clip.fx(vfx.blackwhite)
                      .fx(vfx.gamma_corr, gamma=random.uniform(0, 5)))
        else:
            m_clip = (clip.fx(vfx.invert_colors)
                      .fx(vfx.mirror_y)
                      .fx(vfx.gamma_corr, gamma=random.uniform(0, 5)))
            # .fx(vfx.painting, saturation=random.uniform(0, 5), black=random.uniform(0, 0.01)))
        return m_clip

    def decorate_clip(self, clip):
        logging.info('Decorating clip...')
        clip = self.add_screens(clip)
        clip = self.add_pics(clip)
        clip = self.add_gifs(clip)
        clip = self.add_sfx(clip)
        return clip

    def add_screens(self, clip):
        logger.info('Adding screens...')
        screen_num = random.randint(3, 7)
        screen_clip = [clip]
        for i in range(screen_num):
            x_pos, y_pos, x_size, y_size = self.generate_coordinates(clip)
            screen = clip.volumex(0).resize((x_size, y_size)) \
                .set_pos((x_pos, y_pos)).add_mask().rotate(random.randint(-180, 180))
            screen = self.modify_clip(screen)
            screen_clip.append(screen)
        return CompositeVideoClip(screen_clip)

    def add_gifs(self, clip):
        logger.info('Adding gifs...')
        gif_clip = [clip]
        for i in range(self.gif_num):
            x_pos, y_pos, x_size, y_size = self.generate_coordinates(clip)
            gif_path = config.GIF_PATH + str(i) + '.gif'
            gif = VideoFileClip(gif_path).loop(duration=clip.duration).set_duration(clip.duration) \
                .fx(vfx.mask_color, color=[255, 255, 255]) \
                .resize((x_size, y_size)).set_pos((x_pos, y_pos))
            gif_clip.append(gif)
        return CompositeVideoClip(gif_clip)

    def add_pics(self, clip):
        logger.info('Adding pics...')
        pic_clip = [clip]
        for i in range(self.pic_num):
            x_pos, y_pos, x_size, y_size = self.generate_coordinates(clip)
            pic_path = config.PIC_PATH + str(i) + '.jpg'
            pic = ImageClip(pic_path).set_duration(clip.duration).resize((x_size, y_size)) \
                .set_pos((x_pos, y_pos)).add_mask().rotate(random.randint(-180, 180))
            pic_clip.append(pic)
        return CompositeVideoClip(pic_clip)

    def add_sfx(self, clip):
        logger.info('Adding sfx...')
        new_audio = [clip.audio]
        for i in range(self.sfx_num):
            sfx_path = config.SFX_PATH + str(i) + '.mp3'
            sfx_clip = AudioFileClip(sfx_path)

            if sfx_clip.duration > clip.duration:
                sfx_clip = sfx_clip.set_duration(clip.duration)
                new_audio.append(sfx_clip)
            else:
                new_audio.append(sfx_clip)

        return clip.set_audio(CompositeAudioClip(new_audio))

    @staticmethod
    def generate_coordinates(clip):
        logger.info('Generating coordinates...')
        x_pos = random.randint(0, clip.w - 100)
        y_pos = random.randint(0, clip.h - 100)
        x_size = random.randint(100, clip.w)
        y_size = random.randint(100, clip.h)
        return x_pos, y_pos, x_size, y_size

    def download_result(self):
        logger.info('Downloading result...')
        self.set_final_clip()
        self.add_intro()
        logger.info('Writing final clip...')
        self.final_clip.write_videofile(self.result_path, verbose=False, progress_bar=True)

    def add_intro(self):
        logger.info('Adding intro...')
        intro = self.generate_intro()
        new_final_clip = concatenate_videoclips([intro, self.get_final_clip()], method='compose')
        self.update_final_clip(new_final_clip)

    def generate_intro(self):
        logger.info('Generating intro...')
        color = (255, 255, 255)
        size = (1280, 720)
        clip = ColorClip(size, color, duration=3)
        logo = ImageClip(config.LOGO_PATH).set_duration(clip.duration) \
            .resize(width=400, height=200) \
            .set_pos(('center', 'center'))
        return CompositeVideoClip([clip, logo])

    def add_clip(self, clip):
        logger.info('Adding clip...')
        self.clips.append(clip)

    def set_interval_lst(self, lst):
        logger.info('Setting interval list...')
        self.interval_lst = lst

    def get_final_clip(self):
        logger.info('Getting final clip...')
        return self.final_clip

    def set_final_clip(self):
        logger.warning('Setting final clip...')
        self.final_clip = concatenate_videoclips(self.clips, method='compose').resize((1280, 720))

    def update_final_clip(self, clip):
        logger.warning('Updating final clip...')
        self.final_clip = clip
