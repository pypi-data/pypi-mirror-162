import click
from stochasticx.client.models import models
from stochasticx.client.datasets import datasets
from stochasticx.client.jobs import jobs
from stochasticx.client.auth import login, me
from stochasticx.client.deployments import instances, deployments
from stochasticx.client.inferences import inference


@click.group()
def cli():
    pass
    
 
cli.add_command(models)
cli.add_command(datasets)
cli.add_command(jobs)
cli.add_command(login)
cli.add_command(me)
cli.add_command(instances)
cli.add_command(deployments)
cli.add_command(inference)