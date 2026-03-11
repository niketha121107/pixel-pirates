const MOJIBAKE_REPLACEMENTS: Array<[RegExp, string]> = [
    [/\u00e2\u20ac\u2122|\u00e2\u20ac\u02dc/g, "'"],
    [/\u00e2\u20ac\u0153|\u00e2\u20ac\u009d|\u00e2\u20acd/g, '"'],
    [/\u00e2\u20ac\u201d|\u00e2\u20ac\u201c/g, '-'],
    [/\u00e2\u20ac\u00a6/g, '...'],
    [/\u00e2\u2020\u2019|\u2192/g, '->'],
    [/\u00c2/g, ''],
    [/\u00c3\u00a9|\u00c3\u00a8/g, 'e'],
    [/\u00c3/g, ''],
    [/\ufffd/g, ''],
    [/â€“|â€”/g, '-'],
    [/â€˜|â€™/g, "'"],
    [/â€œ|â€/g, '"'],
    [/â€¦/g, '...'],
    [/Â/g, ''],
    [/ðŸ[^\s]*/g, ''],
];

export const sanitizeMojibakeText = (value: string) => {
    let next = String(value ?? '');
    for (const [pattern, replacement] of MOJIBAKE_REPLACEMENTS) {
        next = next.replace(pattern, replacement);
    }
    return next.replace(/\s+/g, ' ').trim();
};

export const sanitizeMojibakePreserveLines = (value: string) => {
    const lines = String(value ?? '').split('\n');
    return lines.map((line) => sanitizeMojibakeText(line)).join('\n');
};