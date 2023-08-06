[![Build](https://github.com/vigenere23/modupipe/actions/workflows/build.yml/badge.svg)](https://github.com/vigenere23/modupipe/actions/workflows/build.yml)

# ModuPipe : A modular and extensible ETL-like pipeline builder

## Benefits

- Entirely typed
- Abstract, so it fits any use case
- Class-based for easy configurations and injections

## Usage

Extract-Transform-Load (ETL) pipelines are a classic form of data-processing pipelines used in the industry. It consists of 3 main elements:

1. An **`Extractor`**, which returns data in a stream-like structure (`Iterator` in Python) using a pull strategy.
2. Some **`Mapper`** (optional), which transforms (parse, converts, filters, etc.) the data obtained from the source(s). Mappers can be chained together and chained to an extractor (with `+`) in order to form a new extractor.
3. A **`Loader`**, which receives the maybe-transformed data using a push strategy. Loaders can be multiple (with `LoaderList`) or chained together (with `+`).

Therefore, those 3 processes are offered as interfaces, easily chainable and interchangeable at any time.

An interface `Runnable` is also offered in order to interface the concept of "running a pipeline". This enables a powerfull composition pattern for wrapping the execution behaviour of runnables.

## Examples

Usage examples are present in the [examples](./examples) folder.

## Discussion

### Optimizing pushing to multiple loaders

If you have multiple loaders (using the `LoaderList` class or many chained `PushTo` mappers), but performance is a must, then you should use a multi-processing approach (with `modupipe.runnable.MultiProcess`), and push to 1 queue per loader. Each queue will also become a direct extractor for each loader, all running in parallel. This is especially usefull when at least one of the loaders takes a long processing time.

As an example, let's take a `Loader 1` which is very slow, and a `Loader 2` which is normally fast. You'll be going from :

```
┌────── single pipeline ──────┐        ┌──────────────── single pipeline ───────────────┐
 Extractor ┬─⏵ Loader 1 (slow)    OR    Extractor ──⏵ Loader 1 (slow) ──⏵ Loader 2 (late)
           └─⏵ Loader 2 (late)
```

to :

```
┌────── pipeline 1 ──────┐               ┌────────── pipeline 2 ─────────┐
 Extractor ┬─⏵ PutToQueue ──⏵ Queue 1 ⏴── GetFromQueue ──⏵ Loader 1 (slow)
           └─⏵ PutToQueue ──⏵ Queue 2 ⏴── GetFromQueue ──⏵ Loader 2 (not late)
                                         └──────────── pipeline 3 ───────────┘
```

This will of course not accelerate the `Loader 1` processing time, but all the other loaders performances will be greatly improved by not waiting for each other.
