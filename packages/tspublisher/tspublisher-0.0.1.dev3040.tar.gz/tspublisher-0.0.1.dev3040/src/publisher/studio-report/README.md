# What is the studio report tool?

This is an automated tool that generates a json file, to be sent to the pdf_templating server (not included) for generating a pdf documents of procedures. It parses the contents of a procedure directory and resolves images, the first frames of videos and it supports embedding HTML tags for styling (\<script> tags are not allowed).

The alternative to this tool is for someone to spend several days assembling a similar document by manually copying and pasting from a CSV of the simulation, and adding screenshots for every step and question in every phase of a procedure.

# How to request a report?

The suggested workflow for Studio when a report is required is to make a request in the Slack channel #project-studio-review-document, specifying the procedure ID and deadline. A team member should then generate the document by following the instructions below.

## Prerequisites

Install TSPublisher according to the [documentation](https://kinosis.atlassian.net/wiki/spaces/VS/pages/391741441/TS+Publisher+Documentation), and the latest version of Studio Procedure HTML Report by running:

`npm install -g https://bitbucket.org/touchsurgery/studio-procedure-html-report/src/master/`

# How to use?

The tool can be used manually or as part of a pipeline. It accepts various CLI configuration options, to define its behaviour. Run the command with the `--help` flag to see all available configuration options. An example for a local development workflow:

- Using as a global package:
  `studio-report --procedure=BD_PiP --dev`

- Running it directly in the cloned repository in `/src` directory:
  `node main.js --procedure=BD_PiP --dev`

The above commands will locate and resolve all assets in `/git/content-procedures/BD_PiP` and post the compiled json payload to `http://localhost:8080/pdf`. The resulting pdf will be saved in the default pdf output path at `~/Desktop/studio-reports/BD_PiP.pdf`

# Steps to start a local pdf generator server:

- clone the Platform repository
- in the `/pdf-templating` directory run `yarn install_dependencies`
- then run `yarn build_and_serve`, which will bundle the client and start the pdf server

# How the studio-report tool works

The script will perform the following steps in order to successfully generate a pdf report:

- Parses `procedure.yml` from the target directory into a JSON object
- Resolves additional `phase.yml` files in all subdirectories as JSON objects, and appends them to the JSON resolved from `procedure.yml`
- Traverses the resulting object and tries to open all videos to extract the first frames as base64 image urls, and then resolves all other images also as base64 image urls
- Iterates over the phases, devices, overview lists to generates components, which then returned as an object that can be consumed by the pdf generator server
- Sends a POST request to the specified ENDPOINT or to a local pdf server
- The pdf received from the server and saved to the specified or default output path

# Hints, tips, cautions

- Make sure that the component definitions are up to date with the schemas defined in `platform/pdf_templating/server/docs/componentSchemas.json`
- The pdf server will check the payload and returns a helpful error if it did not pass validation
- Images are compressed 50% by default, changing the compression can greatly increase or reduce the overall payload size
- Missing video files will not fail the process, but a warning will be displayed
- Missing images will be replaced with a placeholder image
- Using `--log` saves the JSON files generated from the YAML files, as well as the payload that is sent to the service. This may help finding an error.

# Troubleshooting

Generally, if the script fails, it will print out the error that broke it. Most of the errors will arise from:

- change in the yaml structure
- component schemas and component functions are out of sync, thus the server rejects the payload
- if posting to the server fails, rename the retuned pdf to .json and inspect the error message.
