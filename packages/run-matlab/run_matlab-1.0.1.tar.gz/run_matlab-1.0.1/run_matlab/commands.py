import argparse
import textwrap
import sys
import os

def run_matlab_parser():
    usage = '''\
        run_matlab <command> [options]
        Commands:
            install            Installation of the MATLAB compiler runtime (MCR)
            run                Running the MATLAB function after installation
        Run run_matlab <command> -h for help on a specific command.
        '''
    parser = argparse.ArgumentParser(
        description='run_matlab: Command Line MATLAB Function Caller with Automatic MATLAB Compiler Runtime (MCR) Installation',
        usage=textwrap.dedent(usage)
    )

    from .version import __version__
    parser.add_argument('--version', action='version', version=f'run_matlab {__version__}')
    
    parser.add_argument('command', nargs='?', help='Subcommand to run')

    return parser

def install_parser():
    parser = MyParser(
        description='Installation of the MATLAB compiler runtime (MCR)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog='run_matlab install'
    )

    parser.add_argument(
        '-d',
        dest='installation_dir',
        type=str,
        default=os.path.expanduser('~')+'/run_matlab',
        help='Directory wherein the MATLAB compiler runtime (MCR) will be installed.')

    parser.add_argument(
        '-v',
        dest='matlab_version',
        type=str,
        default='R2013b',
        help='Number of threads to use.')
    
    parser.add_argument(
        '-r',
        dest='runtime_version',
        type=str,
        default='8.2',
        help='Number of repeats to perform.')

    return parser
      
def run_parser():
    parser = MyParser(
        description='Running the MATLAB function after installation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog='run_matlab run'
    )

    parser.add_argument(
        'function_dir',
        type=str,
        help='Directory wherein the standalone MATLAB function is located.')
        
    parser.add_argument(
        'function_name',
        type=str,
        help='Name of the standalone MATLAB function.')
        
    parser.add_argument(
        'function_args',
        nargs='*',
        type=str,
        help='Arguments for the standalone MATLAB function.')

    parser.add_argument(
        '-d',
        dest='installation_dir',
        type=str,
        default=os.path.expanduser('~')+'/run_matlab',
        help='Directory wherein the MATLAB compiler runtime (MCR) was installed.')
        
    parser.add_argument(
        '-v',
        dest='matlab_version',
        type=str,
        default='R2013b',
        help='Number of threads to use.')
    
    parser.add_argument(
        '-r',
        dest='runtime_version',
        type=str,
        default='8.2',
        help='Number of repeats to perform.')

    return parser

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)
