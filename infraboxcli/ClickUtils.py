from click import Option, UsageError, option

import infraboxcli


# Source: https://gist.github.com/jacobtolar/fb80d5552a9a9dfc32b12a829fa21c0c
class MutuallyExclusiveOption(Option):
    """
    Mutually exclusive options for click.
    Usage example:
        @option('--jar-file', cls=MutuallyExclusiveOption,
            help="The jar file the topology lives in.",
            mutually_exclusive=["other_arg"])
        @option('--other-arg',
            cls=MutuallyExclusiveOption,
            help="Another argument.",
            mutually_exclusive=["jar_file"])
    """

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help + (
                    'NOTE: This argument is mutually exclusive with arguments: [' + ex_str + '].'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.name in opts and self.mutually_exclusive.intersection(opts):
            raise UsageError(
                "Illegal usage: `{}` is mutually exclusive with "
                "arguments `{}`.".format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


# Recurrent decorators
def add_project_id_option(f):
    def project_id_from_env_callback(ctx, param, value):
        # Nothing to do when there is some auto-completion
        if ctx.command_path.startswith("complete"):
            return None

        # Avoids having conflictual options
        if len(list(value)) > 1:
            infraboxcli.logger.error("Please do not use the \"--project-id\" multiple times "
                                     "or with a \"--project-name\" option.")

        # Both callbacks are called but the one for the option actually used, is called first
        if ctx.params.get("project_id"):
            return ctx.params.get("project_id")

        # The callback is still called even when the option is not used
        # So if value is None, we need to get the id from the env
        return infraboxcli.CLI_SETTINGS.get_from_env(value[0] if value else None, "project_id")

    def name_resolution_callback(ctx, param, value):
        # Nothing to do when there is some auto-completion
        # Also: The callback is still called even when the option is not used
        if ctx.command_path.startswith("complete") or not value:
            return None

        # Avoids having conflictual options
        if len(list(value)) > 1:
            infraboxcli.logger.error("Please do not use the \"--project-name\" multiple times "
                                     "or with a \"--project-id\" option.")

        # Both callbacks are called but the one for the option actually used, is called first
        if ctx.params.get("project_id"):
            return ctx.params.get("project_id")

        # Resolving the project's name
        name = value[0]
        project_id = infraboxcli.CLI_SETTINGS.known_project_names.get(name, None)
        if project_id is None:
            project_id = infraboxcli.CLI_SETTINGS.get_api().get_project_by_name(name).id
            infraboxcli.CLI_SETTINGS.known_project_names[name] = project_id

        # Updating the env/history
        infraboxcli.CLI_SETTINGS.get_from_env(project_id, "project_id")

        return project_id

    def name_autocompletion(ctx, args, incomplete):
        return list(filter(lambda string: string.startswith(incomplete) if string else False,
                           infraboxcli.CLI_SETTINGS.known_project_names))

    # Decorating
    f = option("-p", "--project-id", "project_id", default=None, callback=project_id_from_env_callback, multiple=True,
               autocompletion=lambda ctx, args, incomplete: infraboxcli.CLI_SETTINGS.completion_from_history(
                   incomplete, "project_id"), help="The project's id.")(f)

    return option("-n", "--project-name", "project_id", default=None, callback=name_resolution_callback, multiple=True,
                  autocompletion=name_autocompletion, help="The project's name.")(f)


def add_build_id_option(f):
    def build_id_from_env_callback(ctx, param, value):
        # Nothing to do when there is some auto-completion
        if ctx.command_path.startswith("complete"):
            return None

        return infraboxcli.CLI_SETTINGS.get_from_env(value, "build_id")

    return option("-b", "--build-id", "build_id", default=None, callback=build_id_from_env_callback,
                  autocompletion=lambda ctx, args, incomplete: infraboxcli.CLI_SETTINGS.completion_from_history(
                      incomplete, "build_id"), help="The build's id.")(f)


def add_job_id_option(f):
    def job_id_from_env_callback(ctx, param, value):
        # Nothing to do when there is some auto-completion
        if ctx.command_path.startswith("complete"):
            return None

        return infraboxcli.CLI_SETTINGS.get_from_env(value, "job_id")

    return option("-j", "--job-id", "job_id", default=None, callback=job_id_from_env_callback,
                  autocompletion=lambda ctx, args, incomplete: infraboxcli.CLI_SETTINGS.completion_from_history(
                      incomplete, "job_id"), help="The job's id.")(f)
