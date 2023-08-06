#!/usr/bin/env python
import argparse
from io import StringIO
import json
import os
import os.path
import sys

from dotenv import load_dotenv
import requests
from yaml import safe_load

load_dotenv(".env")


class CLI(object):

    """Docstring for CLI. """

    def __init__(self):
        """TODO: to be defined. """
        parser = argparse.ArgumentParser(
            description="Motivus cluster CLI utility")
        parser.add_argument('command', choices=[
                            "build", "push", "clean", "worker", "loopback", "new"])
        args = parser.parse_args(sys.argv[1:2])
        self.args = args
        getattr(self, args.command)()

    def parse_config(self):
        args = self.args
        with open(args.config_file, 'r') as f:
            config = safe_load(f)
            self.config = config

    def push(self):
        parser = argparse.ArgumentParser(
            prog="motivus push", description="Push package bundle to package registry")
        parser.add_argument('-c, --config-file', help="yaml configuration file location",
                            default="./motivus.yml", dest='config_file')
        parser.add_argument('-D, --dev', help="development mode",
                            action='store_true', default=False, dest="D")
        parser.add_argument('--build-dir, -b',
                            help="package bundle location", default="./build", dest='build_dir')
        args = parser.parse_args(sys.argv[2:])

        self.args = args
        self.parse_config()
        config = self.config

        base_url = "http://localhost:4000/api/package_registry/algorithms/" if args.D else "https://marketplace.api.motivus.cl/api/package_registry/algorithms/"
        token = os.environ["MOTIVUS_PERSONAL_ACCESS_TOKEN"] if "MOTIVUS_PERSONAL_ACCESS_TOKEN" in os.environ else ""
        if (token == ""):
            print("MOTIVUS_PERSONAL_ACCESS_TOKEN is not present in env")
        headers = {'authorization': f'Bearer {token}'}

        algorithm_res = requests.get(
            base_url, params={'name': config["package"]["name"]}, headers=headers)
        if (algorithm_res.status_code == 401):
            raise Exception('not authorized, check your token')
        if (len(algorithm_res.json()["data"]) == 1):
            algorithm_id = algorithm_res.json()["data"][0]["id"]

            package_filename = f'{config["package"]["name"]}-{config["package"]["version"]}.zip'
            package_location = os.path.join(args.build_dir, package_filename)
            version = {
                'name': config["package"]["version"],
                'metadata': config["package"]["metadata"]
            }
            version = parse_metadata(version)
            with open(package_location, 'rb') as f:
                json_string = StringIO(json.dumps(version))
                files = {"version": (None, json_string, "application/json"),
                         "package": (package_filename, f, "application/octet-stream")}
                resp = requests.post(
                    f'{base_url}{algorithm_id}/versions', files=files, headers=headers)
                if (resp.status_code == 403):
                    raise Exception(f'not authorized to push version')
                try:
                    res_json = resp.json()
                    data = res_json.get("data", None)
                    errors = res_json.get("errors", None)
                    if data:
                        if data.get("id", None):
                            print(
                                f'ok: {config["package"]["name"]}-{config["package"]["version"]}')
                        else:
                            raise Exception("could not push version")
                    elif errors:
                        if errors.get("name", None):
                            raise Exception(
                                f'this version name {errors.get("name", None)[0]}')
                        else:
                            raise Exception(
                                f'could not push version: {errors}')
                    else:
                        raise Exception(f'could not push version: {errors}')

                except Exception as e:
                    raise e
        else:
            raise Exception(
                f'could not get algorithm: {config["package"]["name"]}')
        sys.exit(0)

    def build(self):
        parser = argparse.ArgumentParser(
            prog="motivus build", description="Generates bundle package from source-code using motivus packager")
        parser.add_argument('-c, --config-file', help="yaml configuration file location",
                            default="./motivus.yml", dest='config_file')
        parser.add_argument('-D, --dev', help="development mode",
                            action='store_true', default=False, dest='D')
        parser.add_argument('--build-dir, -b',
                            help="package bundle location", default="./build", dest='build_dir')
        args = parser.parse_args(sys.argv[2:])

        self.args = args
        self.parse_config()
        config = self.config
        run_docker_packager(args, config)
        sys.exit(0)

    def clean(self):
        parser = argparse.ArgumentParser(
            prog="motivus clean", description="Cleans package build directory")
        parser.add_argument('-c, --config-file', help="yaml configuration file location",
                            default="./motivus.yml", dest='config_file')
        parser.add_argument('--build-dir, -b',
                            help="package bundle location", default="./build", dest='build_dir')
        args = parser.parse_args(sys.argv[2:])

        self.args = args
        self.parse_config()
        config = self.config
        args = self.args

        run_docker_packager(
            args, config, "make --makefile=/common/Makefile clean")
        sys.exit(0)

    def worker(self):
        parser = argparse.ArgumentParser(
            prog="motivus worker", description="Executes tasks")
        parser.add_argument('-t', help="limit parallel task execution to N threads",
                            default="1", dest='thread_count', metavar='N')
        parser.add_argument('--backend-host', help="connect to HOST to ask for tasks",
                            default="waterbear.api.motivus.cl", dest='backend_host', metavar='HOST')
        parser.add_argument('--no-tls', help="disable Transport Layer Security",
                            action='store_true', default=False, dest='no_tls')
        parser.add_argument('--token', help="use provided worker token",
                            default="", dest='worker_token', metavar='TOKEN')

        args = parser.parse_args(sys.argv[2:])

        env = {
            'CLUSTER_MODE': "network",
            'PROCESSING_THREADS': args.thread_count,
            'REACT_APP_TLS': not args.no_tls,
            'REACT_APP_API_HOST': args.backend_host,
            'WB_WORKER_TOKEN': args.worker_token
        }

        run_docker_worker(env)

    def loopback(self):
        parser = argparse.ArgumentParser(
            prog="motivus loopback", description="Executes tasks")
        parser.add_argument('-p, --port', help="loopback server post",
                            default="7070", dest='port', metavar='PORT')
        args = parser.parse_args(sys.argv[2:])

        env = {
            'CLUSTER_MODE': "loopback",
            'LOOPBACK_PORT': args.port,
        }

        run_docker_worker(env, args.port)

    def new(self):
        parser = argparse.ArgumentParser(
            prog="motivus new", description="Creates a new project")
        parser.add_argument(
            'name', help="project name", metavar="name")
        args = parser.parse_args(sys.argv[2:])
        config = {"build": {"compiler": "mvrc"},
                  "package": {"name": None, "version": None}}
        run_docker_packager(
            args, config, "cargo generate --git https://github.com/m0tivus/wasm-pack-template.git --name " + args.name)


def parse_metadata(version):
    readme = version.get("metadata", {}).get("long_description", "")
    if readme.endswith(".md") or readme.endswith(".MD"):
        with open(readme, 'r') as f:
            contents = f.read()
            return {**version, **{'metadata': {**version["metadata"], **{'long_description': contents}}}}
    return version


def run_docker_packager(args, config, command=""):
    compiler = config['build']['compiler']
    image = 'motivus/packager-emscripten:1.1.0' if compiler == 'mvcc' else 'motivus/packager-wasm-pack:0.3.0' if compiler == 'mvrc' else exit(
        f'compiler not supported "{compiler}". Use one of "mvcc", "mvrc"')

    docker_args = 'docker run -ti --rm  -v $(pwd):/src -w /src -u $(id -u):$(id -g)'

    env = {
        'SOURCE_DIR': config["build"].get("source", "./"),
        'BUILD_DIR': args.build_dir if hasattr(args, "build_dir") else "./build",
        'FILESYSTEM_DIR': config["build"].get("filesystem", "./"),
        'PACKAGE_NAME': config["package"]["name"],
        'PACKAGE_VERSION': config["package"]["version"],
        'LOG_STDOUT_STDERR': "true" if hasattr(args, "D") and args.D else "false",
        'USER': "$(id -u)"
    }
    os.system(" ".join([docker_args, format_env(env), image, command]))


def run_docker_worker(env, port=""):
    image = 'motivus/worker:1.1.0'
    docker_args = 'docker run -ti --rm --network=host'

    if port:
        docker_args += f' -p {port}:{port}'

    os.system(" ".join([docker_args, format_env(env), image]))


def format_env(env):
    env_vars = []
    for k, v in env.items():
        env_vars.append(f'-e {k}={v}')

    return " ".join(env_vars)


if __name__ == "__main__":
    CLI()
