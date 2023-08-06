import logging

from django.apps import apps
from django.contrib.auth import get_user_model

from mayan.celery import app

from .classes import ModelFiler

logger = logging.getLogger(name=__name__)


@app.task(ignore_result=True)
def task_import_setup_process(import_setup_id):
    ImportSetup = apps.get_model(
        app_label='importer', model_name='ImportSetup'
    )

    import_setup = ImportSetup.objects.get(pk=import_setup_id)
    import_setup.process()


@app.task(ignore_result=True)
def task_import_setup_item_process(import_setup_item_id):
    ImportSetupItem = apps.get_model(
        app_label='importer', model_name='ImportSetupItem'
    )

    import_setup_item = ImportSetupItem.objects.get(pk=import_setup_item_id)
    import_setup_item.process()


@app.task(ignore_result=True)
def task_import_setup_populate(import_setup_id):
    ImportSetup = apps.get_model(
        app_label='importer', model_name='ImportSetup'
    )

    import_setup = ImportSetup.objects.get(pk=import_setup_id)
    import_setup.populate()


@app.task(ignore_result=True)
def task_model_filer_load(
    full_model_name, shared_upload_file_id, field_defaults=None,
    organization_installation_url=None, user_id=None
):
    SharedUploadedFile = apps.get_model(
        app_label='storage', model_name='SharedUploadedFile'
    )
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    shared_upload_file = SharedUploadedFile.objects.get(
        pk=shared_upload_file_id
    )

    model_filer = ModelFiler.get(full_model_name=full_model_name)

    model_filer.items_load(
        field_defaults=field_defaults, shared_upload_file=shared_upload_file,
        user=user
    )


@app.task(ignore_result=True)
def task_model_filer_save(
    full_model_name, save_file_title, filter_kwargs=None,
    organization_installation_url=None, user_id=None
):
    User = get_user_model()

    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    model_filer = ModelFiler.get(full_model_name=full_model_name)

    return model_filer.items_save(
        filter_kwargs=filter_kwargs,
        organization_installation_url=organization_installation_url,
        save_file_title=save_file_title, user=user
    )
