from datateer_cli.commands.pipeline import aws_deploy_flow, gcp_deploy_flow


def do_deploy(
    flow,
    cloud,
    account,
    region,
    client_code,
    environment,
    custom_modules=[],  # list of tuples: full_path, rel_path
    prefect_api_key=None,
    deploy_key_prefect_lib=None,
    prefect_results_bucket=None,
    debug=False,
):
    if cloud == "aws":
        aws_deploy_flow.do_deploy(
            flow,
            account,
            region,
            client_code,
            environment,
            custom_modules,
        )
    elif cloud == "gcp":
        gcp_deploy_flow.do_deploy(
            flow,
            account,
            region,
            client_code,
            environment,
            custom_modules,
        )
    else:
        raise Exception("Cloud Provider supplied has not been implemented yet")
