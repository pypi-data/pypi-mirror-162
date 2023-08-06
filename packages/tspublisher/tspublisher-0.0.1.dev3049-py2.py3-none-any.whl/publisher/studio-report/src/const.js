const fs = require('fs-extra');
const homedir = require('os').homedir();

const introInternalWarning = 'CONFIDENTIAL – For internal use only. Do not copy or distribute.'

const introTopCopy = (title) =>
  `This document contains the graphic and written content of the ${title} simulation on the Touch Surgery™ mobile application. The simulation displays key surgical concepts and procedural steps for healthcare professionals(HCP).The content is presented in four sections:`;

const introList = [
  'Overview of background information',
  'Key Instruments',
  'Instructional Learn Mode',
  'Test Mode to assess knowledge acquisition',
];

const introRightSectionCopyList = [
  'The contents of this report differ slightly from how they are displayed in the app. An example is shown here. The written content that accompanies the visual segments is displayed at the bottom of the screen when viewed in the app.In this report, the text is presented beside the image.',
  'Interactive widgets are featured throughout the simulation. Some examples are draggers, galleries, picture -in - picture, info points, and labels.',
  '<strong>Draggers</strong> simulate actions that the user must perform in a procedure.Draggers are shown with a green circle at their initial location, and a white circle at their target location.Dragging to the target progresses the simulation to the next step.',
  '<strong>Galleries of images</strong> appear over the main image of a step.Each gallery image may be accompanied by text.In this report, these images and text are included after the main step image.',
  '<strong>Picture-in-picture</strong> widgets are additional images overlaid on the main step image.Some can be minimized.In this report, picture -in -picture widgets follow the main step image.',
  '<strong>Labels</strong> indicate items of interest in the image.They consist of text and a line to the item.In this report, labels are shown on the main step image, and are also repeated alongside the image.',
  '<strong>Info points</strong> are similar to labels, but without the line, and do not show text unless the user interacts with them.In this report, they are listed A, B, C, etc., and the text follows the main text of the step.',
  '<strong>The flipbook</strong> widget allows the user to scrub through a video one frame at a time, showing them actions they are supposed to take, or their effects, in detail. In this report the first frame of the flipbook video will be shown following the step image, but the flipbook will be entirely overlaid on top of the main step image in the app.',
];

const introBottomCopy =
  'Touch Surgery™ from Medtronic is a medical education mobile application. The app acts as a cognitive task trainer, featuring a library of simulations created by our team in collaboration with key opinion leaders. Our simulations combine interactive visual materials with informative text to deliver surgical education.';

const TSLOGO = {
  type: 'ts_logo_mdt_white',
};

const DEV_ENDPOINT = 'http://localhost:8080/pdf-templating/new';
const contentProceduresPath = `${homedir}/git/content-procedures`;
const tempFolderPath = '/tmp/studio-review-doc/';
const translationsPath = `/tmp/studio_review_doc/translations`;
const downloadedTranslationsZipFile = translationsPath + '/download.zip';
const unzippedTranslations = translationsPath + '/latest';
const missingFile = fs.readFileSync(
  `${__dirname}/assets/missing_file_base64.txt`,
  {
    encoding: 'base64',
  }
);
const defaultPdfOutputPath = `${homedir}/Desktop/studio-reports`;
const devLogOutputPath = `${homedir}/Desktop/studio-reports/logs`;

const outputFormats = {
  HTML: 'html',
  PDF: 'pdf',
};

module.exports = {
  introInternalWarning,
  introTopCopy,
  introBottomCopy,
  introList,
  introRightSectionCopyList,
  TSLOGO,
  DEV_ENDPOINT,
  contentProceduresPath,
  tempFolderPath,
  missingFile,
  defaultPdfOutputPath,
  devLogOutputPath,
  outputFormats,
  translationsPath,
  downloadedTranslationsZipFile,
  unzippedTranslations,
};
