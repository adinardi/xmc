thetr.string = {};

/**
 * Trim whitespace from around a string.
 * @param {string} string The string to trim.
 * @return {string} The trimmed String.
 */
thetr.string.trim = function(args) {
  var s = args.string;
  var ns = '';
  var curPos = 0;
  while (s.charAt(curPos).search(/\s/) > -1) {
    curPos++;
  }
  ns = s.substr(curPos);
 
  curPos = ns.length - 1;
  while (ns.charAt(curPos).search(/\s/) > -1) {
    curPos--;
  }
  ns = ns.substr(0, curPos + 1);

  return ns;
};