from pathlib import Path

import click
from stochasticx.datasets.datasets import Datasets, Dataset

@click.group(name="datasets")
def datasets():
    pass


@click.command(name="ls")
def ls_datasets():
    datasets = Datasets.get_datasets()
    for dataset in datasets:
        click.echo(dataset)


@click.command(name="inspect")
@click.option('--dataset_id', help='Dataset ID')
def dataset_inspect(dataset_id):
    dataset = Datasets.get_dataset(dataset_id)
    click.echo(dataset)
    click.echo(dataset.get_dataset_info())
    
    
@click.command(name="columns")
@click.option('--dataset_id', help='Dataset ID')
def dataset_columns(dataset_id):
    dataset = Datasets.get_dataset(dataset_id)
    click.echo(dataset.get_column_names())
    
    
@click.command(name="download")
@click.option('--dataset_id', help='Dataset ID')
@click.option('--local_path', help='Path where the downloaded dataset will be saved')
def dataset_download(dataset_id, local_path):
    dataset = Datasets.get_dataset(dataset_id)
    dataset.download(local_path)


@click.command(name="upload")
@click.option('--name', help='Path where the dataset to upload is located')
@click.option('--directory_path', help='Directory where the dataset to upload is located')
@click.option('--dataset_type', help='Dataset type. It should be hf, csv or json')
def dataset_upload(name, directory_path, dataset_type):
    dataset_type = dataset_type.strip()
    assert dataset_type in ["hf", "csv", "json"], "Dataset type should be hf, csv or json"
    directory_path = Path(directory_path)
    assert directory_path.exists(), "The directory path does not exist"
    
    dataset = Dataset(
        name=name,
        directory_path=directory_path,
        dataset_type=dataset_type
    )
    
    click.echo("Uploading dataset...")
    dataset.upload()
    click.echo("Dataset uploaded")


datasets.add_command(ls_datasets)
datasets.add_command(dataset_inspect)
datasets.add_command(dataset_download)
datasets.add_command(dataset_upload)
datasets.add_command(dataset_columns)