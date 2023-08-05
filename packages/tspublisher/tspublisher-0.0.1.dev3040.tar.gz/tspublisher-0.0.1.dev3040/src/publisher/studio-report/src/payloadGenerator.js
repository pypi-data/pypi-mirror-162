const { head, path, flatten } = require('ramda');
const {
  tableOfContents,
  article,
  pill,
  phaseStepCard,
  banner,
  makeDocumentTitle,
  documentConfig,
  intro,
  divider,
  componentTypes,
  pageBreak,
} = require('./components');
const constants = require('./const');
const { getSha } = require('./utilities/io')

// HELPERS
const makeLink = ({ name, mode = '', anchor = '' }) =>
  `${anchor && '#'}${name.replace(/\s+/g, '_')}_${mode}`;
const simpleTraverse = (obj, callback) => {
  for (let key in obj) {
    callback.apply(this, [key, obj[key]]);
    if (obj[key] !== null && typeof obj[key] === 'object') {
      simpleTraverse(obj[key], callback);
    }
  }
};

const getRevisionDate = () => {
  const d = Date.now();
  const ye = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(d);
  const mo = new Intl.DateTimeFormat('en', { month: 'long' }).format(d);
  const da = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(d);
  const ti = new Date().toLocaleTimeString().slice(0, -3);
  return `${ti}   ${mo} ${da}, ${ye}`;
};
// -------

const processInfoCards = (sections, title, withTitle, translate) => {
  if (!Array.isArray(sections) || !sections.length) {
    return [];
  } else {
    return sections
      .filter((section) => section.body && section.body.length)
      .map((section, sectionIndex) => {
        return section.body
          .map((body, bodyIndex) => {
            const type = head(Object.keys(body));
            // Title translated at call site
            const articleTitle = withTitle && bodyIndex === 0 && sectionIndex === 0 ? title : '';
            const subtitle = translate(bodyIndex === 0 ? section.title : '');
            const link = makeLink({ name: title || subtitle });
            switch (type) {
              case componentTypes.GALLERY: {
                const base64Gallery = body.gallery
                  .filter(
                    (galleryItem) => galleryItem.image || galleryItem.video
                  )
                  .map((galleryItem) => {
                    if (galleryItem.image) {
                      return { src: galleryItem.image.img_src };
                    } else if (galleryItem.video) {
                      return { src: galleryItem.video.first_frame_src };
                    }
                  });
                return article({
                  gallery: base64Gallery,
                  title: articleTitle,
                  subtitle: subtitle,
                  font_colors: { text: '#26c6da' },
                  link,
                });
              }
              case componentTypes.TEXT: {
                return article({
                  title: articleTitle,
                  subtitle: subtitle,
                  text: translate(body.text),
                  link,
                });
              }
              case componentTypes.NUMBERED_LIST:
              case componentTypes.LIST: {
                return article({
                  title: articleTitle,
                  subtitle: subtitle,
                  list:
                    (body.list ||
                    body.numbered_list || 
                    []).map(translate),
                  list_type: body.numbered_list ? '1' : '',
                  link,
                });
              }
              case componentTypes.AUTHOR: {
                if (path(['author', 'image', 'name'], body)) {
                  return [
                    article({
                      title: articleTitle,
                      subtitle: subtitle,
                      text: translate(body.author.name),
                      gallery: [{ src: body.author.image.img_src }],
                    }),
                    article({
                      text: translate(body.author.desc),
                    }),
                  ];
                } else {
                  return article({
                    title: articleTitle,
                    text: translate(body.author.name),
                    subtitle: subtitle,
                  });
                }
              }
              default:
                return null;
            }
          })
          .filter(Boolean);
      });
  }
};

const generateSection = (infoCardList, withTitle, translate) =>
  infoCardList.map(({ information_card: { sections, title } }) =>
    processInfoCards(sections, translate(title), withTitle, translate)
  );

const generatePhaseStepCards = (
  objectives,
  isLearnMode,
  phaseInfo,
  isExtractMode,
  header,
  translate
) => {
  let currentPhaseStepNumber = 0;

  const totalSteps = objectives.reduce(
    (acc, objective) => acc + objective.steps.length,
    0
  );
  return flatten(
    objectives.map((objective) => {
      return objective.steps.map((step) => {
        let videoPaths = [];
        simpleTraverse(step, (key, value) => {
          if (key === 'video_path' && isExtractMode) {
            videoPaths.push(value);
          }
        });
        currentPhaseStepNumber++;
        const labelsList = step.widgets.reduce(
          (acc, { label }) =>
            label && label.text_anchor_x ? acc.concat(label.content) : acc,
          []
        );
        const infoPoints = step.widgets.reduce(
          (acc, { label }) =>
            label && !label.text_anchor_x ? acc.concat(label.content) : acc,
          []
        );
        const taps = step.widgets.reduce(
          (acc, { tap }) => (tap ? acc.concat(tap) : acc),
          []
        );
        const pips = step.widgets
          .reduce((acc, { pip }) => (pip ? acc.concat(pip) : acc), [])
          .map(({ code, position, assets }) => ({
            code,
            position,
            img:
              assets[0].image && assets[0].image.img_src
                ? assets[0].image.img_src
                : assets[0].video.first_frame_src,
          }));
        const draggerABs = step.widgets.reduce(
          (acc, { dragger_ab }) => (dragger_ab ? acc.concat(dragger_ab) : acc),
          []
        );
        const draggerDirectionals = step.widgets.reduce(
          (acc, { dragger_directional }) =>
            dragger_directional ? acc.concat(dragger_directional) : acc,
          []
        );
        const labelsData = step.widgets.filter(
          (widget) => widget.label && widget.label.text_anchor_x
        );
        const infoPointsData = step.widgets.filter(
          (widget) => widget.label && widget.label.text_anchor_x == null
        );
        let bottomContent = [];
        const content = step.widgets
          .map((widget) => {
            if (widget.text) {
              if (widget.text.information_cards) {
                const infoCards = widget.text.information_cards.map(
                  ({ information_card: { sections, title } }) =>
                    processInfoCards(sections, translate(title), true, translate)
                );
                bottomContent = bottomContent
                  .concat(
                    pill({
                      text: 'Additional information',
                      background_color: '#ededed',
                      font_colors: { text: '#4e4e4e' },
                    })
                  )
                  .concat(flatten(infoCards));
              }
              return article({
                title: 'text',
                text: translate(widget.text.content),
              });
            }
            if (widget.mcq) {
              return [
                article({
                  title: 'Question',
                  text: translate(widget.mcq.content),
                }),
                article({
                  title: 'Options',
                  list: widget.mcq.choices
                    .concat(widget.mcq.answer)
                    .map(translate),
                }),
                article({
                  title: 'Correct answer',
                  text: translate(widget.mcq.answer),
                }),
              ];
            }
            if (widget.gallery) {
              const galleryImages = widget.gallery.items
                .map((galleryItem) => {
                  if (galleryItem.image && galleryItem.image.img_src) {
                    return article({
                      subtitle: translate(galleryItem.title),
                      text: translate(galleryItem.text),
                      gallery: [
                        { src: galleryItem.image.img_src, size: 'large' },
                      ],
                    });
                  } else if (
                    galleryItem.video &&
                    galleryItem.video.first_frame_src
                  ) {
                    return article({
                      subtitle: translate(galleryItem.title),
                      text: translate(galleryItem.text),
                      gallery: [
                        {
                          src: galleryItem.video.first_frame_src,
                          size: 'large',
                        },
                      ],
                    });
                  } else {
                    return null;
                  }
                })
                .filter(Boolean);
              bottomContent = bottomContent
                .concat(article({ title: 'Gallery' }))
                .concat(flatten(galleryImages));
              return null;
            }
            if (widget.flip_book) {
              if (widget.flip_book.assets && widget.flip_book.assets.length) {
                const images = widget.flip_book.assets.filter(
                  (item) => item.image && item.image.img_src
                );
                const videos = widget.flip_book.assets.filter(
                  (item) => item.video && item.video.first_frame_src
                );
                if (images.length) {
                  bottomContent = bottomContent.concat([
                    article({ subtitle: 'Flipbook: First frame' }),
                    article({
                      gallery: [
                        { src: head(images).image.img_src, size: 'largest' },
                      ],
                    }),
                  ]);
                } else if (videos.length) {
                  bottomContent = bottomContent.concat([
                    article({ subtitle: 'Flipbook: First frame' }),
                    article({
                      gallery: [
                        {
                          src: head(videos).video.first_frame_src,
                          size: 'largest',
                        },
                      ],
                    }),
                  ]);
                }
              }
              return null;
            }
          })
          .filter(Boolean);

        const flattenedContents = flatten(content).filter(Boolean);
        const sideContentWithLabels = !labelsList.length
          ? flattenedContents
          : flattenedContents.concat(
              article({
                title: 'Labels',
                list: labelsList.map(translate),
                list_type: 'A',
              })
            );
        const contentWithInfoPointsAndLabels = !infoPoints.length
          ? sideContentWithLabels
          : sideContentWithLabels.concat(
              article({
                title: 'Information points',
                list: infoPoints.map(translate),
                list_type: 'a',
              })
            );

        const hasAdditionalInfoText = Boolean(
          bottomContent.filter(
            (component) =>
              component && component.title === 'Additional information'
          ).length
        );
        const labelsInfoCardsInitialValue = hasAdditionalInfoText
          ? null
          : pill({
              text: 'Additional information',
              background_color: '#ededed',
              font_colors: { text: '#4e4e4e' },
            });
        const extractInfoCards = (acc, hasInfoCard, index, charOffset) => {
          if (
            hasInfoCard.information_cards &&
            hasInfoCard.information_cards.length
          ) {
            const infoCards = hasInfoCard.information_cards.reduce(
              (acc, infoCard) => {
                if (
                  infoCard.information_card &&
                  infoCard.information_card.sections
                ) {
                  // This is a title prepended with a letter, starting from "a" or "A"
                  const orderedTitle = `${String.fromCharCode(
                    charOffset + index
                  )}. ${translate(infoCard.information_card.title)}`;
                  return flatten(
                    acc.concat(
                      processInfoCards(
                        infoCard.information_card.sections,
                        orderedTitle,
                        true,
                        translate
                      )
                    )
                  );
                } else {
                  return acc;
                }
              },
              []
            );
            return acc.concat(infoCards);
          } else {
            return acc;
          }
        };
        const infoPointsInfoCards = infoPointsData.reduce(
          (acc, { label }, index) => extractInfoCards(acc, label, index, 97),
          []
        );
        const labelsInfoCards = labelsData.reduce(
          (acc, { label }, index) => extractInfoCards(acc, label, index, 65),
          []
        );
        let allInfoCards = [labelsInfoCardsInitialValue];
        if (labelsInfoCards && labelsInfoCards.length) {
          allInfoCards = allInfoCards.concat(labelsInfoCards);
        }
        if (infoPointsInfoCards && infoPointsInfoCards.length) {
          allInfoCards = allInfoCards.concat(infoPointsInfoCards);
        }
        // assemble final content for the bottom part of phase cards
        const composedBottomContent =
          allInfoCards.length > 1
            ? flatten(bottomContent.concat(allInfoCards)).filter(Boolean)
            : bottomContent.filter(Boolean);
        const videoList = videoPaths.length
          ? article({
              title: 'Videos in this step',
              list: videoPaths.map(
                (path, i) =>
                  `<a href="file:${path}" target="_blank" rel="noopener noreferrer">${path}</a>`
              ),
            })
          : [];
        if (step.assets) {
          const stepImage = step.assets
            .map((asset) => (asset.image ? asset.image.img_src : null))
            .filter(Boolean);
          return phaseStepCard({
            title: phaseInfo,
            header: currentPhaseStepNumber === 1 ? header : null,
            pill: pill({
              text: `Step ${currentPhaseStepNumber} of ${totalSteps}`,
              background_color: isLearnMode ? '#5f78be' : '#DB6174',
            }),
            dragger_ab: draggerABs,
            dragger_directional: draggerDirectionals,
            labels: labelsData,
            info_points: infoPointsData,
            tap: taps,
            objective: translate(objective.name),
            imageSrc: head(stepImage),
            content: flatten(contentWithInfoPointsAndLabels.concat(videoList)),
            picture_in_picture: pips,
            bottom_content: composedBottomContent,
          });
        } else {
          return phaseStepCard({
            title: translate(phaseInfo),
            tap: taps,
            header: currentPhaseStepNumber === 1 ? header : null,
            pill: pill({
              text: `Step ${currentPhaseStepNumber} of ${totalSteps}`,
              background_color: isLearnMode ? '#5f78be' : '#DB6174',
            }),
            labels: labelsData,
            info_points: infoPointsData,
            dragger_ab: draggerABs,
            dragger_directional: draggerDirectionals,
            objective: objective.name,
            imageSrc: '',
            content: flatten(contentWithInfoPointsAndLabels.concat(videoList)),
            picture_in_picture: pips,
            bottom_content: composedBottomContent,
          });
        }
      });
    })
  );
};

const generatePhaseSection = (phasesArray, isExtractMode, translate) => {
  return phasesArray.map((phase, phaseNumber) => {
    const learnHeader = pill({
      text: `Phase ${phaseNumber + 1} - ${translate(phase.name)}`,
      mode: 'Learn mode',
      width: '100%',
      background_color: '#5f78be',
      link: makeLink({ name: phase.name, mode: 'Learn' }),
    });
    const testHeader = pill({
      text: `Phase ${phaseNumber + 1} - ${translate(phase.name)}`,
      mode: 'Test mode',
      width: '100%',
      background_color: '#DB6174',
      link: makeLink({ name: phase.name, mode: 'Test' }),
    });
    const phaseInfo = `Phase ${phaseNumber + 1} - ${translate(phase.name)}`;
    const learnSteps = phase.objectives
      ? generatePhaseStepCards(
          phase.objectives,
          true,
          phaseInfo,
          isExtractMode,
          learnHeader,
          translate
        )
      : [];
    // remove the steps that do not have mcq (multiple choice questions)
    // or dragger widgets
    const filteredTestObjectives = phase.test_objectives.map((objective) => {
      return {
        ...objective,
        steps: objective.steps.reduce((acc, step) => {
          const hasValidWidgets = step.widgets.every(
            (widget) =>
              widget.mcq || widget.dragger_ab || widget.dragger_directional
          );
          if (hasValidWidgets) {
            return acc.concat(step);
          }
          return acc;
        }, []),
      };
    });
    const testSteps = filteredTestObjectives
      ? generatePhaseStepCards(
          filteredTestObjectives,
          false,
          phaseInfo,
          isExtractMode,
          testHeader,
          translate
        )
      : [];
    return [...learnSteps, ...testSteps];
  });
};

const generateTableOfContents = (
  overviewList,
  devicesList,
  phasesList,
  translate
) => {
  const sections = [
    {
      title: 'Overview',
      contents: overviewList.map((infoCard) => ({
        text: `${translate(infoCard.information_card.title)}`,
        link: makeLink({ name: infoCard.information_card.title, anchor: true }),
      })),
    },
    {
      title: 'Key instruments',
      contents: flatten(
        devicesList.map((deviceInfoCard) =>
          deviceInfoCard.information_card.sections
            ? deviceInfoCard.information_card.sections
                .map((device) => {
                  if (device.title) {
                    return {
                      text: `${translate(device.title).replace(/\s+/g, ' ')}`,
                      link: makeLink({ name: device.title, anchor: true }),
                    };
                  }
                  return null;
                })
                .filter(Boolean)
            : {
                text: translate(deviceInfoCard.information_card.title),
                link: makeLink({
                  name: deviceInfoCard.information_card.title,
                  anchor: true,
                }),
              }
        )
      ),
    },
    {
      title: 'Phases',
      contents: phasesList.map((phase, i) => ({
        text: `${i + 1}. ${translate(phase.name)}`,
        subsections: [
          {
            text: 'Learn mode',
            link: makeLink({
              name: translate(phase.name),
              mode: 'Learn',
              anchor: true,
            }),
          },
          {
            text: 'Test mode',
            link: makeLink({
              name: translate(phase.name),
              mode: 'Test',
              anchor: true,
            }),
          },
        ],
      })),
    },
  ].filter((section) => section.contents.length);
  return tableOfContents({ sections });
};

const generateReviewDocument = (yamlJson, consts, isExtractMode, translate) => {
  const phaseSection = generatePhaseSection(
    yamlJson.phases,
    isExtractMode,
    translate
  );
  const devicesSection = generateSection(yamlJson.devices, false, translate);
  const overviewSection = generateSection(yamlJson.overview, true, translate);
  const keyInstrumentsSection = devicesSection.length
    ? [
        banner({ title: 'Key instruments', anchor: 'key_instruments' }),
        ...flatten(devicesSection),
      ]
    : null;
  const outputFormat = isExtractMode
    ? constants.outputFormats.HTML
    : constants.outputFormats.PDF;

  const documentMetaDetails = `Version: ${getSha()}   ·   ${getRevisionDate()}`;
  return {
    config: documentConfig(outputFormat),
    sections: [
      [
        makeDocumentTitle(
          translate(yamlJson.name),
          !isExtractMode ? consts.TSLOGO : undefined
        ),
        article({ text: documentMetaDetails }),
        article({ text: constants.introInternalWarning }),
        !isExtractMode &&
          intro({
            topText: consts.introTopCopy(
              translate(yamlJson.name).trim(),
              translate(yamlJson.name).trim()
            ),
            bottomText: consts.introBottomCopy,
            listArray: consts.introList,
            rightContentList: consts.introRightSectionCopyList,
          }),
        divider(),
      ].filter(Boolean),
      [
        pageBreak(),
        banner({ title: 'Table of contents' }),
        article({ text: 'Click to navigate the document.' }),
        generateTableOfContents(
          yamlJson.overview,
          yamlJson.devices,
          yamlJson.phases,
          translate
        ),
      ],
      [
        pageBreak(),
        banner({ title: 'Overview', anchor: 'overview' }),
        ...flatten(overviewSection),
      ],
      [pageBreak()],
      keyInstrumentsSection,
      ...phaseSection,
    ].filter(Boolean),
  };
};

module.exports = { generateReviewDocument };
