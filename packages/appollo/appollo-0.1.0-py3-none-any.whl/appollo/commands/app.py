import click


@click.group()
def app():
    """ Subcommands to manage your applications on Appollo. """


@app.command()
def ls():
    """ Lists the applications to which the logged in user has access.

    \f
    Example output:

    .. image:: /img/appollo-ls.png
        :alt: example output of the appollo ls command
        :align: center

    Usage:
    """
    from rich.table import Table
    from rich.syntax import Syntax

    from appollo import api
    from appollo.settings import console

    apps = api.get("/applications/")

    if apps:
        table_apps = Table()
        table_apps.add_column("KEY")
        table_apps.add_column("Name")
        table_apps.add_column("Apple Name")
        table_apps.add_column("Bundle ID")
        table_apps.add_column("Account")
        for app in apps:
            table_apps.add_row(app['key'], app['name'], app['apple_name'], app['bundle_id'], app['account']['name'] + " (" + app['account']['key'] + ")")

        console.print(table_apps)
    else:
        code = Syntax(
            code="$ appollo app mk --name NAME --bundle-id BUNDLE_ID --account-key APPLE_DEVELOPER_ACCOUNT_KEY",
            lexer="shell")
        console.print(f"You did not register any apps. Create one with")
        console.print(code)


@app.command()
@click.option('--name', prompt=True, help="Your application name")
@click.option('--bundle-id', prompt=True, help="The bundle ID for your app on Apple (e.g.: com.company.appname)")
@click.option('--account-key', prompt=True, help="Appollo key to the Apple Developer Account")
def mk(name, bundle_id, account_key):
    """ Creates a new application.

    ..note: This will also create an application with this bundle ID on your Developer Account. This allows us to verify the validity of your bundle ID
     """
    from appollo import api
    from appollo.settings import console

    application = api.post(
        "/applications/",
        json_data={
            "name": name,
            "bundle_id": bundle_id,
            "account": account_key,
            "apple_create": True,
        }
    )

    if application:
        console.print(f"Congratulations! Your application {application['apple_name']} has been created "
                      f"in Appollo as {application['name']} with key \"{application['key']}\" and on the "
                      f"App Store as ID \"{application['apple_id']}\"")


@app.command()
@click.argument('key', required=True)
@click.option('--delete-on-apple', is_flag=True, help="Also delete the app on Apple")
def rm(key, delete_on_apple):
    """ Deletes the application with key \"KEY\" from Appollo and on Apple if specified. """
    from appollo import api
    from appollo.settings import console

    url = f"/applications/{key}"
    if delete_on_apple:
        url += "?apple=1"
    account = api.delete(url)

    if account:
        console.print(f"Application with key \"{key}\" successfully removed.")


@app.command("link")
@click.argument('key', required=True)
@click.option('--team-key', prompt=True, help="Key of the team to link")
def link(key, team_key):
    """ Links an application to Appollo team with key \"KEY\".

    \f
    .. warning:: All users who are in a team linked to an Apple Developer Account have full control over it.
    """
    from appollo import api
    from appollo.settings import console

    try:
        teams = api.post(f"/applications/{key}/teams/{team_key}/")
    except api.NotFoundException:
        console.print("This application or team does not exist or you do not have access to it")
        return

    if teams:
        console.print(f"Team \"{team_key}\" is now linked to application \"{key}\".")


@app.command("unlink")
@click.argument('key', required=True)
@click.option('--team-key', prompt=True, help="Key of the team to link")
def unlink(key, team_key):
    """ Links or unlinks an application to Appollo team with key \"KEY\".
    """
    from appollo import api
    from appollo.settings import console

    deleted = api.delete(f"/applications/{key}/teams/{team_key}/")

    if deleted:
        console.print(f"Team \"{team_key}\" is now unlinked from application \"{key}\".")


@app.command("import")
@click.option('--name', prompt=True, help="How you want to name your app in Appollo")
@click.option('--bundle-id', prompt=True, help="The bundle ID for your app on Apple (e.g.: com.company.appname)")
@click.option('--account-key', prompt=True, help="Appollo key to the Apple Developer Account")
def import_app(name, bundle_id, account_key):
    """ Imports an application from Apple Developer to Appollo. """
    from appollo import api
    from appollo.settings import console

    application = api.post(
        "/applications/",
        json_data={
            "name": name,
            "bundle_id": bundle_id,
            "account": account_key,
            "apple_create": False,
        }
    )

    if application:
        console.print(f"Congratulations! Your application {application['apple_name']} has been imported on Appollo "
                      f"as {application['name']}. It is registered with key \"{application['key']}\".")
