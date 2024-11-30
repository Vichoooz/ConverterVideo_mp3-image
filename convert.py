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
    # El archivo token.json almacena el acceso del usuario y los tokens de actualización, y se
    # crea automáticamente cuando el flujo de autorización se completa por primera vez.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Si no hay credenciales (válidas) disponibles, deja que el usuario inicie sesión.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Guarda las credenciales para la próxima ejecución
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

def VideoImagenConverter(output_directory): 

    # Ruta del directorio que contiene los archivos
    directory_path = "./"

    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Obtener listas de archivos JPG y M4A
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.jpg')]
    audio_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.m4a')]

    # Ordenar las listas si es necesario
    image_files.sort()
    audio_files.sort()

    # Verificar que las listas tengan la misma longitud
    if len(image_files) != len(audio_files):
        print("Las listas de imágenes y audios no tienen la misma longitud.")
        return False
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

                # Definir el nombre del archivo de salida en la carpeta deseada
                output_file = os.path.join(output_directory, audio_file + ".mp4")

                # Exportar el video con opciones adicionales
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
                print(f"Video {audio_file} exportado exitosamente en {output_file}.")
                
                # Eliminar los archivos temporales
                os.remove(resized_image_file)
                os.remove(image_file)
                os.remove(audio_file)
                return True

            except Exception as e:
                print(f"Ocurrió un error al procesar {image_file} y {audio_file}: {e}")
                return False


def upload_video(file_path, title, description, tags=None, category_id="22", privacy_status="private"):
    """
    Subir un video a YouTube usando la API de YouTube.

    :param file_path: Ruta del archivo de video a subir
    :param title: Título del video
    :param description: Descripción del video
    :param tags: Lista de etiquetas (opcional)
    :param category_id: ID de la categoría del video (por defecto "22" que corresponde a 'People & Blogs')
    :param privacy_status: Estado de privacidad del video ('public', 'private', 'unlisted')
    :return: Response del video subido
    """


    # Preparar el archivo de video para ser subido
    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)

    # Definir la solicitud para subir el video
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status  # Puedes cambiarlo a 'public' o 'unlisted'
        }
    }

    # Realizar la subida
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    # Subir el video de forma resumible
    response = request.execute()

    print(f"Video subido exitosamente. ID del video: {response['id']}")
    video_url = f"https://www.youtube.com/watch?v={response['id']}"
    return video_url




# Ruta de la carpeta donde se guardarán los videos
output_directory = "./output_videos/"

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

VideoImagenConverter(output_directory)

    
# Autenticar al usuario con la API de YouTube
youtube = autenticar_youtube()
print("Autenticación exitosa")

# Subir el video a YouTube
for file in os.listdir(output_directory):
    if file.endswith(".mp4"):
        file_path = os.path.join(output_directory, file)
        title = file.title()[:-10] + " - Moises Muñoz"
        description = "Fotografías de Moises Muñoz con música de fondo."
        tags = ["Musica", "Fotografia", "Moises Muñoz"]
        link = upload_video(file_path, title, description, tags=tags, privacy_status="public")
        archivo = open("link.txt", "w")
        archivo.write(link)
archivo.close()