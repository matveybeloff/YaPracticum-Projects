import os

import aiohttp
import requests
from aiohttp import ClientError
from dotenv import load_dotenv

load_dotenv()

DISK_FILES_DIR = 'disk:/Приложения/Uploader/'
DISK_TOKEN = os.getenv('DISK_TOKEN')
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
DISK_INFO_URL = f'{API_HOST}{API_VERSION}/disk/'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

AUTH_HEADERS = {
    'Authorization': f'OAuth {DISK_TOKEN}'
}


def get_download_link_to_file(path: str = '') -> str:
    """Получение ссылки на скачивание файла с Я.Диска."""
    full_path = f'{DISK_FILES_DIR}{path}'
    response = requests.get(
        headers=AUTH_HEADERS,
        url=DOWNLOAD_LINK_URL,
        params={'path': full_path}
    )
    response.raise_for_status()
    data = response.json()
    if 'href' not in data:
        raise KeyError(f"{full_path}: {data}")
    return data['href']


async def _request_upload_link(session, filename):
    """Получение ссылки для загрузки файла на Я.Диск."""
    upload_path = f'{DISK_FILES_DIR}{filename}'
    payload = {'path': upload_path, 'overwrite': 'True'}
    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params=payload,
    ) as response:
        response.raise_for_status()
        data = await response.json()
    upload_url = data.get('href')
    if not upload_url:
        raise KeyError(f'{upload_path}: {data}')
    return upload_url


async def _upload_to_disk(session, upload_url, file_storage):
    """Загрузка файла на Я.Диск по ссылке."""
    stream = getattr(file_storage, 'stream', file_storage)
    if hasattr(stream, 'seek'):
        stream.seek(0)
    data = stream.read()
    async with session.put(upload_url, data=data) as response:
        response.raise_for_status()


async def _request_download_link(session, filename):
    """Получение ссылки на скачивание загруженного файла."""
    full_path = f'{DISK_FILES_DIR}{filename}'
    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': full_path},
    ) as response:
        response.raise_for_status()
        data = await response.json()
    download_url = data.get('href')
    if not download_url:
        raise KeyError(f'{full_path}: {data}')
    return download_url


async def _upload_single_file(session, file_storage):
    """Обработка загрузки одного файла на Я.Диск."""
    filename = getattr(file_storage, 'filename', None)
    if not filename:
        return None
    try:
        upload_url = await _request_upload_link(session, filename)
        await _upload_to_disk(session, upload_url, file_storage)
        await _request_download_link(session, filename)
        return filename, filename
    except (KeyError, ClientError) as exception:
        return filename, exception


async def upload_file(file_storage_list: list) -> dict:
    """Загрузка набора файлов на Я.Диск."""
    results = {}
    async with aiohttp.ClientSession() as session:
        for fs in file_storage_list:
            if not fs or not getattr(fs, 'filename', None):
                continue
            upload_result = await _upload_single_file(session, fs)
            if upload_result is None:
                continue
            filename, value = upload_result
            results[filename] = value
    return results
