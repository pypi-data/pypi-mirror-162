const ffmpeg = require('fluent-ffmpeg');
const fs = require('fs');
const chalk = require('chalk');
const { contentProceduresPath, tempFolderPath } = require('../const');
const R = require('ramda');

const makeScreenshots = (filePath, outputPath) => {
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
  }
  ffmpeg(filePath).screenshot({
    folder: outputPath,
    filename: '%b.png',
    timemarks: [0],
  });
};

const resolveVideoFrames = (obj, procedureName, folderName = '') => {
  const phaseName =
    folderName || (!R.isNil(obj) && obj.folder_name ? obj.folder_name : '');
  const videoPath = `${contentProceduresPath}/${procedureName}${
    phaseName && `/${phaseName}`
  }/assets/`;
  const imageOutputPath = `${tempFolderPath}${procedureName}/${
    phaseName && `${phaseName}/`
  }`;

  if (Array.isArray(obj)) {
    return obj.forEach((elem) =>
      resolveVideoFrames(elem, procedureName, phaseName)
    );
  } else if (typeof obj === 'object' && obj && !R.isNil(obj)) {
    const keys = Object.keys(obj);
    if (obj.video && obj.video.name) {
      const filePath = videoPath + obj.video.name + '.mp4';
      fs.access(filePath, fs.F_OK, (err) => {
        if (err) {
          console.log(
            chalk`{inverse.yellow [WARNING]} {yellow Missing file: ${filePath}} \n`
          );
        } else {
          makeScreenshots(filePath, imageOutputPath);
        }
      });
    }
    return keys.forEach((key) =>
      resolveVideoFrames(obj[key], procedureName, phaseName)
    );
  }
};

module.exports = resolveVideoFrames;
