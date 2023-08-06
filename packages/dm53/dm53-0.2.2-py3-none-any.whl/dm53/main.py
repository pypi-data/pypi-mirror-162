#!/usr/bin/env python

import logging
import os
import time
from pathlib import Path

import boto3
import typer

from dm53.models.domain import RegisterDomainDetails

# configure typer cli app
app = typer.Typer(add_completion=False)

# configure logger
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dm53")


@app.command()
def check(
    domain_name: str = typer.Option(
        ...,
        help="The name of the domain `example.com`.",
    ),
    monitor: bool = typer.Option(
        default=False,
        help="Whether to keep checking until the domain becomes available.",
    ),
    interval: int = typer.Option(
        default=5,
        min=1,
        help="How often in seconds to check the availability of the domain.",
    ),
    register: bool = typer.Option(
        default=False,
        help="Whether to register the given domain if available.",
    ),
    path: Path = typer.Option(
        default="/",
        help="The path to a JSON file containing registration details.",
    ),
) -> None:
    """Check availability of a domain name."""

    _validate_aws_caller_identity()

    # configure boto client
    # domain requests can only be made to us-east-1 at the time of writing
    # see https://docs.aws.amazon.com/general/latest/gr/r53.html
    route53 = boto3.client("route53domains", region_name="us-east-1")

    registration_details = None
    if register:
        # get and validate details before monitoring
        registration_details = _get_registration_details(path)

    availability = None
    if monitor:
        while availability != "AVAILABLE":
            try:
                logger.info(
                    f"Checking availability for domain: '{domain_name}'"
                )
                res = route53.check_domain_availability(DomainName=domain_name)
                availability = res.get("Availability")
                logger.info(f"Availability: {availability}\n")
            except Exception as e:
                logger.error(e)
                logger.warning("Got error from AWS, sleeping 5 seconds")
                # sleep in case some aws limit/quota is exceeded, in the future
                # implement exponential backoff
                time.sleep(5)

            if availability != "AVAILABLE":
                # sleep the specified interval before checking again
                time.sleep(interval)
    else:
        try:
            logger.info(f"Checking availability for domain: '{domain_name}'")
            res = route53.check_domain_availability(DomainName=domain_name)
            availability = res.get("Availability")
            logger.info(f"Availability: {availability}\n")
        except Exception as e:
            logger.error(e)
            raise typer.Abort()

    if register and availability == "AVAILABLE":
        operation_id = None
        logger.info(f"Registering domain: '{registration_details.DomainName}'")
        try:
            res = route53.register_domain(**registration_details.dict())
            operation_id = res.get("OperationId")
        except Exception as e:
            logger.error(e)
            raise typer.Abort()

        logger.info(f"Registration successful. OperationId: '{operation_id}'")


@app.command()
def validate_registration_details(
    path: Path = typer.Option(
        ...,
        help="The path to a JSON file containing registration details.",
    ),
) -> None:
    """Validate registration details."""

    _get_registration_details(path)


@app.command()
def example_registration_details() -> None:
    """Print example registration details."""

    registration_details = Path(
        os.path.join(
            os.path.dirname(__file__),
            "../../example-registration-details.json",
        )
    ).read_text()
    print(registration_details)


def _validate_aws_caller_identity() -> None:
    """Validate AWS caller identity.

    Raises:
        Error: If unable to locate credentials
    """

    logger.info("Validating AWS caller identity")
    try:
        sts = boto3.client("sts")
        res = sts.get_caller_identity()
    except Exception as e:
        logger.error(e)
        raise typer.Abort()
    logger.info(f"AWS caller identity: '{res['UserId']}'\n")


def _get_registration_details(path: Path) -> RegisterDomainDetails:
    """Get and validate registration details.

    Args:
        path: The path to a JSON file containing registration details

    Raises:
        Error: If file not found or invalid details
    """

    if not path.exists():
        logger.error(f"The path '{path}' doesn't exist")
        raise typer.Abort()

    if not path.is_file() or not str(path).endswith("json"):
        logger.error(f"The path '{path}' doesn't point to a JSON file")
        raise typer.Abort()

    logger.info("Validating domain registration file")
    try:
        details = RegisterDomainDetails.parse_raw(path.read_text())
    except Exception as e:
        logger.error(e)
        raise typer.Abort()
    logger.info("Validation successful")
    return details


if __name__ == "__main__":
    app()
