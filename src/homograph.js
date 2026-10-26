const punycode = require('punycode/');

/**
 * Maps known confusable Cyrillic characters to their Latin counterparts.
 */
const CONFUSABLES = {
  '\u0430': 'a', // Cyrillic a
  '\u0441': 'c', // Cyrillic c
  '\u0435': 'e', // Cyrillic e
  '\u043E': 'o', // Cyrillic o
  '\u0440': 'p', // Cyrillic p
};

/**
 * Checks if a string contains any of the known confusable characters.
 * @param {string} domain
 * @returns {boolean}
 */
function isConfusable(domain) {
  // Decode punycode if necessary
  const decoded = punycode.toUnicode(domain);

  for (let i = 0; i < decoded.length; i++) {
    if (CONFUSABLES[decoded[i]]) {
      return true;
    }
  }
  return false;
}

/**
 * Checks if a string mixes different scripts (e.g. Latin and Cyrillic)
 * @param {string} domain
 * @returns {boolean}
 */
function hasMixedScripts(domain) {
  const decoded = punycode.toUnicode(domain);

  const hasLatin = /[a-zA-Z]/.test(decoded);
  const hasCyrillic = /[\u0400-\u04FF]/.test(decoded);
  const hasGreek = /[\u0370-\u03FF]/.test(decoded);

  let scriptsCount = 0;
  if (hasLatin) scriptsCount++;
  if (hasCyrillic) scriptsCount++;
  if (hasGreek) scriptsCount++;

  return scriptsCount > 1;
}

module.exports = {
  isConfusable,
  hasMixedScripts
};
