/**
 * The following functions are used to generate an instance of a component, that will be used
 * in the pdf_templating project. Object keys correlate to the keys in
 * platform/pdf_templating/server/docs/componentSchemas.json
 */
const constants = require('./const');

const margins = (
  top = '2rem',
  bottom = '2rem',
  left = '0rem',
  right = '0rem'
) => ({
  margin_top: top,
  margin_bottom: bottom,
  margin_left: left,
  margin_right: right,
});

const documentConfig = (output_format = constants.outputFormats.PDF) => ({
  document_background: '#ffffff',
  section_background: '#ffffff',
  format: 'A4',
  footer: false,
  height_offset: 150,
  output_format,
  is_paginated: true,
  margin: {
    top: '30px',
    right: '0px',
    bottom: '25px',
    left: '0px',
  },
});

const banner = ({
  title,
  icon = undefined,
  reverse = false,
  is_bold = false,
}) => ({
  component_type: 'banner',
  icon,
  title,
  background_color: '#ffffff',
  font_colors: {
    title: '#4e4e4e',
  },
  reverse,
  font_sizes: {
    title: 'xxl',
  },
  margin: margins('0.5rem', '0.5rem'),
  is_bold,
});

const article = ({
  title,
  text,
  gallery,
  list,
  subtitle,
  margin = {},
  link,
  list_type,
  font_colors = {
    title: '#26c6da',
    text: '#4e4e4e',
    list: '#4e4e4e',
    subtitle: '#4e4e4e',
  },
  font_sizes = {
    title: 'l',
    text: 's',
    list: 's',
    subtitle: 's',
  },
}) => ({
  component_type: 'article',
  title,
  subtitle,
  text,
  link,
  margin: margins('1rem', '1rem', margin.margin_left),
  font_colors,
  font_sizes,
  gallery,
  list,
  list_type,
});

const htmlMarkup = ({ markup }) => ({
  component_type: 'html_markup',
  markup,
});

const list = ({ list, is_ordered = true, is_bold_text = true }) => ({
  component_type: "list",
  list,
  font_sizes: {
    text: 's',
  },
  is_ordered,
  is_bold_text,
});

const intro = ({ topText, bottomText, listArray, rightContentList }) => ({
  component_type: 'intro',
  top_content: article({ text: topText }),
  bottom_content: article({ text: bottomText }),
  right_content: rightContentList,
  list: list({ list: listArray }),
  margin: margins(),
});

const divider = () => ({
  component_type: 'divider',
  type: 'line',
  margin: margins('2rem', '3.5rem'),
});

const tableOfContents = ({ sections }) => ({
  component_type: 'table_of_contents',
  margin: margins('2rem', '0', '2rem'),
  font_sizes: {
    text: 's',
    title: 'm',
  },
  sections,
});

const pill = ({
  text,
  mode,
  width = 'fit-content',
  background_color,
  link,
  font_sizes = {
    text: 's',
  },
  font_colors = {
    text: '#ffffff',
  },
}) => ({
  component_type: 'pill',
  text,
  mode,
  font_colors,
  width,
  background_color,
  margin: margins('1rem', '1rem'),
  font_sizes,
  link,
});

const phaseStepCard = ({
  title,
  content,
  pill,
  objective,
  imageSrc,
  labels,
  info_points,
  tap,
  dragger_ab,
  dragger_directional,
  bottom_content,
  picture_in_picture,
  header,
}) => ({
  component_type: 'phase_step_card',
  header,
  title,
  tap,
  labels,
  info_points,
  dragger_ab,
  dragger_directional,
  picture_in_picture,
  font_color: '#4e4e4e',
  font_sizes: {
    title: 'm',
  },
  margin: margins('2rem', '0rem'),
  content,
  pill,
  objective,
  image: {
    src: imageSrc,
  },
  bottom_content,
});

const makeDocumentTitle = (title, icon) =>
  banner({ title, icon, is_bold: true, reverse: icon ? true : false });

const pageBreak = () => ({
  component_type: 'page_break',
});

const componentTypes = {
  GALLERY: 'gallery',
  LIST: 'list',
  TEXT: 'text',
  AUTHOR: 'author',
  NUMBERED_LIST: 'numbered_list',
};

module.exports = {
  documentConfig,
  banner,
  htmlMarkup,
  intro,
  divider,
  tableOfContents,
  article,
  pill,
  phaseStepCard,
  makeDocumentTitle,
  pageBreak,
  componentTypes,
};
