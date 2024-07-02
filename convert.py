import os
from moviepy.editor import *
from PIL import Image, ImageOps

# Ruta del directorio que contiene los archivos
directory_path = "./"

# Obtener listas de archivos JPG y M4A
image_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.jpg')]
audio_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.m4a')]

# Ordenar las listas si es necesario
image_files.sort()
audio_files.sort()

# Verificar que las listas tengan la misma longitud
if len(image_files) != len(audio_files):
    print("Las listas de imágenes y audios no tienen la misma longitud.")
else:
    print(image_files)
    print(audio_files)
    # Crear videos para cada par de archivos
    for i, (image_file, audio_file) in enumerate(zip(image_files, audio_files)):
        try:
            # Cargar el archivo de audio
            audio = AudioFileClip(os.path.join(directory_path, audio_file))
            duration = audio.duration

            # Redimensionar la imagen manteniendo la proporción original y añadir bordes si es necesario
            img = Image.open(os.path.join(directory_path, image_file))
            img = ImageOps.fit(img, (1280, 720), Image.LANCZOS, centering=(0.5, 0.5))  # Ajusta el tamaño deseado aquí
            resized_image_file = os.path.join(directory_path, f"resized_{image_file}")
            img.save(resized_image_file)

            # Crear un clip de imagen con la misma duración que el audio
            image_clip = ImageClip(resized_image_file).set_duration(duration)

            # Añadir el audio al clip de imagen
            video_clip = image_clip.set_audio(audio)

            # Exportar el video con opciones adicionales
            output_file = os.path.join(directory_path, audio_file+".mp4")
            video_clip.write_videofile(
                output_file,
                fps=24,
                codec='libx264',       # Codec de video
                audio_codec='aac',     # Codec de audio
                temp_audiofile='temp-audio.m4a',  # Archivo temporal para el audio
                remove_temp=True,      # Eliminar archivos temporales después de la exportación
                preset='ultrafast',    # Preset de FFmpeg para exportación rápida
                threads=4              # Número de threads para la exportación
            )
            print(f"Video {audio_file} exportado exitosamente.")
            # Eliminar el archivo de imagen redimensionado
            os.remove(resized_image_file)
        except Exception as e:
            print(f"Ocurrió un error al procesar {image_file} y {audio_file}: {e}")
