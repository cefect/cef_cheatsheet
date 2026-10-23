// Compact, greyscale one-page reference sheet template (see docs/adr/0001-reference-sheet-print-format.md).
// Replaces Quarto's typst-template.typ partial; unused Quarto arguments are absorbed by `..rest`.
#let article(
  title: none,
  subtitle: none,
  fontsize: 12pt,
  ..rest,
  doc,
) = {
  // base text: black, left-aligned, tight leading
  set text(size: fontsize, fill: black)
  set par(justify: false, leading: 0.5em, spacing: 0.7em)

  // greyscale: code and links black; raw defaults to 0.8em, so 1.25em restores the body size
  show raw: set text(size: 1.25em, fill: black)
  show link: set text(fill: black)

  // footnotes may go below the 12pt minimum (ADR floor: 6pt)
  show footnote.entry: set text(size: 8pt)
  set footnote.entry(gap: 0.2em, clearance: 0.6em)

  // compact section headings (smaller than the title)
  show heading: it => block(above: 0.9em, below: 0.4em, text(size: fontsize * 1.15, weight: "bold", it.body))

  // tables: alternating grey rows (header is row 0), no rules
  set table(
    fill: (_, y) => if calc.even(y) and y > 0 { luma(230) },
    stroke: none,
    inset: (x: 4pt, y: 4pt),
  )

  // one-line title block
  if title != none {
    block(below: 0.6em)[
      #text(size: 1.4em, weight: "bold")[#title]
      #if subtitle != none { h(0.8em); text(style: "italic")[#subtitle] }
    ]
  }

  doc
}
