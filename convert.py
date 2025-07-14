import os
from moviepy.editor import *
from PIL import Image, ImageOps

def VideoImagenConverter(output_directory): 
    directory_path = "./"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.jpg')]
    audio_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.m4a')]

    image_files.sort()
    audio_files.sort()

    if len(image_files) != len(audio_files):
        print("Las listas de imágenes y audios no tienen la misma longitud.")
        print(f"Imágenes: {len(image_files)}")
        print(f"Audios: {len(audio_files)}")
        return False

    for i, (image_file, audio_file) in enumerate(zip(image_files, audio_files)):
        try:
            audio = AudioFileClip(os.path.join(directory_path, audio_file))
            duration = audio.duration

            img = Image.open(os.path.join(directory_path, image_file))
            img = ImageOps.fit(img, (1280, 720), Image.LANCZOS, centering=(0.5, 0.5))
            resized_image_file = os.path.join(directory_path, f"resized_{image_file}")
            img.save(resized_image_file)

            image_clip = ImageClip(resized_image_file).set_duration(duration)
            video_clip = image_clip.set_audio(audio)

            output_file = os.path.join(output_directory, audio_file + ".mp4")

            video_clip.write_videofile(
                output_file,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='ultrafast',
                threads=4
            )
            print(f"Video {audio_file} exportado exitosamente en {output_file}.")

            os.remove(resized_image_file)
            os.remove(image_file)
            os.remove(audio_file)
        except Exception as e:
            print(f"Ocurrió un error al procesar {image_file} y {audio_file}: {e}")

# Definir ruta de salida y autenticación
output_directory = "./output_videos/"

VideoImagenConverter(output_directory)
