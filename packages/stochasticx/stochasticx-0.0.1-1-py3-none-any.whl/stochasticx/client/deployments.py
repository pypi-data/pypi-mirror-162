from pathlib import Path

import click

from stochasticx.deployment.deployments import (
    Deployment,
    Deployments,
    Instances,
    SequenceClassificationInfTask,
    QuestionAnsweringInfTask,
    TranslationInfTask,
    SummarizationInfTask,
    TokenClassificationInfTask
)

from stochasticx.models.models import Models

@click.group(name="deployments")
def deployments():
    pass


@click.command(name="ls")
def ls_deployments():
    deployments = Deployments.get_deployments()
    for deployment in deployments:
        click.echo(deployment)
        
        
@click.command(name="inspect")
@click.option('--deployment_id', help='Deployment ID')
def inspect_deployment(deployment_id):
    deployment = Deployments.get_deployment(deployment_id)
    click.echo(deployment)
    
    if deployment is not None:
        click.echo("Instance used: {}".format(deployment.get_instance()))
        click.echo("Deployed model: {}".format(deployment.get_optimized_model()))
        
        
@click.command(name="status")
@click.option('--deployment_id', help='Deployment ID')
def deployment_status(deployment_id):
    deployment = Deployments.get_deployment(deployment_id)
    click.echo(deployment.get_status())
    
    
@click.group(name="deploy")
def deploy():
    pass

    
@click.command(name="sequence_classification")
@click.option('--model_id', help='Model ID')
@click.option('--instance_type', help='Instance type')
@click.option('--max_batch_size', default=8, show_default=True, help='Maximum batch size')
@click.option('--max_seq_length', default=128, show_default=True, help='Maximum source length')
def sequence_classification(
    model_id,
    instance_type,
    max_batch_size,
    max_seq_length
):
    task_type = SequenceClassificationInfTask(
        max_batch_size=max_batch_size,
        max_seq_length=max_seq_length
    )
    
    model = Models.get_optimized_model(model_id)
    
    deployment = Deployment()
    deployment.start_inference(
        model=model,
        task_type=task_type,
        instance_type=instance_type
    )


@click.command(name="question_answering")
@click.option('--model_id', help='Model ID')
@click.option('--instance_type', help='Instance type')
@click.option('--max_batch_size', default=8, show_default=True, help='Maximum batch size')
@click.option('--max_seq_length', default=128, show_default=True, help='Maximum sequence length')
def question_answering(
    model_id,
    instance_type,
    max_batch_size,
    max_seq_length
):
    task_type = QuestionAnsweringInfTask(
        max_batch_size=max_batch_size,
        max_seq_length=max_seq_length
    )
    
    model = Models.get_optimized_model(model_id)
    
    deployment = Deployment()
    deployment.start_inference(
        model=model,
        task_type=task_type,
        instance_type=instance_type
    )


@click.command(name="summarization")
@click.option('--model_id', help='Model ID')
@click.option('--instance_type', help='Instance type')
@click.option('--max_batch_size', default=8, show_default=True, help='Maximum batch size')
@click.option('--max_source_length', default=128, show_default=True, help='Maximum source length')
@click.option('--source_prefix', default='', show_default=True, help='Source prefix')
@click.option('--lang', default='en', show_default=True, help='Language')
def summarization(
    model_id,
    instance_type,
    max_batch_size,
    max_source_length,
    source_prefix,
    lang
):
    task_type = SummarizationInfTask(
        max_batch_size=max_batch_size,
        max_source_length=max_source_length,
        source_prefix=source_prefix,
        lang=lang
    )
    
    model = Models.get_optimized_model(model_id)
    
    deployment = Deployment()
    deployment.start_inference(
        model=model,
        task_type=task_type,
        instance_type=instance_type
    )


@click.command(name="translation")
@click.option('--model_id', help='Model ID')
@click.option('--instance_type', help='Instance type')
@click.option('--max_batch_size', default=8, show_default=True, help='Maximum batch size')
@click.option('--max_source_length', default=128, show_default=True, help='Maximum source length')
@click.option('--source_prefix', default='', show_default=True, help='Source prefix')
@click.option('--src_lang', default='en', show_default=True, help='Source language')
@click.option('--tgt_lang', default='de', show_default=True, help='Target language')
def translation(
    model_id,
    instance_type,
    max_batch_size,
    max_source_length,
    source_prefix,
    src_lang,
    tgt_lang
):
    task_type = TranslationInfTask(
        max_batch_size=max_batch_size,
        max_source_length=max_source_length,
        source_prefix=source_prefix,
        src_lang=src_lang,
        tgt_lang=tgt_lang
    )
    
    model = Models.get_optimized_model(model_id)
    
    deployment = Deployment()
    deployment.start_inference(
        model=model,
        task_type=task_type,
        instance_type=instance_type
    )


@click.command(name="token_classification")
@click.option('--model_id', help='Model ID')
@click.option('--instance_type', help='Model ID')
@click.option('--max_batch_size', default=8, show_default=True, help='Maximum batch size')
@click.option('--max_seq_length', default=128, show_default=True, help='Maximum source length')
def token_classification(
    model_id,
    instance_type,
    max_batch_size,
    max_seq_length
):
    task_type = TokenClassificationInfTask(
        max_batch_size=max_batch_size,
        max_seq_length=max_seq_length
    )
    
    model = Models.get_optimized_model(model_id)
    
    deployment = Deployment()
    deployment.start_inference(
        model=model,
        task_type=task_type,
        instance_type=instance_type
    )


        
@click.group(name="instances")
def instances():
    pass


@click.command(name="ls")
def ls_instances():
    instances = Instances.get_instance_types()
    for instance in instances:
        click.echo(instance)
        
        
deploy.add_command(sequence_classification)
deploy.add_command(question_answering)
deploy.add_command(token_classification)
deploy.add_command(summarization)
deploy.add_command(translation)

deployments.add_command(ls_deployments)
deployments.add_command(inspect_deployment)
deployments.add_command(deployment_status)
deployments.add_command(deploy)

instances.add_command(ls_instances)