import click
from stochasticx.auth.auth import Stochastic

stochastic = Stochastic()

@click.command(name="login")
@click.option('--username', help='Username for login')
@click.option('--password', help='Password for login')
def login(username, password):
    if username is None or password is None:
        stochastic.login()
    else:
        stochastic.login(username, password)
        
    click.echo("Login successfully")


@click.group(name="me")
def me():
    pass


@click.command(name="profile")
def profile():
    profile_info = stochastic.get_profile()
    click.echo(profile_info)
    

@click.command(name="company")
def company():
    company_info = stochastic.get_company()
    click.echo(company_info)
    

@click.command(name="usage")
def usage():
    usage_info = stochastic.get_usage_quota()
    click.echo(usage_info)
    

me.add_command(profile)
me.add_command(company)
me.add_command(usage)