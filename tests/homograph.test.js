const { isConfusable, hasMixedScripts } = require('../src/homograph');

describe('isConfusable', () => {
  it('should detect Cyrillic "a" in a domain', () => {
    expect(isConfusable('ex\u0430mplebank.example')).toBe(true);
  });

  it('should detect Cyrillic "c" in a domain', () => {
    expect(isConfusable('\u0441heck.com')).toBe(true);
  });

  it('should detect Cyrillic "e" in a domain', () => {
    expect(isConfusable('t\u0435st.com')).toBe(true);
  });

  it('should detect Cyrillic "o" in a domain', () => {
    expect(isConfusable('l\u043Egin.com')).toBe(true);
  });

  it('should detect Cyrillic "p" in a domain', () => {
    expect(isConfusable('a\u0440\u0440le.com')).toBe(true);
  });

  it('should detect confusables in a punycode domain', () => {
    expect(isConfusable('xn--exmplebank-0qi.example')).toBe(true); // exаmplebank
  });

  it('should detect confusables when there is a subdomain in front of punycode', () => {
    expect(isConfusable('www.xn--exmplebank-0qi.example')).toBe(true);
  });

  it('should return false for completely Latin domain', () => {
    expect(isConfusable('examplebank.example')).toBe(false);
  });
});

describe('hasMixedScripts', () => {
  it('should return true for a domain mixing Latin and Cyrillic', () => {
    expect(hasMixedScripts('ex\u0430mplebank.example')).toBe(true);
  });

  it('should return true for a punycode domain mixing Latin and Cyrillic', () => {
    expect(hasMixedScripts('xn--exmplebank-0qi.example')).toBe(true);
  });

  it('should return true when there is a subdomain in front of punycode mixing Latin and Cyrillic', () => {
    expect(hasMixedScripts('www.xn--exmplebank-0qi.example')).toBe(true);
  });

  it('should return false for purely Latin domain', () => {
    expect(hasMixedScripts('examplebank.example')).toBe(false);
  });

  it('should return false for purely Cyrillic domain', () => {
    expect(hasMixedScripts('\u043C\u043E\u0441\u043A\u0432\u0430.рф')).toBe(false); // москва.рф
  });

  it('should return false for a purely Cyrillic punycode domain', () => {
     expect(hasMixedScripts('xn--80adxhks.xn--p1ai')).toBe(false); // москва.рф
  });
});
