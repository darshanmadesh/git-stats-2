import requests
import os
import json
import yaml

# GitHub GraphQL API endpoint
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

# GraphQL query
GRAPHQL_QUERY = """
    query user($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoriesWithContributedCommits
          totalRepositoriesWithContributedPullRequests
          totalRepositoriesWithContributedPullRequestReviews
          commitContributionsByRepository { repository { name } contributions { totalCount } }
          pullRequestContributionsByRepository { repository { name } contributions { totalCount } }
          pullRequestReviewContributionsByRepository { repository { name } contributions { totalCount } }
        }
      }
    }
"""


# Function to make the GraphQL query
def make_query(json_query, headers):
    response = requests.post(GITHUB_GRAPHQL_URL, json=json_query, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

# Function to read team members file
def read_members_file(team_name='k8s_team'):
    file_path = os.path.join(os.path.dirname(__file__), 'teams', team_name, 'members.yml')

    with open(file_path, 'r') as file:
        members = yaml.safe_load(file)
    
    print(f"{team_name} members are : {members["members"]}")
    
    return members["members"]

def fetch_stats(team_members, github_token, from_date, to_date):
    
    # Define Request header
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json"
    }

    # Aggregated Team Result
    team_result = {}

    # Make the query for each user
    for member in team_members:
        # Prepare query
        variable = {
            "login": member,
            "from": f"{from_date}T00:00:00Z",
            "to": f"{to_date}T00:00:00Z"            
        }
        json_query = {
            "query": GRAPHQL_QUERY,
            "variables": variable
        }
        # Send the query and fetch the data
        member_result = make_query(json_query, headers)
        print(f"Member: {member}, Result: {member_result}")

        team_result[member] = member_result

    return team_result



def main():

    # Prepare environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise Exception("Please set the GITHUB_TOKEN environment variable.")
    from_date = os.getenv("FROM_DATE")
    if not from_date:
        raise Exception("Please pass the FROM_DATE input.")
    to_date = os.getenv("TO_DATE")
    if not to_date:
        raise Exception("Please pass the TO_DATE input.")

    team_members = read_members_file()

    fetch_stats(team_members, github_token, from_date, to_date)



if __name__ == "__main__":
    main()