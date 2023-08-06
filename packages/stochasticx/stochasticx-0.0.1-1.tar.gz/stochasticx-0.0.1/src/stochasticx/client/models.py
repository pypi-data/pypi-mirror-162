from pathlib import Path

import click
from stochasticx.models.models import Models, Model

@click.group(name="models")
def models():
    pass


@click.command(name="ls")
@click.option('--optimized', is_flag=True, help='Show only optimized models')
@click.option('--all', is_flag=True, help='Show all models')
def ls_models(optimized, all):
    if not optimized or all:
        models = Models.get_models()
        for model in models:
            click.echo(model)
    
    if optimized or all:
        models = Models.get_optimized_models()
        for model in models:
            click.echo(model)


@click.command(name="inspect")
@click.option('--model_id', help='Model ID')
def model_inspect(model_id):
    model = Models.get_model(model_id)
    click.echo(model)
    click.echo(model.get_model_info())
    
    
@click.command(name="download")
@click.option('--model_id', help='Model ID that you want to download')
@click.option('--local_path', help='Path where the downloaded model will be saved')
def model_download(model_id, local_path):
    model = Models.get_model(model_id)
    model.download(local_path)


@click.command(name="upload")
@click.option('--name', help='Path where the model to upload is located')
@click.option('--directory_path', help='Directory where the model to upload is located')
@click.option('--model_type', help='Model type. It should be hf, pt or custom')
def model_upload(name, directory_path, model_type):
    model_type = model_type.strip()
    assert model_type in ["hf", "pt", "custom"], "Model type should be hf, pt or custom"
    directory_path = Path(directory_path)
    assert directory_path.exists(), "The directory path does not exist"
    
    model = Model(
        name=name,
        directory_path=directory_path,
        model_type=model_type
    )
    
    click.echo("Uploading the model. This can take several minutes...")
    model.upload()


models.add_command(ls_models)
models.add_command(model_inspect)
models.add_command(model_download)
models.add_command(model_upload)