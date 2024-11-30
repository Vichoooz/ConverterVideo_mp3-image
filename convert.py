import os
from moviepy.editor import *
from PIL import Image, ImageOps
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

def autenticar_youtube():
    """Autentica al usuario con la API de YouTube y devuelve un objeto de servicio."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

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

def upload_video(file_path, title, description, tags=None, category_id="22", privacy_status="private"):
    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
    response = request.execute()
    print(f"Video subido exitosamente. ID del video: {response['id']}")
    return f"https://www.youtube.com/watch?v={response['id']}"

# Definir ruta de salida y autenticación
output_directory = "./output_videos/"
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Crear videos y subirlos
VideoImagenConverter(output_directory)
youtube = autenticar_youtube()
print("Autenticación exitosa")

# Escribir links en archivo
with open("link.txt", "w") as archivo:
    for file in os.listdir(output_directory):
        if file.endswith(".mp4"):
            file_path = os.path.join(output_directory, file)
            title = file[:-10] + " - Moises Muñoz"  # Remueve los últimos 10 caracteres
            description = "Fotografías de Moises Muñoz con música de fondo."
            tags = ["Musica", "Fotografia", "Moises Muñoz"]
            link = upload_video(file_path, title, description, tags=tags, privacy_status="private")
            archivo.write(link + "\n")
