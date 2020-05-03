import logging
import os
import click


from ultru_query.query import Query

from .utils import (
    init_ultru_client,
    load_queries,
    save_query,
    list_queries,
    submit_query,
    get_jobs,
    record_type_choices,
    score_choices
)

loglevel = os.environ.get('LOGLVL', logging.INFO)
logging.basicConfig(level=int(loglevel) * 10)
logger = logging.getLogger("ultru::ultru-cli:main")


api_key_helper = "The ULTRU (TM) API key, use the user interface to access this, this will accept the file <ultru.key>; if not specified, the cli will look for the file in the current directory"
record_type_helper = f"""Type of record, can be one of: {", ".join([x for x in record_type_choices])}"""
score_helper = f"""Score, can be one of {", ".join([x for x in score_choices])}"""

@click.group()
@click.pass_context
@click.Choice()
# @click.option("-k", "--api-key", default=None, required=False, help=api_key_helper)
# @click.option("-e", "--engagement", required=None, help="The engagement to query")
def query_cli(ctx):
    init_ultru_client()

@query_cli.command()
@click.option("-n", "--name", default=None, required=False, help="Name of the query")
@click.option("-t", "--record-type", default=None, required=True, help=record_type_helper)
@click.option("-s", "--score", default=None, required=False, help=score_helper)
@click.pass_context
def create(ctx, name, record_type, score):
    save_query(name, record_type, score)

@query_cli.command()
@click.pass_context
def list(ctx):
    list_queries()

@query_cli.command()
@click.argument('query', nargs=-1)
@click.pass_context
def submit(ctx, query):
    for q in query:
        submit_query(q)
    

def main():
    query_cli(obj={})

if __name__ == "__main__":
    main()