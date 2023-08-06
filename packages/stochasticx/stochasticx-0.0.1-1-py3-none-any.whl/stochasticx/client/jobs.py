import click
from stochasticx.models.models import Models
from stochasticx.datasets.datasets import Datasets
from stochasticx.jobs.jobs import (
    Job, 
    Jobs, 
    OptimizationCriteria, 
    SequenceClassificationTask, 
    QuestionAnsweringTask, 
    SummarizationTask, 
    TranslationTask, 
    TokenClassificationTask
)


@click.group(name="jobs")
def jobs():
    pass

@click.command(name="ls")
def ls_jobs():
    jobs = Jobs.get_jobs()
    for job in jobs:
        click.echo(job)


@click.command(name="inspect")
@click.option('--job_id', help='Job ID')
def job_inspect(job_id):
    job = Jobs.get_job(job_id)
    click.echo(job)


@click.command(name="status")
@click.option('--job_id', help='Job ID')
def job_status(job_id):
    job = Jobs.get_job(job_id)
    click.echo(job.get_status())
    


@click.group(name="launch")
def job_launch():
    pass


@click.command(name="sequence_classification")
@click.option('--job_name', help='Job name')
@click.option('--model_id', help='Model ID')
@click.option('--dataset_id', help='Dataset ID')
@click.option('--optimization_criteria', help='Optimization criteria. It should be latency or lossless')
@click.option('--sentence1_column', help='Sentence 1 column')
@click.option('--sentence2_column', help='Sentence 2 column')
@click.option('--labels_column', help='Labels column')
@click.option('--max_seq_length', default=128, help='Maximum sequence length')
def job_launch_sequence_classification(
    job_name,
    model_id, 
    dataset_id, 
    optimization_criteria,
    sentence1_column,
    sentence2_column,
    labels_column,
    max_seq_length
):
    model = Models.get_model(model_id)
    assert model is not None, "Model ID does not exist"
    dataset = Datasets.get_dataset(dataset_id)
    assert dataset is not None, "Dataset ID does not exist"
    assert optimization_criteria in ["latency", "lossless"], "optimization_criteria should take one of these values: latency or lossless"

    task_type = SequenceClassificationTask(
        sentence1_column=sentence1_column,
        sentence2_column=sentence2_column,
        labels_column=labels_column,
        max_seq_length=max_seq_length
    )

    job = Job(name=job_name)
    job.launch_auto(
        model=model,
        dataset=dataset,
        task_type=task_type,
        optimization_criteria=OptimizationCriteria.LATENCY
    )


@click.command(name="question_answering")
@click.option('--job_name', help='Job name')
@click.option('--model_id', help='Model ID')
@click.option('--dataset_id', help='Dataset ID')
@click.option('--optimization_criteria', help='Optimization criteria. It should be latency or lossless')
@click.option('--question_column', help='Question column')
@click.option('--answer_column', help='Answer column')
@click.option('--context_column', help='Context column')
@click.option('--max_seq_length', default=128, help='Maximum sequence length')
@click.option('--stride', default=30, help='Stride')
def job_launch_question_answering(
    job_name,
    model_id, 
    dataset_id, 
    optimization_criteria,
    question_column,
    answer_column,
    context_column,
    max_seq_length,
    stride
):
    model = Models.get_model(model_id)
    assert model is not None, "Model ID does not exist"
    dataset = Datasets.get_dataset(dataset_id)
    assert dataset is not None, "Dataset ID does not exist"
    assert optimization_criteria in ["latency", "lossless"], "optimization_criteria should take one of these values: latency or lossless"

    task_type = QuestionAnsweringTask(
        question_column=question_column,
        answer_column=answer_column,
        context_column=context_column,
        max_seq_length=max_seq_length,
        stride=stride
    )

    job = Job(name=job_name)
    job.launch_auto(
        model=model,
        dataset=dataset,
        task_type=task_type,
        optimization_criteria=OptimizationCriteria.LATENCY
    )


@click.command(name="summarization")
@click.option('--job_name', help='Job name')
@click.option('--model_id', help='Model ID')
@click.option('--dataset_id', help='Dataset ID')
@click.option('--optimization_criteria', help='Optimization criteria. It should be latency or lossless')
@click.option('--text_column', help='Text column')
@click.option('--summary_column', help='Summary column')
@click.option('--max_source_length', default=256, help='Maximum source length')
@click.option('--max_target_length', default=64, help='Maximum target length')
@click.option('--lang', default="en", help='Language')
@click.option('--pad_to_max_length', default=False, help='Pad to maximum length')
@click.option('--num_beams', default=4, help='Number of beams')
@click.option('--ignore_pad_token_for_loss', default=True, help='Ignore pad token for loss')
@click.option('--source_prefix', default="", help='Source prefix')
@click.option('--forced_bos_token', default=None, help='Forced BOS token')
def job_launch_summarization(
    job_name,
    model_id, 
    dataset_id, 
    optimization_criteria,
    text_column,
    summary_column,
    max_source_length,
    max_target_length,
    lang,
    pad_to_max_length,
    num_beams,
    ignore_pad_token_for_loss,
    source_prefix,
    forced_bos_token
):
    model = Models.get_model(model_id)
    assert model is not None, "Model ID does not exist"
    dataset = Datasets.get_dataset(dataset_id)
    assert dataset is not None, "Dataset ID does not exist"
    assert optimization_criteria in ["latency", "lossless"], "optimization_criteria should take one of these values: latency or lossless"

    task_type = SummarizationTask(
        text_column=text_column,
        summary_column=summary_column,
        max_source_length=max_source_length,
        max_target_length=max_target_length,
        lang=lang,
        pad_to_max_length=pad_to_max_length,
        num_beams=num_beams,
        ignore_pad_token_for_loss=ignore_pad_token_for_loss,
        source_prefix=source_prefix,
        forced_bos_token=forced_bos_token
    )

    job = Job(name=job_name)
    job.launch_auto(
        model=model,
        dataset=dataset,
        task_type=task_type,
        optimization_criteria=OptimizationCriteria.LATENCY
    )


@click.command(name="translation")
@click.option('--job_name', help='Job name')
@click.option('--model_id', help='Model ID')
@click.option('--dataset_id', help='Dataset ID')
@click.option('--optimization_criteria', help='Optimization criteria. It should be latency or lossless')
@click.option('--translation_column', help='Translation column')
@click.option('--src_lang', default="en", help='Source language')
@click.option('--tgt_lang', default="es", help='Target language')
@click.option('--max_source_length', default=256, help='Maximum source length')
@click.option('--max_target_length', default=256, help='Maximum target length length')
@click.option('--pad_to_max_length', default=False, help='Pad to maximum length')
@click.option('--num_beams', default=4, help='Number of beams')
@click.option('--ignore_pad_token_for_loss', default=True, help='Ignore pad token for loss')
@click.option('--source_prefix', default="", help='Source prefix')
@click.option('--forced_bos_token', default=None, help='Forced bos token')
def job_launch_translation(
    job_name,
    model_id, 
    dataset_id, 
    optimization_criteria,
    translation_column,
    src_lang,
    tgt_lang,
    max_source_length,
    max_target_length,
    pad_to_max_length,
    num_beams,
    ignore_pad_token_for_loss,
    source_prefix,
    forced_bos_token
):
    model = Models.get_model(model_id)
    assert model is not None, "Model ID does not exist"
    dataset = Datasets.get_dataset(dataset_id)
    assert dataset is not None, "Dataset ID does not exist"
    assert optimization_criteria in ["latency", "lossless"], "optimization_criteria should take one of these values: latency or lossless"

    task_type = TranslationTask(
        translation_column=translation_column,
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        max_source_length=max_source_length,
        max_target_length=max_target_length,
        pad_to_max_length=pad_to_max_length,
        num_beams=num_beams,
        ignore_pad_token_for_loss=ignore_pad_token_for_loss,
        source_prefix=source_prefix,
        forced_bos_token=forced_bos_token
    )

    job = Job(name=job_name)
    job.launch_auto(
        model=model,
        dataset=dataset,
        task_type=task_type,
        optimization_criteria=OptimizationCriteria.LATENCY
    )


@click.command(name="token_classification")
@click.option('--job_name', help='Job name')
@click.option('--model_id', help='Model ID')
@click.option('--dataset_id', help='Dataset ID')
@click.option('--optimization_criteria', help='Optimization criteria. It should be latency or lossless')
@click.option('--tokens_column', help='Tokens column')
@click.option('--domains_column', help='Domains 2 column')
@click.option('--ner_tags_column', help='Ner column')
@click.option('--max_seq_length', default=128, help='Maximum sequence length')
@click.option('--label_all_tokens', default=False, help='Label all columns')
def job_launch_token_classification(
    job_name,
    model_id, 
    dataset_id, 
    optimization_criteria,
    tokens_column,
    domains_column,
    ner_tags_column,
    max_seq_length,
    label_all_tokens
):
    model = Models.get_model(model_id)
    assert model is not None, "Model ID does not exist"
    dataset = Datasets.get_dataset(dataset_id)
    assert dataset is not None, "Dataset ID does not exist"
    assert optimization_criteria in ["latency", "lossless"], "optimization_criteria should take one of these values: latency or lossless"

    task_type = TokenClassificationTask(
        tokens_column=tokens_column,
        domains_column=domains_column,
        ner_tags_column=ner_tags_column,
        max_seq_length=max_seq_length,
        label_all_tokens=label_all_tokens
    )

    job = Job(name=job_name)
    job.launch_auto(
        model=model,
        dataset=dataset,
        task_type=task_type,
        optimization_criteria=OptimizationCriteria.LATENCY
    )
    
    
job_launch.add_command(job_launch_sequence_classification)
job_launch.add_command(job_launch_question_answering)
job_launch.add_command(job_launch_summarization)
job_launch.add_command(job_launch_translation) 
job_launch.add_command(job_launch_token_classification)

jobs.add_command(ls_jobs)
jobs.add_command(job_inspect)
jobs.add_command(job_status)
jobs.add_command(job_launch)
