from aurori.jobs.job import Job
from datetime import datetime


class CreateTicketJob(Job):

    description = "Creates a ticket in OpenProject"

    def defineArguments(self):
        self.addStringArgument(
            'project',
            label="Project",
            description="Name of OpenProject project to add to")
        self.addStringArgument('subject',
                               label="Subject",
                               description="Subject of the ticket (aka title)")
        self.addStringArgument('object',
                               label="Object",
                               description="Object to return the result to")

    def run(self, **kwargs):
        print('\n Running ticket job')
