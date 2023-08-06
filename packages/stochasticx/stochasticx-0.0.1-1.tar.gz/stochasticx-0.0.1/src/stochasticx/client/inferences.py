import click
from stochasticx.inferences.inference import (
    SequenceClassificationModel, 
    QuestionAnsweringModel, 
    SummarizationModel, 
    TranslationModel, 
    TokenClassificationModel
)


@click.group(name="inference")
def inference():
    pass


@click.command(name="sequence_classification")
@click.option('--deployment_id', help='Deployment ID')
@click.option('--text', help='Text')
def sequence_classification(deployment_id, text):
    inference_model = SequenceClassificationModel(
        deployment_id
    )
    
    labels, scores = inference_model.inference([text])
    click.echo("Labels: {}".format(labels))
    click.echo("Scores: {}".format(scores))


@click.command(name="question_answering")
@click.option('--deployment_id', help='Deployment ID')
@click.option('--question', help='Question')
@click.option('--context', help='Context')
def question_answering(deployment_id, question, context):
    inference_model = QuestionAnsweringModel(
        deployment_id
    )
    
    answer = inference_model.inference([question], [context])
    click.echo("Answer: {}".format(answer))


@click.command(name="summarization")
@click.option('--deployment_id', help='Deployment ID')
@click.option('--text', help='Text')
@click.option('--min_length', help='Min length')
@click.option('--max_length', help='Max length')
def summarization(deployment_id, text, min_length, max_length):
    inference_model = SummarizationModel(
        deployment_id
    )
    
    summary = inference_model.inference([text], [min_length], [max_length])
    click.echo("Answer: {}".format(summary))
    

@click.command(name="translation")
@click.option('--deployment_id', help='Deployment ID')
@click.option('--text', help='Text')
@click.option('--max_length', help='Max length')
def translation(deployment_id, text, max_length):
    inference_model = TranslationModel(
        deployment_id
    )
    
    translation = inference_model.inference([text], [max_length])
    click.echo("Answer: {}".format(translation))
    
    
@click.command(name="token_classification")
@click.option('--deployment_id', help='Deployment ID')
@click.option('--text', help='Text')
def token_classification(deployment_id, text):
    inference_model = TokenClassificationModel(
        deployment_id
    )
    
    tokens, tags, scores = inference_model.inference([text])
    click.echo("Tokens: {}".format(tokens))
    click.echo("Tags: {}".format(tags))
    click.echo("Scores: {}".format(scores))
    
    
inference.add_command(sequence_classification)
inference.add_command(question_answering)
inference.add_command(summarization)
inference.add_command(translation)
inference.add_command(token_classification)
