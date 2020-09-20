import asyncio
import os
import subprocess
import aiohttp


TIKTOK_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.0.146.3-Gen4_12000410) '
                  'AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true'
}


async def get_video_water_url(video_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url, headers=TIKTOK_HEADERS) as get_request:
            referer = str(get_request.url)
            if 'com/v/' in referer:
                video_id = referer.split('v/')[1].split('.')[0]
            else:
                video_id = referer.split('video/')[1].split('?')[0]

            get_request_content = await get_request.content.read()
            get_request_str = str(get_request_content, 'utf-8').replace('\\', '')

            video_water_url = get_request_str.split('video":{')[1].split('["')[1].split('"')[0]

            return video_water_url, referer, video_id


async def download_video(video_url, referer, video_id):
    file_directory = 'videos/{}_water.mp4'.format(video_id)
    TIKTOK_HEADERS['referer'] = referer

    if not os.path.exists('videos'):
        os.mkdir('videos')

    async with aiohttp.ClientSession() as session:
        async with session.get(video_url, headers=TIKTOK_HEADERS) as get_video:
            video_url_content = await get_video.content.read()
            with open(file_directory, "wb") as file_stream:
                file_stream.write(video_url_content)

            return file_directory
        

async def remove_watermark(file_directory):
    new_file_directory = file_directory.replace('_water', '')
    command = ['ffmpeg', '-i', file_directory, '-filter:v', 'crop=in_w:in_h-185', '-c:a', 'copy', new_file_directory]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process.communicate()
    os.remove(file_directory)

    return new_file_directory


async def main():
    tiktok_url = input('Paste TikTok video link here: ')
    water_url, referer_url, video_id = await get_video_water_url(tiktok_url)
    print('Downloading video...')
    video_directory = await download_video(water_url, referer_url, video_id)
    print('Video downloaded. Removing watermark from the video...')
    video_directory_new = await remove_watermark(video_directory)
    print('Watermark removed. File path:', video_directory_new)


if __name__ == '__main__':
    asyncio.run(main())



