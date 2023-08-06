const extract = require('extract-zip');
const { LokaliseApi } = require('@lokalise/node-api');
const fetch = require('node-fetch');
const fs = require('fs-extra');
const { 
  translationsPath,
  unzippedTranslations,
  downloadedTranslationsZipFile,
} = require('../const');

const mkdirIfNotExists = (path) => {
  if (!fs.existsSync(path)) {
    fs.mkdirSync(path, { recursive: true });
  }
};

const extractDownloadedLocale = (language) => {
  mkdirIfNotExists(unzippedTranslations);
  return extract(downloadedTranslationsZipFile, { dir: unzippedTranslations })
    .then(() => {
      console.log('Translations downloaded & unzipped');
      console.log(unzippedTranslations + '/locale/' + language + '.json');
      try {
        const fileContents = fs.readFileSync(unzippedTranslations + '/locale/' + language + '.json');
        const translations = JSON.parse(fileContents);
        console.log("Parsed translations");
        return translations
      } catch(error) { 
        console.log("Failed to parse JSON");
        console.log(error);
        return {}
      }
    })
    .catch((error) => {
      console.log("Failed to extract JSON");
      console.log(error);
    });
};

const getLocalisation = async (language = 'en') => {
  if (language == 'en') {
    return Promise.resolve({});
  }
  const lokaliseProjectID = '6096066960dd7dd2ceb166.93212597';
  const lokaliseApi = new LokaliseApi({ apiKey: process.env.LOKALISE_TOKEN });
  console.log(`Finding Lokalise language ID...`);
  const project = await lokaliseApi.projects
    .get(lokaliseProjectID)
    .catch(console.log);
  const lokaliseLanguage = project.statistics.languages.find(
    (incomingLanguage) => {
      return incomingLanguage.language_iso === language;
    }
  );
  if (!lokaliseLanguage) {
    const availableLanguages = project.statistics.languages.map(
      (lokaliseLanguage) => {
        return lokaliseLanguage.language_iso;
      }
    );
    console.log(
      `Cannot find language ID ${language} in ${availableLanguages}`
    );
  }
  const translationFilesURL = await lokaliseApi.files
    .download(lokaliseProjectID, {
      format: 'json',
      filter_data: ['reviewed'],
      disable_references: true,
      original_filenames: false,
    })
    .catch((error) => {
      console.log(`Error creating Lokalise files`, error);
    });
  const translations = await fetch(translationFilesURL.bundle_url, {
    headers: {
      Connection: 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      Accept: '*/*',
      'Accept-Encoding': 'gzip, deflate, br',
    },
  });
  mkdirIfNotExists(translationsPath);
  return new Promise((resolve) => {
    const writer = fs.createWriteStream(downloadedTranslationsZipFile);
    translations.body.pipe(writer);
    writer.on('error', (err) => {
      writer.close();
      console.log(err);
      resolve();
    });
    writer.on('close', async () => {
      console.log(`Translations saved at: ${downloadedTranslationsZipFile}`);
      const parsedTranslations = await extractDownloadedLocale(language);
      resolve(parsedTranslations);
    });
  });
};

const curriedTranslate = (translations, validate_translations) => (key) => {
  if (!translations) {
    if (!curriedTranslate.errorDisplayed) {
      curriedTranslate.errorDisplayed = true;
      console.log("Translations not loaded");
    }
    return key
  }
  if (key  == null) { return; }
  var value = translations[key];
  if (value == null && key != "") {
    if (typeof key === 'object' && validate_translations) {
      console.log("Object passed for translation");
      console.log(JSON.stringify(key));
    } else {
      const fixedKey = JSON.stringify(key).replace(/^"/, "").replace(/"$/,"");
      value = translations[fixedKey];
      if (value == null && validate_translations) {
        console.log(`Translation missing for key: ${fixedKey}`);
      }
    }
  }
  return value || key;
}

module.exports = {
  curriedTranslate,
  getLocalisation,
};