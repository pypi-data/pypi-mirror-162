import subprocess
import os
import json
import sys
from time import sleep
import httpx
import typer
from .data.accomate_config import AccomateConfig

from .utils.config import validate_project_config

from .aws.route53 import add_dns_record, verify_dns_record
from .utils.command import is_installed
from .utils.compose import assign_service_type_tag, compose_down, compose_up, exec_run, get_containers_on_same_network, restart_containers
from .utils.echo import echo
from .utils.git import clone_repo
from .utils.keys import write_all_the_keys
from .utils.network import find_open_port
from .utils.nginx import add_lets_encrypt_certificate, restart_nginx
from .utils.validators import validate_email, validate_enviorment
from .utils.yaml_file import read_yaml_file, write_yaml_file
from .utils.passwords import generate_django_secret_key, generate_random_password
import dotenv
from .utils.store import generate_store_app_id, generate_store_app_key
from .aws import s3
from .clis.database import database

app = typer.Typer()

app.add_typer(database, name="db")

USER = os.environ.get("USER")

# [DEFAULT]
accomate_config: AccomateConfig = AccomateConfig.get_instance()

# exit()
accomate_base_path = accomate_config.get_base_path()
accomate_domain = accomate_config.get_domain()

absolute_package_path = os.path.dirname(os.path.abspath(__file__))

image_host_username = "042826358439.dkr.ecr.us-east-1.amazonaws.com"


@app.command()
def version():
    echo(accomate_config.get_version())
    exit()


if not os.path.exists(accomate_base_path):
    action = sys.argv[1] if len(sys.argv) > 1 else False
    if action != "install":
        echo("🚫 Accomate is not installed.")
        echo("Run `accomate install` to install .")
        sys.exit(1)


@app.command()
def install(domain: str):
    try:
        # Setting up Accoladez to start building stores

        echo("Starting domain setup...")

        set_domain_response = accomate_config.set_domain(domain)

        if not os.path.exists(accomate_base_path):
            os.mkdir(accomate_base_path)
        else:
            reinstall = input(
                "🚫 Accomate is already installed. Do you want to reinstall? (y/n) ")
            if reinstall == "y":
                echo("🚀 Reinstalling .")
                subprocess.run(["rm", "-rf", accomate_base_path])
                os.mkdir(accomate_base_path)
            else:
                echo("🚫 Exiting.")
                exit(code=901)

        # Install Nginx if not available
        if is_installed("nginx"):
            echo("Nginx is already installed.")
        else:
            echo("Installing Nginx")
            subprocess.call(["sudo", "apt-get", "install", "nginx"])

        # Configure Nginx
        echo("Configuring Nginx")

        nginx_conf = os.path.join(absolute_package_path, "conf", "nginx.conf")

        # print(nginx_conf)

        with open(nginx_conf, "r+") as f:
            # Update user variable in nginx_conf
            file = f.read()
            file = file.replace("#user#", USER)
            f.truncate(0)
            f.seek(0)
            f.write(file)

        subprocess.call(
            ["sudo", "cp", nginx_conf, "/etc/nginx/nginx.conf"])
        restart_nginx()

        # Install Docker if not available

        docker_install_script_path = os.path.join(
            absolute_package_path, "scripts", "docker-install.sh")
        docker_compose_install_script_path = os.path.join(
            absolute_package_path, "scripts", "docker-compose-install.sh")

        if is_installed("docker"):
            echo("Docker is already installed.")
        else:
            echo("Installing Docker")
            subprocess.call(["sudo", "sh", docker_install_script_path])

        # Install Docker Compose if not available
        if is_installed("docker compose", "version"):
            echo("Docker Compose is already installed.")
        else:
            echo("Installing Docker Compose")
            subprocess.call(["sudo", "sh", docker_compose_install_script_path])

        if is_installed("certbot", "--version"):
            echo("Certbot is already installed.")
        else:
            subprocess.call(["sudo", "apt-get", "install", "certbot"])
            subprocess.call(
                ['sudo', 'apt', 'install', 'python3-certbot-nginx'])

        # Install AWS CLI if not available
        if is_installed("aws", "--version"):
            echo("AWS CLI is already installed.")
        else:
            echo("Installing AWS CLI")
            subprocess.call(["sudo", "apt-get", "install", "awscli"])

        echo("Github Personal Token least required privileges are: 'private_repo', 'repo', 'org:read'")
        GITHUB_PERSONAL_TOKEN = str(
            input("Enter your Github personal token: "))
        AWS_REGION = str(
            input("Enter your AWS Region: "))
        AWS_ACCESS_KEY = str(
            input("Enter your AWS Access Key: "))
        AWS_ACCESS_SECRET = str(
            input("Enter your AWS Access Secret: "))

        config = {
            "github_personal_token": GITHUB_PERSONAL_TOKEN,
            "base_domain": domain,
            "base_path": accomate_base_path,
            "image_host_username": image_host_username,
            "public_ip": accomate_config.get_public_ip(),
            "hosted_zone_id": accomate_config.get_hosted_zone_id(),
            "aws": {
                "region": AWS_REGION,
                "access_key": AWS_ACCESS_KEY,
                "access_secret": AWS_ACCESS_SECRET,
            }
        }

        write_yaml_file(accomate_config.get_config_path(), config)

        echo("🚀 Accomate setup is done, you can now start building stores")

        echo("Happy Accoladezing! 😎")
    except typer.Abort as _:
        print(e)
        echo("Removing Accomate folder")
        subprocess.call(["sudo", "rm", "-rf", accomate_base_path])
        echo("🚫 Accomate setup failed, please try again.")
        exit(code=1)
    except Exception as e:
        print(e)
        echo("Removing Accomate folder")
        subprocess.call(["sudo", "rm", "-rf", accomate_base_path])
        echo("🚫 Accomate setup failed, please try again.")
        exit(code=1)


@app.command()
def authenticate():
    pass


@app.command()
def init(store_name: str, version: str, store_email: str, environment: str = "production", template: str = "accomate-subscription-template"):
    """
    Initialize a new accomate store project.

    @store_name: The name of the store.
    @template: The git address of the template repository.

    """

    GITHUB_PERSONAL_TOKEN = os.environ.get("GITHUB_PERSONAL_TOKEN")

    accomate_base_domain = accomate_config.get_domain()
    machine_ip_address = accomate_config.get_public_ip()
    hosted_zone_id = accomate_config.get_zone_id()

    validate_email(store_email)

    environment = validate_enviorment(environment)

    docker_container_accoladez_store = accomate_config.get_store_service_image(
        version)
    docker_container_accoladez_auth = accomate_config.get_auth_service_image(
        version)

    echo(
        f"😉️ Choosen environment: {environment} and service version: {version}")

    echo("Calling the 🧙️ to do the 🪄️...")

    if GITHUB_PERSONAL_TOKEN is None:
        echo("💥 You must set the GITHUB_PERSONAL_TOKEN environment variable.")
        echo(
            "See https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line")
        raise typer.Exit(code=1)

    echo(f"😀️ Crafting the new store --({store_name})--")

    echo(f"Cloning template repository --({template})--")

    parsed_store_name = store_name.replace(" ", "_").lower()
    parsed_store_name = store_name.replace("-", "_").lower()

    repository_url = f"https://{GITHUB_PERSONAL_TOKEN}@github.com/Accoladez/{template}"

    repository_clone_path = f"{accomate_config.get_stores_path()}/{parsed_store_name}"

    cloned = clone_repo(repository_url, repository_clone_path)

    if cloned:
        echo("🎉 Repository cloned successfully")
        echo("Removing .git folder")
        subprocess.call(["rm", "-rf", f"{repository_clone_path}/.git"])
        echo("🎉 .git folder removed")

    if not cloned:
        echo("💥 Failed to clone repository")
        raise typer.Exit(code=1)

    # START---- TODO: Work on generating the domain and updating the DNS records. -----START

    doamin_prefix_rfc_1034 = parsed_store_name.replace("_", "-")

    base_domain = f"{doamin_prefix_rfc_1034}.{accomate_base_domain}"
    auth_domain = f'auth.{base_domain}'
    store_domain = f'store.{base_domain}'

    echo(f"Setting up store --({store_name})-- domains")

    auth_dns_response = add_dns_record(
        hosted_zone_id, "A", auth_domain, machine_ip_address)
    store_dns_response = add_dns_record(
        hosted_zone_id, "A", store_domain, machine_ip_address)

    if not auth_dns_response and not store_dns_response:
        echo("💥 Failed to add DNS record")
        raise typer.Exit(code=1)

    echo(f"🎉️ Store --({store_name})-- domains setup completed")

    # END---- TODO: Work on generating the domain and updating the DNS records. -----END

    key_response = write_all_the_keys(repository_clone_path)

    if key_response:
        echo(f"💾 All the keys are saved for --({store_name})--")
    else:
        typer.Abort("💥 Failed to write all the keys to the store.")

    echo(f"✏️ Editing docker-compose.yaml for --({store_name})--")

    docker_compose_file = f"{repository_clone_path}/docker-compose.yaml"

    compose_dict = read_yaml_file(docker_compose_file)

    # print(compose_dict)
    # exit()

    echo("💾 Updating docker-compose.yaml")

    # REDIS SETUP

    REDIS_PASSWORD = generate_random_password(22)

    compose_dict['services']['redis']['environment'][
        0] = f"REDIS_PASSWORD={REDIS_PASSWORD}"

    # REDIS PASSWORD CONF FILE SETUP
    with open(f"{repository_clone_path}/docker/redis/redis.conf", "w") as f:
        f.write(f"requirepass {REDIS_PASSWORD}")

    # compose_dict['services']['redis']['volumes'][0] = f"{parsed_store_name}-redis-data:/data"

    # MongoDB SETUP

    MONGODB_PASSWORD = generate_random_password(22)

    compose_dict['services']['mongodb']['environment'][
        0] = "MONGO_INITDB_ROOT_USERNAME=root"
    compose_dict['services']['mongodb']['environment'][
        1] = f"MONGO_INITDB_ROOT_PASSWORD={MONGODB_PASSWORD}"
    # compose_dict['services']['mongodb']['volumes'][
    #     0] = f"{parsed_store_name}-mongo-data:/data/db"

    # MySQL SETUP

    MYSQL_PASSWORD = generate_random_password(22)

    compose_dict['services']['mysql']['environment'][
        1] = f"MYSQL_ROOT_PASSWORD={MYSQL_PASSWORD}"
    compose_dict['services']['mysql']['environment'][
        2] = f"MYSQL_USER={parsed_store_name}"
    compose_dict['services']['mysql']['environment'][
        3] = f"MYSQL_PASSWORD={MYSQL_PASSWORD}"

    # Auth Service SETUP

    auth_service_port = find_open_port()

    compose_dict['services']['auth']['image'] = docker_container_accoladez_auth
    compose_dict['services']['auth']['ports'][0] = f"{auth_service_port}:8000"
    compose_dict['services']['auth']['environment'][
        0] = f"ENVIRONMENT={environment}"
    compose_dict['services']['auth']['environment'][
        1] = f"DJANGO_SUPERUSER_USERNAME={parsed_store_name}"
    compose_dict['services']['auth']['environment'][
        2] = f"DJANGO_SUPERUSER_EMAIL={store_email}"

    # Store Service SETUP

    store_service_port = find_open_port()

    compose_dict['services']['store']['image'] = docker_container_accoladez_store
    compose_dict['services']['store']['ports'][0] = f"{store_service_port}:8000"
    compose_dict['services']['store']['environment'][
        0] = f"ENVIRONMENT={environment}"
    compose_dict['services']['store']['environment'][
        1] = f"DJANGO_SUPERUSER_USERNAME={parsed_store_name}"
    compose_dict['services']['store']['environment'][
        2] = f"DJANGO_SUPERUSER_EMAIL={store_email}"

    # Celery & Celery Beat
    compose_dict['services']['celery']['image'] = docker_container_accoladez_store
    compose_dict['services']['celery-beat']['image'] = docker_container_accoladez_store

    with open(f"{repository_clone_path}/accomate.json", "w+", encoding="utf-8") as accomate:
        json_data = {
            "store": {
                "name": store_name,
                "slug": parsed_store_name,
                "email": store_email,
                "template": template,
            },
            "environment": environment,
            "version": version,
            "urls": {
                "base": base_domain,
                "store": store_domain,
                "auth": auth_domain,
            },
            "secrets": {
                "redis": REDIS_PASSWORD,
                "mongodb": MONGODB_PASSWORD,
                "mysql": MYSQL_PASSWORD
            },
            "ports": {
                "store": store_service_port,
                "auth": auth_service_port
            },
        }
        json.dump(json_data, accomate, indent=4)

    echo(f"💾 Writing docker-compose.yaml for --({store_name})--")
    write_yaml_file(docker_compose_file, compose_dict)
    echo("💾 Docker-compose.yaml is updated.")
    echo("😉️ Initialization is complete.")
    echo(
        f"🎉️ You can now run `accomate setup` in the project directory.")


@app.command()
def setup(store_url: str = "https://store-new.accomate.com", auth_url: str = "https://auth.accomate.com", plan: str = "RedirectionProcess"):
    """
    Setup the store.
    """
    accomate_base_domain = accomate_config.get_domain()
    machine_ip_address = accomate_config.get_public_ip()
    hosted_zone_id = accomate_config.get_zone_id()
    execution_directory = os.getcwd()
    auth_env_path = os.path.join(
        execution_directory, "docker", "envs", "auth.env")
    store_env_path = os.path.join(
        execution_directory, "docker", "envs", "store.env")
    project_config_path = os.path.join(execution_directory, "accomate.json")
    scope_config_path = os.path.join(
        execution_directory, "config", 'scopes.yaml')
    directory_split = execution_directory.split("/")
    project_name = directory_split[-1]

    parsed_store_name = project_name.replace(" ", "_").lower()
    parsed_store_name_dir = project_name.replace(" ", "-").lower()
    parsed_store_name_dir = project_name.replace("_", "-").lower()

    # os.chdir(f"{accomate_base_store_path}/{parsed_store_name}")

    try:
        with open(project_config_path, "r") as accomate:
            json_data = json.load(accomate)
            if not validate_project_config(json_data):
                echo("💥 The project config is not valid.")
                raise typer.Abort("💥 The project config is not valid.")
            else:
                project_config = json_data

        if not project_config:
            echo("💥 Failed to read accomate.json")
            return
        else:
            echo("Setup starting...")

            base_domain = project_config["urls"]["base"]
            auth_domain = project_config["urls"]["auth"]
            store_domain = project_config["urls"]["store"]

            if verify_dns_record(hosted_zone_id, 'A', auth_domain, machine_ip_address):
                echo(
                    f"✅ Client domain {auth_domain} is verified.")
            else:
                echo(
                    f"❌ Client domain {auth_domain} is not verified.")
                raise typer.Abort()

            if verify_dns_record(hosted_zone_id, 'A', store_domain, machine_ip_address):
                echo(
                    f"✅ Client domain {store_domain} is verified.")
            else:
                echo(
                    f"❌ Client domain {store_domain} is not verified.")
                raise typer.Abort()

            ACCOLADEZ_APP_ID = generate_store_app_id(parsed_store_name)
            ACCOLADEZ_APP_SECRET = generate_store_app_key(parsed_store_name)

            AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
            AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
            AMPQ_SERVER_URL = os.environ.get("AMPQ_SERVER_URL")
            AWS_REGION = os.environ.get("AWS_REGION")
            AWS_BUCKET = f'{parsed_store_name_dir}-accoladez'

            if AWS_KEY is None or AWS_SECRET is None:
                echo("💥 AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is not set.")
                raise typer.Abort()

            if AMPQ_SERVER_URL is None:
                echo("💥 AMPQ_SERVER_URL is not set.")
                raise typer.Abort()

            auth_env = dotenv.load_dotenv(auth_env_path, encoding="utf-8")

            echo(f"Creating bucket: {AWS_BUCKET} in {AWS_REGION}")

            bucket = s3.create_bucket(AWS_BUCKET, AWS_REGION)

            if bucket is not None:
                echo("💾 S3 Bucket created successfully.")

                scope_config = read_yaml_file(scope_config_path)

                if scope_config is not None:
                    reward_token_scopes = scope_config['plans'][plan]['scopes']['token_scopes']
                    reward_token_scopes = " ".join(reward_token_scopes)
                    dotenv.set_key(
                        auth_env_path, "REWARDS_TOKEN_SCOPES", reward_token_scopes)

                # AWS Config
                dotenv.set_key(auth_env_path,
                               "AWS_ACCESS_KEY_ID", AWS_KEY)
                dotenv.set_key(auth_env_path,
                               "AWS_SECRET_ACCESS_KEY", AWS_SECRET)
                dotenv.set_key(auth_env_path, "AWS_REGION", AWS_REGION)

                # Accoladez Config
                dotenv.set_key(auth_env_path,
                               "APP_ID", ACCOLADEZ_APP_ID)
                dotenv.set_key(auth_env_path,
                               "APP_KEY", ACCOLADEZ_APP_SECRET)

                # AMPQ Config
                dotenv.set_key(auth_env_path,
                               "AMPQ_SERVER", AMPQ_SERVER_URL)

                # DJANGO Config

                ALLOWED_HOST = [
                    auth_domain,
                    'localhost',
                ]

                ALLOWED_HOST = " ".join(ALLOWED_HOST)

                dotenv.set_key(auth_env_path,
                               "SECRET_KEY", generate_django_secret_key(55))
                dotenv.set_key(auth_env_path,
                               "ALLOWED_HOSTS", ALLOWED_HOST)

                # Remove Key Password

                if os.environ.get("GUEST_USER_PRIVATE_KEY_PASSPHRASE") is not None:
                    dotenv.unset_key(auth_env_path,
                                     "GUEST_USER_PRIVATE_KEY_PASSPHRASE")

                if os.environ.get("JWT_PRIVATE_KEY_PASSPHRASE") is not None:
                    dotenv.unset_key(auth_env_path,
                                     "JWT_PRIVATE_KEY_PASSPHRASE")

                # Auth Store Config

                store_api_url = f"https://{project_config['urls']['store']}/api/v1"
                auth_api_url = f"https://{project_config['urls']['auth']}/api/v1"

                dotenv.set_key(auth_env_path,
                               "STORE_SERVICE", store_api_url)

                # Auth MySQL Config

                MYSQL_HOST = "mysql"
                MYSQL_USER = parsed_store_name
                MYSQL_PASSWORD = project_config['secrets']['mysql']

                dotenv.set_key(auth_env_path, "DB_HOST", MYSQL_HOST)
                dotenv.set_key(auth_env_path, "DB_USER", MYSQL_USER)
                dotenv.set_key(auth_env_path,
                               "DB_PASSWORD", MYSQL_PASSWORD)
                dotenv.set_key(auth_env_path, "DB_NAME",
                               "accoladez_auth_service")

                # Email Config

                EMAIL = f"{parsed_store_name}@accoladez.com"
                SENDER_NAME = project_name.capitalize().replace("_", " ")

                dotenv.set_key(auth_env_path,
                               "SENDER_MAIL", f"{SENDER_NAME} <{EMAIL}>")

                # Auth Frontend Config

                # AUTH_FRONTEND_URL = input("Enter the Auth Frontend URL: ")
                AUTH_FRONTEND_URL = auth_url
                dotenv.set_key(auth_env_path,
                               "BASE_URL", AUTH_FRONTEND_URL)

                # JWT Config

                dotenv.set_key(auth_env_path,
                               "JWT_AUDIENCE", base_domain)
                dotenv.set_key(auth_env_path,
                               "JWT_ISSUER", accomate_base_domain)

                # CORS Config

                # STORE_FRONTEND_URL = input("Enter the Store Frontend URL: ")
                STORE_FRONTEND_URL = store_url

                CORS_ALLOWED_ORIGINS = [
                    STORE_FRONTEND_URL,
                    AUTH_FRONTEND_URL,
                ]

                CSRF_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS

                CSRF_ALLOWED_ORIGINS.append(f"https://{auth_domain}")
                CSRF_ALLOWED_ORIGINS.append(f"https://{store_domain}")

                CORS_ALLOWED_ORIGINS = " ".join(CORS_ALLOWED_ORIGINS)
                CSRF_ALLOWED_ORIGINS = " ".join(CSRF_ALLOWED_ORIGINS)

                dotenv.set_key(auth_env_path,
                               "COOKIE_HOST", f".{accomate_base_domain}")
                dotenv.set_key(auth_env_path,
                               "CORS_ALLOWED_ORIGINS", CORS_ALLOWED_ORIGINS)
                dotenv.set_key(auth_env_path,
                               "CSRF_TRUSTED_ORIGINS", CSRF_ALLOWED_ORIGINS)

                # Store ENV Config

                store_env = dotenv.load_dotenv(
                    store_env_path, encoding="utf-8")

                # CORS Config

                dotenv.set_key(store_env_path,
                               "COOKIE_HOST", f".{base_domain}")
                dotenv.set_key(store_env_path,
                               "CORS_ALLOWED_ORIGINS", CORS_ALLOWED_ORIGINS)
                dotenv.set_key(store_env_path,
                               "CSRF_TRUSTED_ORIGINS", CORS_ALLOWED_ORIGINS)

                # JWT Config

                dotenv.set_key(store_env_path,
                               "JWT_AUDIENCE", base_domain)
                dotenv.set_key(store_env_path,
                               "JWT_ISSUER", accomate_base_domain)

                # Store Auth Config
                dotenv.set_key(store_env_path,
                               "BASE_URL", AUTH_FRONTEND_URL)

                # AWS Config
                dotenv.set_key(store_env_path,
                               "AWS_ACCESS_KEY_ID", AWS_KEY)
                dotenv.set_key(store_env_path,
                               "AWS_SECRET_ACCESS_KEY", AWS_SECRET)
                dotenv.set_key(store_env_path,
                               "AWS_S3_REGION_NAME", AWS_REGION)
                dotenv.set_key(store_env_path,
                               "AWS_STORAGE_BUCKET_NAME", AWS_BUCKET)

                # AMPQ Config

                dotenv.set_key(store_env_path,
                               "AMPQ_SERVER", AMPQ_SERVER_URL)

                dotenv.set_key(store_env_path,
                               "SENDER_MAIL", f"{SENDER_NAME} <{EMAIL}>")

                # DJANGO Config

                store_service_url = project_config['urls']['store']

                ALLOWED_HOST = [
                    store_service_url,
                    'localhost',
                ]

                ALLOWED_HOST = " ".join(ALLOWED_HOST)

                dotenv.set_key(store_env_path,
                               "SECRET_KEY", generate_django_secret_key(55))
                dotenv.set_key(store_env_path,
                               "ALLOWED_HOSTS", ALLOWED_HOST)

                # Remove Key Password

                if os.environ.get("GUEST_USER_PRIVATE_KEY_PASSPHRASE") is not None:
                    dotenv.unset_key(store_env_path,
                                     "GUEST_USER_PRIVATE_KEY_PASSPHRASE")

                if os.environ.get("JWT_PRIVATE_KEY_PASSPHRASE") is not None:
                    dotenv.unset_key(store_env_path,
                                     "JWT_PRIVATE_KEY_PASSPHRASE")

                # MongoDB Config

                MONGODB_PASSWORD = project_config['secrets']['mongodb']

                dotenv.set_key(store_env_path,
                               "DB_NAME", "store_service")
                dotenv.set_key(store_env_path,
                               "DB_CLIENT_HOST", "mongodb")
                dotenv.set_key(store_env_path,
                               "DB_CLIENT_USERNAME", "root")
                dotenv.set_key(store_env_path,
                               "DB_CLIENT_PASSWORD", MONGODB_PASSWORD)

                # Redis Config

                REDIS_PASSWORD = project_config['secrets']['redis']

                dotenv.set_key(store_env_path,
                               "DB_CACHES_LOCATION", f"redis://redis:6379")
                dotenv.set_key(store_env_path, "DB_CACHES_DB", "1")
                dotenv.set_key(store_env_path,
                               "DB_CACHES_PASSWORD", REDIS_PASSWORD)
                dotenv.set_key(store_env_path,
                               "DB_CACHES_KEY_PREFIX", parsed_store_name)

                dotenv.set_key(store_env_path, "AUTH_SERVER_URL", auth_api_url)

                echo("😉️ Setup is done.")
                echo(
                    f"🎉️ You can now run `accomate up` in the project directory.")

            else:
                echo("💥 Bucket already exists.")
                raise typer.Abort()

    except FileNotFoundError as e:
        echo("💥 The store is not initialized.")
        raise typer.Abort("💥 The store is not initialized.")
    except Exception as e:
        print(e)
        echo(f"💥 {e}")
        raise typer.Abort()


@app.command()
def up(restart: bool = False, nginx: bool = True, time_period: int = False, period: str = "minutes"):
    """
    Up the store
    """
    # compose up the docker-compose.yaml
    try:

        base_nginx_path = accomate_config.get_nginx_path()
        execution_directory = os.getcwd()
        project_config_path = os.path.join(
            execution_directory, "accomate.json")
        directory_split = execution_directory.split("/")
        project_name = directory_split[-1]

        parsed_dir = project_name.replace(" ", "_")

        try:
            with open(project_config_path, "r") as config:
                project_config = json.load(config)
                if not validate_project_config(project_config):
                    echo("💥 The project config is not valid.")
                    raise typer.Abort("💥 The project config is not valid.")

        except FileNotFoundError as e:
            echo("💥 The store is not initialized.")
            raise typer.Abort("💥 The store is not initialized.")

        # Loading important configs
        base_domain = project_config["urls"]["base"]
        auth_domain = project_config["urls"]["auth"]
        store_domain = project_config["urls"]["store"]

        auth_service_proxy_pass = f"http://localhost:{project_config['ports']['auth']}"
        store_service_proxy_pass = f"http://localhost:{project_config['ports']['store']}"

        auth_service_static_files_path = f"{execution_directory}/static/auth"
        store_service_static_files_path = f"{execution_directory}/static/store"

        echo("🚀 Uping the store...")

        is_up = compose_up(execution_directory)

        # total_service_start_wait_time = 20  # TODO: Please change it to 20
        # echo("🚀 Waiting for services to start...")
        # with typer.progressbar(range(total_service_start_wait_time)) as progress:
        #     for i in progress:
        #         time.sleep(1)

        echo("Services are up.")

        if restart:
            service_containers = get_containers_on_same_network(
                f"{parsed_dir}_default")
            services_by_tags = assign_service_type_tag(
                service_containers, parsed_dir)
            auth_container_id = services_by_tags['auth'].get('id')
            auth_restart_response = restart_containers(auth_container_id)
            if auth_restart_response:
                echo("\n🚀 Auth service restarted.")
            else:
                echo("💥 Auth service failed to restart.")

        if nginx:
            echo("🚀 Starting Nginx setup")
            try:
                with open(f"{absolute_package_path}/conf/nginx/site.conf", "r") as site_template:
                    template = site_template.read()

                    auth_nginx_site_config = template
                    store_nginx_site_config = template

                    os.makedirs(base_nginx_path, exist_ok=True)

                    base_nginx_site_log_path = f"{execution_directory}/logs/nginx"
                    auth_nginx_site_log_path = f"{execution_directory}/logs/nginx/auth"
                    store_nginx_site_log_path = f"{execution_directory}/logs/nginx/store"

                    os.makedirs(base_nginx_site_log_path, exist_ok=True)
                    os.makedirs(auth_nginx_site_log_path, exist_ok=True)
                    os.makedirs(store_nginx_site_log_path, exist_ok=True)

                    # Mofifing the template for auth_service
                    auth_nginx_site_config = auth_nginx_site_config.replace(
                        "#domain#", base_domain)
                    auth_nginx_site_config = auth_nginx_site_config.replace(
                        "#static_files_path#", auth_service_static_files_path)
                    auth_nginx_site_config = auth_nginx_site_config.replace(
                        "#proxy_pass_uri#", auth_service_proxy_pass)
                    auth_nginx_site_config = auth_nginx_site_config.replace(
                        "#access_log#", f"{auth_nginx_site_log_path}/access.log")
                    auth_nginx_site_config = auth_nginx_site_config.replace(
                        "#error_log#", f"{auth_nginx_site_log_path}/error.log")

                    echo("Writing client auth site nginx conf...")
                    with open(f"{base_nginx_path}/{auth_domain}.conf", "w+") as f:
                        f.write(auth_nginx_site_config)

                    # Mofifing the template for store_service
                    store_nginx_site_config = store_nginx_site_config.replace(
                        "#domain#", base_domain)
                    store_nginx_site_config = store_nginx_site_config.replace(
                        "#static_files_path#", store_service_static_files_path)
                    store_nginx_site_config = store_nginx_site_config.replace(
                        "#proxy_pass_uri#", store_service_proxy_pass)
                    store_nginx_site_config = store_nginx_site_config.replace(
                        "#access_log#", f"{store_nginx_site_log_path}/access.log")
                    store_nginx_site_config = store_nginx_site_config.replace(
                        "#error_log#", f"{store_nginx_site_log_path}/error.log")

                    echo("Writing client store site nginx conf...")
                    with open(f"{base_nginx_path}/{store_domain}.conf", "w+") as f:
                        f.write(store_nginx_site_config)

                    restart_nginx()

                    echo("✅ Nginx is up.")

            except FileNotFoundError as e:
                print(e)
                echo("💥 Not able to find template site.conf.")
                raise typer.Abort()
            except Exception as e:
                print(e)
                echo("💥 Not able to find template site.conf.")
                raise typer.Abort()

        else:
            client_auth_nginx_site_config_exists = os.path.exists(
                f"{base_nginx_path}/{auth_domain}.conf")

            client_store_nginx_site_config_exists = os.path.exists(
                f"{base_nginx_path}/{store_domain}.conf")

            if client_auth_nginx_site_config_exists and client_store_nginx_site_config_exists:
                echo("Nginx confs are already available.")
            else:
                echo("Forcefully blocking Nginx configuration auto-setup.")

    except Exception as e:
        echo(f"💥 {e}")
        raise typer.Abort()


@app.command("config-ssl")
def config_ssl():
    try:
        execution_directory = os.getcwd()
        project_config_path = os.path.join(
            execution_directory, "accomate.json")
        directory_split = execution_directory.split("/")
        project_name = directory_split[-1]

        try:
            with open(project_config_path, "r") as config:
                project_config = json.load(config)
                if not validate_project_config(project_config):
                    echo("💥 The project config is not valid.")
                    raise typer.Abort("💥 The project config is not valid.")

        except FileNotFoundError as e:
            echo("💥 The store is not initialized.")
            raise typer.Abort("💥 The store is not initialized.")

        echo(f"Running SSL for {project_name}")

        auth_domain = project_config['urls']['auth']
        store_domain = project_config['urls']['store']
        store_email = project_config['store']['email']

        echo("🔒 Let's Encrypt Setup")

        add_lets_encrypt_certificate(auth_domain, store_email)
        add_lets_encrypt_certificate(store_domain, store_email)

        echo("🔒 Let's Encrypt Setup Done")

        echo("🚀 Re-starting Nginx...")

        restart_nginx()

        echo("✅ Nginx is up.")
    except Exception as e:
        echo(f"💥 {e}")
        raise typer.Abort()


@app.command()
def health(exec=""):
    try:
        execution_directory = os.getcwd()
        project_config_path = os.path.join(
            execution_directory, "accomate.json")
        directory_split = execution_directory.split("/")
        project_name = directory_split[-1]
        parsed_dir = project_name.replace(" ", "_")

        try:
            with open(project_config_path, "r") as config:
                project_config = json.load(config)
                if not validate_project_config(project_config):
                    echo("💥 The project config is not valid.")
                    raise typer.Abort("💥 The project config is not valid.")

        except FileNotFoundError as e:
            echo("💥 The store is not initialized.")
            raise typer.Abort("💥 The store is not initialized.")

        auth_domain = project_config['urls']['auth']
        store_domain = project_config['urls']['store']

        auth_domain = f'https://{auth_domain}'
        store_domain = f'https://{store_domain}'

        echo(f"Health check for {auth_domain} and {store_domain}")

        is_up = False

        while not is_up:
            try:
                auth_response = httpx.get(auth_domain)
                store_response = httpx.get(store_domain)
                if auth_response is not None and store_response is not None:
                    p_status = (auth_response.status_code //
                                500) == (store_response.status_code // 500)
                    if not p_status:
                        is_up = True
                        echo("✅ It's up and running")
            except Exception as e:
                echo("🔄 Waiting for 1 sec...")
                sleep(1)

        if exec != "":

            keys_path = os.path.join(
                execution_directory, 'config', 'keys.yaml')

            does_key_exists = False

            while not does_key_exists:
                if os.path.exists(keys_path):
                    sleep(2)
                    echo(f"Found {keys_path}")
                    does_key_exists = True
                else:
                    echo("🔄 Waiting for 1 sec...")
                    sleep(1)

            if does_key_exists:
                echo(f"Executing {exec}...")
                service_containers = get_containers_on_same_network(
                    f"{parsed_dir}_default")
                services_by_tags = assign_service_type_tag(
                    service_containers, parsed_dir)
                auth_container_id = services_by_tags['auth'].get('id')
                res = exec_run(auth_container_id, exec)
                if res.exit_code == 0:
                    echo("Executed !!")
                else:
                    echo("Execution failed !!")

    except Exception as e:
        echo(f"💥 {e}")
        raise typer.Abort()

@app.command()
def finalize():
    try:

        execution_directory = os.getcwd()
        project_config_path = os.path.join(
            execution_directory, "accomate.json")

        try:
            with open(project_config_path, "r") as config:
                project_config = json.load(config)
                if not validate_project_config(project_config):
                    echo("💥 The project config is not valid.")
                    raise typer.Abort("💥 The project config is not valid.")

        except FileNotFoundError as e:
            echo("💥 The store is not initialized.")
            raise typer.Abort("💥 The store is not initialized.")

        echo("🚀 Finalizing...")
        subprocess.call(["pwd"])
        subprocess.call(["sudo", "chmod", "-R", "777", "static/"])
        subprocess.call(["sudo", "chown", "-R", f"{USER}:{USER}", "static/"])

        echo("🚀 Finalizing Done")
    except Exception as e:
        echo(f"💥 {e}")
        raise typer.Abort()


@app.command()
def down():
    """
    Down the store
    """
    try:

        execution_directory = os.getcwd()
        project_config_path = os.path.join(
            execution_directory, "accomate.json")

        try:
            with open(project_config_path, "r") as config:
                project_config = json.load(config)
                if not validate_project_config(project_config):
                    echo("💥 The project config is not valid.")
                    raise typer.Abort("💥 The project config is not valid.")

        except FileNotFoundError as e:
            echo("💥 The store is not initialized.")
            raise typer.Abort("💥 The store is not initialized.")

        echo("🚀 Downing the store...")
        compose_down(execution_directory)

        echo("🚀 Closed")
    except Exception as e:
        echo(f"💥 {e}")
        raise typer.Abort()
