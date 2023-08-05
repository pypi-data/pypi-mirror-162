#!/usr/bin/env node

'use strict';

const constants = require('./const');
const path = require('path');
const fs = require('fs');
const { generateReviewDocument } = require('./payloadGenerator');
const resolveAllImagesAsBase64 = require('./utilities/image');
const resolveVideoFrames = require('./utilities/video');
const {
  generateYAMLJSON,
  copyProcedureAssets,
  downloadDocument,
  writeJSON,
  error,
  printHelp,
} = require('./utilities/io');
const {
  curriedTranslate,
  getLocalisation,
} = require('./utilities/translations');

const args = require('minimist')(process.argv.slice(2), {
  boolean: ['help', 'dev', 'log', 'extract', 'validate_translations'],
  string: ['procedure', 'endpoint', 'output', 'input_json', 'language'],
});

const main = async () => {
  const translate = curriedTranslate(await getLocalisation(args.language || 'en'), args.validate_translations);
  console.log(`Resolving assets...`);
  // check if there is input json and try to resolve it
  // if exist continue processing but skip generating and processing images/json
  let procedureWithImages;
  if (args.input_json && fs.existsSync(args.input_json)) {
    procedureWithImages = JSON.parse(fs.readFileSync(args.input_json));
  } else if (args.procedure) {
    const procedure = generateYAMLJSON(args.procedure);
    resolveVideoFrames(procedure, procedure.procedure_name);
    procedureWithImages = await resolveAllImagesAsBase64(
      procedure,
      procedure.procedure_name,
      args.extract
    );
  } else {
    error(`File at: ${args.input_json} cannot be resolved.`, true);
  }
  return Promise.all([procedureWithImages]).then(([procedureWithImgs]) => {
    args.log &&
      console.log(
        `Writing ${constants.devLogOutputPath}/${procedureWithImgs.procedure_name}.json...`
      );
    args.log &&
      writeJSON(
        `${constants.devLogOutputPath}/${procedureWithImgs.procedure_name}.json`,
        procedureWithImgs
      );
    console.log(`Generating payload...`);
    const payload = generateReviewDocument(
      procedureWithImgs,
      constants,
      args.extract,
      translate
    );
    args.log &&
      console.log(
        `Writing ${constants.devLogOutputPath}/${procedureWithImgs.procedure_name}_payload.json...`
      );
    args.log &&
      writeJSON(
        `${constants.devLogOutputPath}/${procedureWithImgs.procedure_name}_payload.json`,
        payload
      );
    if (args.endpoint || args.dev) {
      const format = args.extract ? 'html' : 'pdf';
      const procedureName = args.extract ? args.procedure : '';
      const creationDate = (new Date()).toISOString().split('T')[0];
      const sha = require('child_process').execSync(`git -C ${constants.contentProceduresPath} rev-parse --short HEAD`).toString().trim();
      const filename = `${procedureName}${procedureWithImgs.procedure_name}-${sha}-${creationDate}.${format}`;
      const outputPath = args.output
        ? `${args.output}/${filename}`
        : `${constants.defaultPdfOutputPath}/${filename}`;
      if (args.extract) {
        const outputFolder = `${path.dirname(outputPath)}/procedure_assets`;
        console.log(`Copying procedure assets to: ${outputFolder}`);
        copyProcedureAssets(args.procedure, outputFolder);
      }
      if (args.endpoint) {
        console.log(`Posting payload to: ${args.endpoint}`);
        downloadDocument(JSON.stringify([payload]), args.endpoint, outputPath);
      }
      if (args.dev) {
        console.log(
          `Posting payload to local server at: ${constants.DEV_ENDPOINT}`
        );
        downloadDocument(
          JSON.stringify([payload]),
          constants.DEV_ENDPOINT,
          outputPath
        );
      }
    }
  });
};

if (args.help) {
  printHelp(true);
}

if (!args.procedure && !args.endpoint && !args.input_json) {
  error(
    'Incorrect usage. Procedure name, input data or endpoint must be provided.',
    true
  );
}

main();
