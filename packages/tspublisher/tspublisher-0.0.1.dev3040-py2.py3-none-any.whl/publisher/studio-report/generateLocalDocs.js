#!/usr/bin/env node

'use strict';

const { readdirSync } = require('fs');
const { contentProceduresPath } = require('./src/const');
const cp = require('child_process');

const getDirectories = (source) =>
  readdirSync(source, { withFileTypes: true })
    .filter((dirent) => dirent.isDirectory())
    .map((dirent) => dirent.name);

const procedures = getDirectories(contentProceduresPath);

procedures.forEach((procedure) => {
  cp.exec(
    `yarn studio-report --procedure=${procedure} --dev --log`,
    (error, stdout, stderr) => {
      if (error) {
        console.log(`${procedure} error: ${error.message}`);
        return;
      }
      if (stderr) {
        console.log(`${procedure} stderr: ${stderr}`);
        return;
      }
      console.log(`${procedure} stdout: ${stdout}`);
    }
  );
});
