import click
import sys

from stoobly_agent.app.settings import Settings
from stoobly_agent.lib.api.keys import InvalidOrganizationKey, InvalidProjectKey, InvalidReportKey, InvalidRequestKey, InvalidScenarioKey
from stoobly_agent.lib.api.keys import OrganizationKey, ProjectKey, ReportKey, RequestKey, ScenarioKey
from stoobly_agent.lib.logger import Logger

# Print

def print_invalid_key(resource: str):
  print(f"Error: Invalid {resource} key", file=sys.stderr) 

# Handle

def handle_invalid_key(resource: str):
  print_invalid_key(resource)
  sys.exit(1)

def handle_missing_key(resource: str):
  print(f"Error: Missing {resource} key", file=sys.stderr) 
  sys.exit(1)

# Validate

def validate_organization_key(organization_key) -> OrganizationKey:
  try:
    return OrganizationKey(organization_key)
  except InvalidOrganizationKey:
    handle_invalid_key('organization') if organization_key else handle_missing_key('organization')

def validate_project_key(project_key) -> ProjectKey:
  try:
    return ProjectKey(project_key)
  except InvalidProjectKey:
    handle_invalid_key('project') if project_key else handle_missing_key('project')

def validate_report_key(report_key) -> ReportKey:
  try:
    return ReportKey(report_key)
  except InvalidReportKey:
    handle_invalid_key('report') if report_key else handle_missing_key('report')

def validate_request_key(request_key) -> RequestKey:
  try:
    return RequestKey(request_key)
  except InvalidRequestKey:
    handle_invalid_key('request') if request_key else handle_missing_key('request')

def validate_scenario_key(scenario_key) -> ScenarioKey:
  try:
    return ScenarioKey(scenario_key)
  except InvalidScenarioKey:
    handle_invalid_key('scenario') if scenario_key else handle_missing_key('scenario')

# Prompt

def prompt_project_key(settings: Settings):
  while True:
    project_key = click.prompt('Please enter a project key', type=str)

    try:
      ProjectKey(project_key)
      break
    except InvalidProjectKey:
      print_invalid_key('project')
      print(f"Try `stoobly-agent project list` to find a project key", file=sys.stderr) 

  settings.proxy.intercept.project_key = project_key
  settings.commit()

  return project_key

# Resolve

def resolve_project_key(kwargs: dict, settings: Settings) -> str:
    project_key = kwargs.get('project_key')

    if not project_key:
      project_key = settings.proxy.intercept.project_key

      if not project_key or len(project_key) == 0:
        project_key = prompt_project_key(settings)

    return project_key

def resolve_project_key_and_validate(kwargs: dict, settings: Settings  = Settings.instance()) -> str:
    project_key = resolve_project_key(kwargs, settings)

    validate_project_key(project_key)

    return project_key

def resolve_scenario_key(kwargs: dict, settings: Settings) -> str:
    scenario_key = kwargs.get('key')

    if not scenario_key:
        project_key = validate_project_key(settings.proxy.intercept.project_key)
        data_rule = settings.proxy.data.data_rules(project_key.id)
        scenario_key = data_rule.scenario_key
        #Logger.instance().info(f"No scenario key specified, using {scenario_key}")

    return scenario_key

def resolve_scenario_key_and_validate(kwargs: dict, settings: Settings = Settings.instance()) -> str:
    scenario_key = resolve_scenario_key(kwargs, settings)

    validate_scenario_key(scenario_key)

    return scenario_key