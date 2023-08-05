"""CLI's project member add subcommand"""

import warnings
from typing import Optional

import click

from kili.cli.common_args import Arguments, Options, from_csv
from kili.cli.project.member.helpers import (
    check_exclusive_options,
    collect_members_from_csv,
    collect_members_from_emails,
    collect_members_from_project,
)
from kili.client import Kili


# pylint: disable=too-many-arguments
@click.command(name="add")
@Options.api_key
@Options.endpoint
@Arguments.emails
@Options.project_id
@Options.role
@from_csv(["email"], ["role"])
@Options.from_project
def add_member(
    api_key: Optional[str],
    endpoint: Optional[str],
    emails: Optional[str],
    project_id: str,
    role: Optional[str],
    csv_path: Optional[str],
    project_id_src: Optional[str],
):
    """Add members to a Kili project

    Emails can be passed directly as arguments.
    You can provide several emails separated by spaces.

    \b
    !!! Examples
        ```
        kili project member add \\
            --project-id <project_id> \\
            --role REVIEWER \\
            john.doe@test.com jane.doe@test.com
        ```
        ```
        kili project member add \\
            --project-id <project_id> \\
            --from-csv path/to/members.csv
        ```
        ```
        kili project member add \\
            --project-id <project_id> \\
            --from-project <project_id_scr>
        ```
    """
    kili = Kili(api_key=api_key, api_endpoint=endpoint)
    check_exclusive_options(csv_path, project_id_src, emails, None)

    if csv_path is not None:
        members_to_add = collect_members_from_csv(csv_path, role)
    elif project_id_src is not None:
        members_to_add = collect_members_from_project(kili, project_id_src, role)
    else:
        members_to_add = collect_members_from_emails(emails, role)

    count = 0
    existing_members = kili.project_users(project_id=project_id, disable_tqdm=True)
    existing_members = [
        member["user"]["email"] for member in existing_members if member["activated"]
    ]

    for member in members_to_add:
        if member["email"] in existing_members:
            already_member = member["email"]
            warnings.warn(
                f"{already_member} is already an active member of the project."
                " Use kili project member update to update role."
            )
        else:
            kili.append_to_roles(
                project_id=project_id, user_email=member["email"], role=member["role"]
            )
            count += 1

    print(f"{count} users have been successfully added to project: {project_id}")
