""" Delete the DB """
from mcli.api.engine.engine import run_graphql_success_query
from mcli.api.engine.utils import dedent_indent


def nuke_db() -> bool:
    """Runs a GraphQL query to wipe the DB

    Returns:
        Returns true if successful
    """

    query = dedent_indent("""
    mutation Mutation {
        nukeEverything
    }
    """)
    r = run_graphql_success_query(query=query, query_function='nukeEverything')
    r.result(timeout=10)
    return True
