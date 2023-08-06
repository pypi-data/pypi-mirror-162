#!/usr/bin/env python3

# Standard libraries
import argparse
import sys

# Modules libraries
import gitlab

# Constants
NAME = 'gitlab-issues-sync'

# Main, pylint: disable=too-many-branches,too-many-locals,too-many-statements
def main():

    # Arguments creation
    parser = argparse.ArgumentParser(
        prog=NAME,
        description=f'{NAME}: Synchronize issues from a GitLab project to another',
        add_help=False, formatter_class=argparse.RawTextHelpFormatter)

    # Arguments optional definitions
    parser.add_argument('-h', dest='help', action='store_true',
                        help='Show this help message')
    parser.add_argument('-i', dest='input_gitlab', default='https://gitlab.com',
                        help='Input GitLab URL (defaults to https://gitlab.com)')
    parser.add_argument('-o', dest='output_gitlab', default='https://gitlab.com',
                        help='Output GitLab URL (defaults to https://gitlab.com)')

    # Arguments positional definitions
    parser.add_argument('input_project', nargs='?', help='Input project ID number')
    parser.add_argument('output_project', nargs='?', help='Output project ID number')
    parser.add_argument('input_token', nargs='?', help='Input project token credential')
    parser.add_argument('output_token', nargs='?',
                        help='Output project token credential (defaults to output_token)')

    # Arguments helper
    options = parser.parse_args()
    if options.help or not options.input_project or not options.output_project \
            or not options.input_token:
        print(' ')
        parser.print_help()
        print(' ', flush=True)
        sys.exit(0)

    # Arguments adaptations
    if not options.output_token:
        options.output_token = options.output_token

    # Variables
    issues_new = []
    issues_remove = []
    issues_updates = []
    labels_new = []
    labels_remove = []
    labels_updates = []
    milestones_new = []
    milestones_remove = []
    milestones_updates = []

    # Label parser
    def label_parser(label):
        return {
            'name': label.name,
            'color': label.color,
            'description': label.description,
            'priority': label.priority,
        }

    # Label updater
    def label_updater(label, data):
        label.name = data['name']
        label.color = data['color']
        label.description = data['description']
        label.priority = data['priority']
        return label

    # Milestone parser
    def milestone_parser(milestone):
        return {
            'title': milestone.title,
            'description': milestone.description,
            'state': milestone.state,
            'due_date': milestone.due_date,
            'start_date': milestone.start_date,
        }

    # Milestone updater
    def milestone_updater(milestone, data):
        milestone.title = data['title']
        milestone.description = data['description']
        milestone.state = data['state']
        milestone.due_date = data['due_date']
        milestone.start_date = data['start_date']
        milestone.state_event = 'close' if milestone.state == 'closed' else 'activate'
        return milestone

    # Issue parser
    def issue_parser(issue, milestones, users):
        milestone_id = 0
        assignee_ids = []
        if issue.milestone:
            for milestone in milestones:
                if issue.milestone['title'] == milestone.title:
                    milestone_id = milestone.id
                    break
        if issue.assignees:
            for assignee in issue.assignees:
                for user in users:
                    if user.username == assignee['username']:
                        assignee_ids += [user.id]
                        break
        return {
            'iid': issue.iid,
            'title': issue.title,
            'description': issue.description,
            'state': issue.state,
            'labels': issue.labels,
            'milestone_id': milestone_id,
            'assignee_ids': assignee_ids,
        }

    # Issue updater
    def issue_updater(issue, data):
        issue.iid = data['iid']
        issue.title = data['title']
        issue.description = data['description']
        issue.state = data['state']
        issue.labels = data['labels']
        issue.milestone_id = data['milestone_id']
        issue.assignee_ids = data['assignee_ids']
        issue.state_event = 'close' if issue.state == 'closed' else 'reopen'
        return issue

    # Header
    print('', flush=True)

    # Input login
    input_gitlab = gitlab.Gitlab(options.input_gitlab, private_token=options.input_token)
    input_gitlab.auth()
    print(f' - GitLab input: {input_gitlab.api_url}', flush=True)

    # Output login
    output_gitlab = gitlab.Gitlab(options.output_gitlab,
                                  private_token=options.output_token)
    output_gitlab.auth()
    print(f' - GitLab output: {output_gitlab.api_url}', flush=True)

    # Input project
    input_project = input_gitlab.projects.get(options.input_project)
    print(f' - Project input: {input_project.name}', flush=True)

    # Output project
    output_project = output_gitlab.projects.get(options.output_project)
    print(f' - Project output: {output_project.name}', flush=True)

    # Output users
    output_users = output_project.users.list(all=True)
    print(f' - Users output: {len(output_users)}', flush=True)

    # Input milestones
    input_milestones = input_project.milestones.list(all=True)
    for milestone in input_milestones:
        milestones_new += [milestone_parser(milestone)]
    print(f' - Milestones input: {len(input_milestones)}', flush=True)

    # Output milestones
    output_milestones = output_project.milestones.list(all=True)
    for output_milestone in output_milestones:
        milestone_data = milestone_parser(output_milestone)
        milestone_new = None
        for milestone in milestones_new:
            if output_milestone.title == milestone['title']:
                milestone_new = milestone
                break
        if milestone_new:
            milestones_new.remove(milestone_new)
            if milestone_new != milestone_data:
                milestones_updates += [milestone_new]
        else:
            milestones_remove += [milestone_data]
    print(f' - Milestones output: {len(output_milestones)}', flush=True)

    # Milestones removal
    for milestone in milestones_remove:
        print(f' - Milestone removal: {milestone["title"]}', flush=True)
        output_project.milestones.list(search=milestone['title'])[0].delete()

    # Milestones creation
    for milestone in milestones_new:
        print(f' - Milestone creation: {milestone["title"]}', flush=True)
        milestone_new = output_project.milestones.create(milestone)
        milestone_new.state_event = 'close' if milestone[
            'state'] == 'closed' else 'activate'
        milestone_new.save()

    # Milestones updates
    for milestone in milestones_updates:
        print(f' - Milestone updates: {milestone["title"]}', flush=True)
        milestone_old = output_project.milestones.list(search=milestone['title'])[0]
        milestone_updater(milestone_old, milestone).save()

    # Input labels
    input_labels = input_project.labels.list(all=True)
    for label in input_labels:
        labels_new += [label_parser(label)]
    print(f' - Labels input: {len(input_labels)}', flush=True)

    # Output labels
    output_labels = output_project.labels.list(all=True)
    for output_label in output_labels:
        label_data = label_parser(output_label)
        label_new = None
        for label in labels_new:
            if output_label.name == label['name']:
                label_new = label
                break
        if label_new:
            labels_new.remove(label_new)
            if label_new != label_data:
                labels_updates += [label_new]
        else:
            labels_remove += [label_data]
    print(f' - Labels output: {len(output_labels)}', flush=True)

    # Labels removal
    for label in labels_remove:
        print(f' - Label removal: {label["name"]}', flush=True)
        for label_old in output_project.labels.list():
            if label_old.name == label['name']:
                label_old.delete()

    # Labels creation
    for label in labels_new:
        try:
            print(f' - Label creation: {label["name"]}', flush=True)
            label_new = output_project.labels.create(label)
        except gitlab.exceptions.GitlabCreateError:
            print('   Label creation: Failed and skipped (may already exist)')

    # Labels updates
    for label in labels_updates:
        print(f' - Label updates: {label["name"]}', flush=True)
        label_old = output_project.labels.list(search=label['name'])[0]
        label_updater(label_old, label).save()

    # Input issues
    input_issues = input_project.issues.list(all=True)
    for input_issue in input_issues:
        issues_new += [issue_parser(input_issue, output_milestones, output_users)]
    print(f' - Issues input: {len(input_issues)}', flush=True)

    # Output issues
    output_issues = output_project.issues.list(all=True)
    for output_issue in output_issues:
        issue_data = issue_parser(output_issue, output_milestones, output_users)
        issue_new = None
        for issue in issues_new:
            if output_issue.iid == issue['iid']:
                issue_new = issue
                break
        if issue_new:
            issues_new.remove(issue_new)
            if issue_new != issue_data:
                issues_updates += [issue_new]
        else:
            issues_remove += [issue_data]
    print(f' - Issues output: {len(output_issues)}', flush=True)

    # Issues removal
    for issue in issues_remove:
        print(f' - Issue removal: [{issue["iid"]}] {issue["title"]}', flush=True)
        output_project.issues.delete(issue['iid'])

    # Issues creation
    for issue in issues_new:
        print(f' - Issue creation: [{issue["iid"]}] {issue["title"]}', flush=True)
        issue_new = output_project.issues.create(issue)
        issue_new.state_event = 'close' if issue['state'] == 'closed' else 'reopen'
        issue_new.save()

    # Issues updates
    for issue in issues_updates:
        print(f' - Issue updates: [{issue["iid"]}] {issue["title"]}', flush=True)
        issue_old = output_project.issues.get(issue['iid'])
        issue_updater(issue_old, issue).save()

    # Footer
    print('', flush=True)

    # Result
    sys.exit(0)

# Entrypoint
if __name__ == '__main__':
    main()
