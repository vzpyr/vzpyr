from PIL import Image, ImageSequence
import os

def stack(target_width=100, target_height=944):
    gif_files = [f for f in os.listdir('.') if f.lower().endswith('.gif') and f != 'stacked_gif.gif']
    if not gif_files:
        print("[-] no gifs found")
        return
    resized_frames_list = []
    heights = []
    all_durations = []
    for gif_file in gif_files:
        try:
            with Image.open(gif_file) as gif:
                frames = []
                width, height = gif.size
                aspect_ratio = height / width
                new_height = int(target_width * aspect_ratio)
                heights.append(new_height)
                for frame in ImageSequence.Iterator(gif):
                    resized_frame = frame.resize((target_width, new_height), Image.Resampling.LANCZOS)
                    frames.append(resized_frame)
                    all_durations.append(gif.info.get('duration', 100))
                resized_frames_list.append(frames)
        except Exception as e:
            print(f"[-] error processing {gif_file}: {e}")
            return
    stacked_frames = []
    max_frame_length = max(len(frame_list) for frame_list in resized_frames_list) if resized_frames_list else 0
    for frame_index in range(max_frame_length):
        new_frame = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 255))
        y_offset = 0
        for i, frame_list in enumerate(resized_frames_list):
            if frame_index < len(frame_list):
                current_frame = frame_list[frame_index]
            elif len(frame_list) > 0:
                current_frame = frame_list[-1]
            if y_offset < target_height:
                paste_height = min(current_frame.height, target_height - y_offset)
                if paste_height > 0:
                    cropped_frame = current_frame.crop((0, 0, target_width, paste_height))
                    new_frame.paste(cropped_frame, (0, y_offset))
            
            y_offset += heights[i]
        stacked_frames.append(new_frame)
    if stacked_frames:
        stacked_frames[0].save(
            'stacked_gif.gif',
            save_all=True,
            append_images=stacked_frames[1:],
            duration=100,
            loop=0
        )
        print(f"[+] {len(gif_files)} gif(s) stacked to stacked_gif.gif")
    else:
        print("[-] no savable frames")

if __name__ == "__main__":
    stack()