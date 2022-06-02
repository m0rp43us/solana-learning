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
            elif resource_state == ResourceState.INSTALLED_ENABLED:
                print("{} is already enabled.".format(resource.name))
                return ExitCode.ALREADY_ENABLED
            elif resource_state == ResourceState.INSTALLED_DISABLED:

                plugins_dir = state.get_plugins_dir()
                source_jar_file = state.resource_jar_file(resource)
                data_dir_name = get_data_directory(source_jar_file)
                spl_data_dir = os.path.join(plugins_dir, "{}-data".format(resource.id))

                target_jarfile = 'plugins/{}.jar'.format(data_dir_name)
                target_data_dir = 'plugins/{}'.format(data_dir_name)

                if os.path.exists(target_jarfile) or os.path.exists(target_data_dir):
                    print("An existing enabled plugin conflicts with the data directory name {}. You must disable that plugin before {} can be enabled.".format(data_dir_name, resource.name))
                else:
                    print("Enabling plugin {} ({})...".format(resource.name, resource.current_version.name))
                    if not os.path.exists(spl_data_dir):
                        os.mkdir(spl_data_dir)
                    os.symlink(os.path.abspath(source_jar_file), target_jarfile)
                    os.symlink(os.path.abspath(spl_data_dir), target_data_dir)

                    state.enable_resource(resource)

                return ExitCode.OK
        except NonSingletonResultException:
            print("'{}' matches more than one resource. Please use the resource ID to enable the plugin.".format(args.package_name))
            return ExitCode.NON_SINGLETON_RESULT
