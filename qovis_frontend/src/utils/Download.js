export function exportSVG(svgElement, filename) {
  const svgDoc = document.implementation.createDocument("http://www.w3.org/2000/svg", "svg");
  svgDoc.replaceChild(svgElement.cloneNode(true), svgDoc.documentElement);

  const elements = svgDoc.querySelectorAll("*");
  elements.forEach(el => {
    const styleRules = getStyleRules(el)
    // add styles to el
    styleRules.forEach(rule => {
      el.style.cssText += rule.style.cssText
    })
  })

  // download
  const svgData = (new XMLSerializer()).serializeToString(svgDoc);
  const blob = new Blob([svgData.replace(/></g, ">\n\r<")], {type: "image/svg+xml;charset=utf-8"});

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * @param element
 * @returns {CSSStyleRule[]}
 */
function getStyleRules(element) {
// Get all the stylesheets in the document
  const styleSheets = document.styleSheets;

// Array to store the matching styles
  const matchingStyleRules = [];

// Iterate through each stylesheet
  for (let i = 0; i < styleSheets.length; i++) {
    const styleSheet = styleSheets[i];

    // Check if the stylesheet is accessible (due to cross-origin restrictions)
    if (!styleSheet.href || styleSheet.href.startsWith(window.location.origin)) {
      const rules = styleSheet.cssRules || styleSheet.rules;

      // Iterate through each style rule in the stylesheet
      for (let j = 0; j < rules.length; j++) {
        const rule = rules[j];

        // Check if the rule matches the desired class name
        if (element.matches(rule.selectorText)) {
          // Add the matching rule to the array
          matchingStyleRules.push(rule);
        }
      }
    }
  }

  // Return the matching styles
  return matchingStyleRules;
}
