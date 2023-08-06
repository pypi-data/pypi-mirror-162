import logging
import os

from dotenv import load_dotenv
from jinja2 import Environment, PackageLoader, select_autoescape

PACKAGE_PATH = os.path.dirname(__file__)

load_dotenv(override=True)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

JINJA_ENV = Environment(loader=PackageLoader("fhir_cli"), autoescape=select_autoescape())

# FHIR

FHIR_API_URL = os.environ.get("FHIR_API_URL", "http://localhost:8080/fhir")
FHIR_API_USER = os.environ.get("FHIR_API_USER")
FHIR_API_PASSWORD = os.environ.get("FHIR_API_PASSWORD")
FHIR_COLUMN_NAME = "fhir"

# OMOP

OMOP_TEMPLATES = (
    "01-OMOPCDM_postgresql_5.4_ddl.sql.j2",
    "02-OMOPCDM_postgresql_5.4_primary_keys.sql.j2",
    "03-vocabulary.sql.j2",
    "04-OMOPCDM_postgresql_5.4_constraints.sql.j2",
    "05-OMOPCDM_postgresql_5.4_indices.sql.j2",
)

# DBT

DBT_SCHEMA = os.environ.get("DBT_SCHEMA", "dbt")
FHIR_DBT_SCHEMA = f"{DBT_SCHEMA}_fhir"
OMOP_DBT_SCHEMA = f"{DBT_SCHEMA}_omop"
DBT_MODELS_DIR = "models"
DBT_META_TABLE = "_meta"
INIT_DB_TEMPLATE = "init_db.sql.j2"
MAPPING_DIR_NAME = os.environ.get("MAPPING_DIR_NAME", "schemas")

# Postgres

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "secret")
POSTGRES_SERVER_NAME = os.environ.get("POSTGRES_SERVER_NAME", "postgres")

# Functions

FUNCTIONS_DIR_NAME = "functions"

# Connect

CONNECT_URL = os.environ.get("CONNECT_URL", "http://localhost:8083")
POSTGRES_SOURCE_CONNECTOR_TEMPLATE = "postgres_source_connector.json.j2"
