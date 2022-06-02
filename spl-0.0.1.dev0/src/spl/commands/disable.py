import os

from spl.bukkit import get_data_directory
from spl.errors import ExitCode, NonSingletonResultException
from spl.state import State, ResourceState


def add_parser_args(parser):
    parser.add_argument('package_name')


def run(spiget, args):
    with State.load(spiget) as state:
        try:
            resource = spiget.resource_details(args.package_name)
            resource_state = state.resource_state(resource)
            if resource_state == ResourceState.NOT_INSTALLED:
                print("{} is not installed.".format(resource.name))
                return ExitCode.NOT_INSTALLED
            elif resource_state == ResourceState.INSTALLED_DISABLED:
                print("{} is already disabled.".format(resource.name))
                return ExitCode.ALREADY_DISABLED
            elif resource_state == ResourceState.INSTALLED_ENABLED:

                source_jar_file = state.resource_jar_file(resource)
                data_dir_name = get_data_directory(source_jar_file)

                target_jarfile = 'plugins/{}.jar'.format(data_dir_name)
                target_data_dir = 'plugins/{}'.format(data_dir_name)

                if os.path.exists(target_jarfile):
                    print("Disabling plugin {} ({})...".format(resource.name, resource.current_version.name))
                    os.unlink(target_jarfile)
                if os.path.exists(target_data_dir):
                    os.unlink(target_data_dir)

                state.disable_resource(resource)

                return ExitCode.OK
        except NonSingletonResultException:
            print("'{}' matches more than one resource. Please use the resource ID to disable the plugin.".format(args.package_name))
            return ExitCode.NON_SINGLETON_RESULT
