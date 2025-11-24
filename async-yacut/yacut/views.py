import requests
from http import HTTPStatus
from flask import (
    render_template,
    redirect,
    request,
    Response,
    current_app,
)

from . import app
from .constants import FILES_ROUTE
from .disk_operations import upload_file, get_download_link_to_file
from .error_handler import InvalidShortIDError, ShortIDConflictError
from .forms import ShortLinkToLinkForm, ShortLinkToFileForm
from .models import URLMap


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Обрабатывает форму на главной странице."""
    form = ShortLinkToLinkForm()
    result_messages = []
    info_messages = []
    error_messages = []

    if not form.validate_on_submit():
        return render_template(
            'main_page.html',
            form=form,
            result_messages=result_messages,
            info_messages=info_messages,
            error_messages=error_messages,
        )

    custom_id = (form.custom_id.data or '').strip() or None
    original_link = form.original_link.data
    link_existing = URLMap.query.filter_by(
        original=original_link
    ).first()

    if link_existing:
        if custom_id:
            error_messages.append(ShortIDConflictError.message)
        else:
            existing_url = f"{request.host_url}{link_existing.short}"
            info_messages.append(
                (
                    'Эта ссылка уже есть: '
                    f'<a href="{existing_url}">{existing_url}</a>'
                ),
            )

    else:
        try:
            shortlink = URLMap.create_short_link(
                original=original_link,
                custom_id=custom_id,
            )
        except (InvalidShortIDError, ShortIDConflictError) as error:
            error_messages.append(error.message)
        else:
            shortlink_dict = shortlink.to_dict()
            short_href = shortlink_dict.get('short_link')
            result_messages.append(
                (
                    'Ваша новая ссылка готова: '
                    f'<a href="{short_href}">{short_href}</a>'
                )
            )

    return render_template(
        'main_page.html',
        form=form,
        result_messages=result_messages,
        info_messages=info_messages,
        error_messages=error_messages,
    )


@app.route(f'/{FILES_ROUTE}', methods=['GET', 'POST'])
def files_view():
    """Обрабатывает загрузку файлов на страницу /files."""
    form = ShortLinkToFileForm()
    result_links = []
    error_messages = []

    if not form.validate_on_submit():
        return render_template(
            'files_page.html',
            form=form,
            result_links=result_links,
            error_messages=error_messages,
        )

    files = [fs for fs in form.files.data if fs and fs.filename]
    file_link = current_app.ensure_sync(upload_file)(files) or {}
    if not file_link:
        file_link = {fs.filename: fs.filename for fs in files if fs}
    created_filenames = []

    for filename, link in file_link.items():
        if isinstance(link, Exception):
            error_messages.append(
                f'{filename} -> Не был загружен. Ошибка: {link}'
            )
            continue

        if URLMap.query.filter_by(original=filename).first():
            error_messages.append(
                (
                    f'{filename} -> Не был загружен. Ошибка: '
                    'Файл с таким именем уже существует.'
                )
            )
            continue

        shortlink = URLMap.create_short_link(
            original=link,
            is_file=True,
        )
        new_url = f'{request.host_url}{shortlink.short}'
        result_links.append({'filename': filename, 'url': new_url})
        created_filenames.append(filename)

    if not result_links and created_filenames:
        saved_links = URLMap.query.filter(
            URLMap.is_file.is_(True),
            URLMap.original.in_(created_filenames),
        ).all()
        for link_obj in saved_links:
            result_links.append({
                'filename': link_obj.original,
                'url': f'{request.host_url}{link_obj.short}',
            })
    return render_template(
        'files_page.html',
        form=form,
        result_links=result_links,
        error_messages=error_messages,
    )


@app.route('/<string:short>')
def redirect_view(short):
    """Выполняет переадресацию по короткой ссылке.

    (Редирект именно со страницы /files отказывался работать
    по неизвестным для меня причинам. Работал везде, но не с
    этой страницы. ERR_INVALID_RESPONSE.
    Пришлось придумывать что-то необычное :/)
    """
    link_obj = URLMap.query.filter_by(short=short).first_or_404()
    if link_obj.is_file:
        href = get_download_link_to_file(link_obj.original)
        remote_resp = requests.get(href, stream=True)
        remote_resp.raise_for_status()
        headers = {
            'Content-Type': remote_resp.headers.get(
                'Content-Type',
                'application/octet-stream',
            ),
            'Content-Length': remote_resp.headers.get('Content-Length'),
            'Content-Disposition': remote_resp.headers.get(
                'Content-Disposition',
            ),
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        return Response(
            remote_resp.iter_content(chunk_size=8192),
            headers=headers,
            status=HTTPStatus.OK,
        )
    return redirect(link_obj.original, code=HTTPStatus.FOUND)
