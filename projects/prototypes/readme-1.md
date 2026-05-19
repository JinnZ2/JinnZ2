# Media Manipulation Filter

A tool for identifying and filtering manipulative language in news headlines and media content through neutral translation.

## The Problem

Modern media headlines are designed to trigger emotional responses rather than inform. Words like “SLAMS,” “DESTROYS,” “DEVASTATES” are deliberately chosen to maximize engagement and profit, reducing complex situations to simplistic emotional triggers.

Current AI systems are trained on this manipulative content, learning to amplify these patterns rather than recognize them as problematic.

## The Solution

This project uses a unique translation approach:

1. **English → Ithquil** (neutral constructed language)
1. **Ithquil → English** (filtered, factual version)

Because Ithquil lacks manipulative emotional framing, the translation process naturally strips away bias and reveals what’s actually being reported.

## Example

**Original (Manipulative):**

> “China DEVASTATES US farmers in RUTHLESS economic attack! Soybean prices COLLAPSE as China REFUSES to buy American crops!”

**Filtered (Factual):**

> “China purchased soybeans from alternative suppliers following trade dispute”

**Missing Context:**

- Did the US impose tariffs on Chinese goods first?
- Did the US ban Chinese technology companies?
- Are Chinese companies buying from Brazil/Argentina because they’re cheaper?
- Is this normal market competition?

## Features

- **Customizable filters** by intensity and manipulation type
- **Side-by-side comparison** of original vs filtered content
- **Missing context analysis** showing information purposefully omitted
- **Translation pipeline** visualization
- **Open source** JSON mappings and filter algorithms

## Project Structure

```
/data/             - Translation mappings and filter definitions
/filters/          - Core filtering algorithms
/api/              - Backend API services
/web/              - Web demonstration interface
/docs/             - Methodology and research documentation
/examples/         - Before/after transformation examples
```

## Getting Started

(Installation and usage instructions to be added)

## Contributing

This project aims to improve information resilience and media literacy. Contributions welcome!

## License

MIT License (or your preferred license)

## Acknowledgments

Built on insights about manipulative language patterns and the importance of neutral, factual reporting in developing critical thinking skills.
