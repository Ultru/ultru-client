import argparse
import json
from cmd2 import Cmd, with_argparser

from .utils.globals import CLI_GLOBALS, _ULTR_JOB_STATUS
from .utils.config import list_config, put_config_value
from .utils.utils import (
    init_ultru_client,
    load_queries,
    save_query,
    list_queries,
    submit_query,
    update_jobs,
    get_jobs,
    record_type_choices,
    score_choices,
    get_query_names,
    remove_queries,
    list_jobs,
    list_results,
    pull_api_key,
    list_key,
    set_engagement,
    list_engagement,
    get_results,
    print_summary,
    remove_jobs
)


class ultrushell(Cmd):
    prompt = 'ultru>'
    intro = """
 _   _ _    ___________ _   _
| | | | |  |_   _| ___ \ | | |
| | | | |    | | | |_/ / | | |
| | | | |    | | |    /| | | |
| |_| | |____| | | |\ \| |_| |
 \___/\_____/\_/ \_| \_|\___/ .io
    """

    def possible_results(self):
        return get_results()

    def possible_queries(self):
        return get_query_names()

    def possible_jobs_status(self):
        return list(_ULTR_JOB_STATUS.__members__.keys())

    def remove_job_options(self):
        return list(_ULTR_JOB_STATUS.__members__.keys()) + ['all']

    def remove_query_options(self):
        return list(get_query_names()) + ['all']


    list_parser = argparse.ArgumentParser()
    shell_choices = ['config', 'queries', 'results', 'jobs', 'key', 'engagement']
    list_parser.add_argument('option', choices=shell_choices, help='list things')

    @with_argparser(list_parser)
    def do_list(self, args):
        """
        This will list current saved queries.
        """
        if args.option == 'config':
            print(list_config())
        if args.option == 'queries':
            for k,v in list_queries().items():
                print(k, ":", json.dumps(v, indent=4))
        if args.option == 'jobs':
            update_jobs(CLI_GLOBALS.ENGAGEMENT)
            for k,v in list_jobs().items():
                print(k, ":", json.dumps(v, indent=4))
        if args.option == 'results':
            for i in list_results():
                print(i)
        if args.option == 'key':
            for k,v in list_key().items():
                print(k, ":", json.dumps(v, indent=4))
        if args.option == 'engagement':
            print(list_engagement())

    config_parser = argparse.ArgumentParser()
    possible_config = ["password", "store_password", "username"]
    config_help = "Set configuration items"
    config_parser.add_argument('set', choices=possible_config, help="Set Configuration")
    config_parser.add_argument('value', help="The value to set; use 'yes' or 'no' for set booleans")

    @with_argparser(config_parser)
    def do_config(self, args):
        """
        This will allow changing config items.
        """
        if args.set == "store_password":
            put_config_value("store_password", True if args.value.lower() == "yes" else False)
        elif args.set == "password":
            put_config_value("password", args.value)
        elif args.set == "username":
            put_config_value("username", args.value)
        else:
            print("Invalid option")

    submit_parser = argparse.ArgumentParser()
    submit_parser.add_argument('queries', nargs='+', choices_method=possible_queries, help='Name the queries you would like to submit to the job api')

    @with_argparser(submit_parser)
    def do_submit(self, args):
        for query in args.queries:
            submit_query(query)

    create_parser = argparse.ArgumentParser()
    create_parser.add_argument('name', help="name of the query")
    create_parser.add_argument('record_type', choices=record_type_choices, help='Types to choose from')
    create_parser.add_argument('score', choices=score_choices, default=None, help="Score to choose from")

    @with_argparser(create_parser)
    def do_create(self, args):
        save_query(args.name, args.record_type, args.score)


    summarizer_parser = argparse.ArgumentParser()
    summarizer_parser.add_argument('name', choices_method=possible_results)

    @with_argparser(summarizer_parser)
    def do_summarize(self, args):
        print_summary(args.name)


    remove_parser = argparse.ArgumentParser()
    remove_parser.add_argument('--queries', nargs='+', choices_method=remove_query_options, help="Remove query or queries from your saved cache")
    remove_parser.add_argument('--jobs', nargs='+', choices_method=remove_job_options, help="Remove jobs from your saved cache")

    @with_argparser(remove_parser)
    def do_remove(self, args):
        print(args.queries)
        print(args.jobs)
        if args.queries:
            if 'all' in args.queries:
                remove_queries(list(self.possible_queries()))
            else:
                remove_queries(args.queries)
            print("Removed: {}".format(args.queries))
        if args.jobs:
            if 'all' in args.jobs:
                remove_jobs(list(self.possible_jobs_status()))
            else:
                remove_jobs(args.jobs)
            print("Removed: {}".format(args.jobs))
        if args.jobs is None and args.queries is None:
            print("Nothing done, please use --queries, or --jobs")


    update_parser = argparse.ArgumentParser()
    update_parser.add_argument('option', help="Sync jobs with API", choices=['jobs'])

    @with_argparser(update_parser)
    def do_update(self, args):
        update_jobs(CLI_GLOBALS.ENGAGEMENT)
        print("Synchronizing jobs with system")




def main():
    init_ultru_client()
    ultrushell().cmdloop()


if __name__ == "__main__":
    main()
