const fs = require('fs-extra');
const sharp = require('sharp');
const { missingFile, contentProceduresPath } = require('../const');

const resizer = (data) =>
  sharp(data)
    .metadata()
    .then(({ width }) =>
      sharp(data)
        .resize(Math.round(width * 0.5))
        .toBuffer()
    );

const bufferToBase64 = (ext) => (buffer) =>
  `data:image/${ext};base64,${buffer.toString('base64')}`;

const readImageToBase64 = async (path) =>
  fs
    .readFile(`${path}.jpg`)
    .then(resizer)
    .then(bufferToBase64('jpg'))
    .catch(() => {
      return fs
        .readFile(`${path}.png`)
        .then(resizer)
        .then(bufferToBase64('png'))
        .catch(() => {
          return fs
            .readFile(`${path}.jpeg`)
            .then(resizer)
            .then(bufferToBase64('jpeg'))
            .catch(() => {
              // if a file does not exist, fall back to the placeholder image
              bufferToBase64('png')(missingFile);
            });
        });
    });

// Asynchronously and recursively iterate an object and resolve any images as base64
const resolveAllImagesAsBase64 = async (
  obj,
  procedureName,
  isExtractMode = false,
  folderName = ''
) => {
  const phaseName = folderName || (obj.folder_name ? obj.folder_name : '');
  const imagePath = `${contentProceduresPath}/${procedureName}${
    phaseName && `/${phaseName}`
  }/assets/`;
  const videoFirstFramePath = `/tmp/studio-review-doc/${procedureName}/${
    phaseName && `${phaseName}/`
  }`;

  if (Array.isArray(obj)) {
    if (!Array.length) {
      return Promise.resolve([]);
    }
    return obj.reduce(async (acc, val) => {
      if (typeof val === 'string' || typeof val === 'number') {
        const accumulator = await acc;
        return Promise.resolve(accumulator.concat(val));
      } else if (val.image && val.image.name) {
        const accumulator = await acc;
        const img = await readImageToBase64(`${imagePath}${val.image.name}`);
        return Promise.resolve(
          accumulator.concat({ ...val, image: { ...val.image, img_src: img } })
        );
      } else if (val.video && val.video.name) {
        const accumulator = await acc;
        const videoFirstFrameImage = await readImageToBase64(
          `${videoFirstFramePath}${val.video.name}`
        );
        return Promise.resolve(
          accumulator.concat({
            ...val,
            video: {
              ...val.video,
              first_frame_src: videoFirstFrameImage,
              video_path: `./procedure_assets/${phaseName}/assets/${val.video.name}.mp4`,
            },
          })
        );
      } else if (typeof val === 'object' && val) {
        const accumulator = await acc;
        const rest = await resolveAllImagesAsBase64(
          val,
          procedureName,
          isExtractMode,
          phaseName
        );
        return Promise.resolve(accumulator.concat(rest));
      } else {
        return Promise.resolve(acc);
      }
    }, Promise.resolve([]));
  } else if (typeof obj === 'object' && obj) {
    const keys = Object.keys(obj);
    return keys.reduce(async (acc, key) => {
      if (key === 'image' && obj[key].name) {
        const accumulator = await acc;
        const img = await readImageToBase64(`${imagePath}${obj[key].name}`);
        return Promise.resolve({
          ...accumulator,
          image: { ...obj[key], img_src: img },
        });
      } else if (key === 'video' && obj[key].name) {
        const accumulator = await acc;
        const videoFirstFrameImage = await readImageToBase64(
          `${videoFirstFramePath}${obj[key].name}`
        );
        return Promise.resolve({
          ...accumulator,
          video: {
            ...obj[key],
            first_frame_src: videoFirstFrameImage,
            video_path: `./procedure_assets/${phaseName}/assets/${val.video.name}.mp4`,
          },
        });
      } else if (typeof obj[key] === 'string' || typeof obj[key] === 'number') {
        const accumulator = await acc;
        return Promise.resolve({ ...accumulator, [key]: obj[key] });
      } else if (typeof obj[key] === 'object' && obj[key]) {
        const accumulator = await acc;
        const rest = await resolveAllImagesAsBase64(
          obj[key],
          procedureName,
          isExtractMode,
          phaseName
        );
        return Promise.resolve({ ...accumulator, [key]: rest });
      } else if (Array.isArray(obj[key]) && !obj[key].length) {
        const accumulator = await acc;
        return Promise.resolve({ ...accumulator, [key]: [] });
      } else {
        return Promise.resolve(acc);
      }
    }, Promise.resolve({}));
  }
};

module.exports = resolveAllImagesAsBase64;
