# Changelog 

## v2.6.0 (2022-08-08)

### Feat

- code for word evaluations

## v2.5.0 (2022-08-05)

### Feat

-  geolocation

## v2.4.7 (2022-07-13)

### Fix

- error in NER
- error in NER

## v2.4.6 (2022-07-13)

### Fix

- removed spacy import in parse.py
- removed spacy import in parse.py

## v2.4.5 (2022-07-13)

### Fix

- name error
- name error

## v2.4.4 (2022-07-13)

### Fix

- added spacy to requirements.txt

## v2.4.3 (2022-07-13)

### Fix

- added parse.py file

## v2.4.2 (2022-07-12)

### Fix

- double def of function
- something weird...

## v2.4.1 (2022-07-12)

### Fix

- weirder
- weirder

## v2.4.0 (2022-07-12)

### Feat

- ner with spaCy
- ner with spaCy

## v2.3.6 (2022-07-12)

### Fix

- nb_ngram to point to new endpoint
- nb_ngram to point to new endpoint

## v2.3.5 (2022-07-11)

### Fix

- word counts
- word counts

## v2.3.4 (2022-07-11)

### Fix

- counts variable crossing
- counts variable crossing

## v2.3.3 (2022-07-11)

### Fix

- counting api
- counting api

## v2.3.2 (2022-07-11)

### Fix

- frequency and counts
- frequency and counts

## v2.3.1 (2022-06-21)

### Fix

- frequency

## v2.3.0 (2022-06-02)

### Fix

- parenthesis
- parenthesis

### Feat

- added access to Norsk Ordbank, wordbank

## v2.2.2 (2022-05-24)

### Fix

- use custom personal access token in ci action

## v2.2.1 (2022-05-16)

### Fix

- use custom personal access token in ci action

## v2.2.0 (2022-05-13)

### Feat

- ngram, geodata


## v2.1.0 (2022-05-13)

### Feat

- geodata

## v2.0.25 (2022-04-27)

### Fix

- **setup.cfg**: make package dhlab importable

## v2.0.24 (2022-04-19)

### Fix

- add missing newline  (#50)

## v2.0.23 (2022-04-01)

### Fix

- **github-workflows**: change github access token (#47)
- **github-workflows**: change github access token (#46)

### Refactor

- expose dhlab v1 modules

## v2.0.22 (2022-03-22)

### Fix

- import all legacy modules in `__init__.py`

### Refactor
- move dhlab_v1 code into its own subpackage
- **docs/package_summary.rst**: add reference table for legacy code 

## v2.0.21 (2022-03-21)
### Refactor 
- **constants**: add global variables for URLs in constants.py 
- Reformat code with pep8 tools
- turn relative imports into absolute imports
- simplify and reduce expressions
- rename classes with CamelCase

### Docs 
- **README**: add "Example use"
- add docstrings in subpackages
- add docs/CHANGELOG.md
- **docs**: add `*.rst` documentation files 
- add autosummary of whole dhlab package
- **logo**: update logo image
- add jupyter integration and toggle feature
- add copybutton to code blocks
- add docstrings and make functions private

## v2.0.20geo (2022-03-02)

### Feat
- **dhlab.api.dhlab_api**: add function `get_places`
- **text.geo_data**: add class `GeoData`

### Fix
- **text.dispersion**: pass **kwargs to `plot()` 

## v.2.0.18dispersion (2022-02-21)

### Feat
- **text.dispersion**: add class Dispersion
- **api.dhlab_api**: add get_dispersion

### Fix
- **requirements**: remove wordcloud  

## v2.0.17params (2022-02-08)
### Refactor
- **text.corpus**: add parameter fulltext
- **api.dhlab_api.document_corpus**: add parameter fulltext
- **text.conc_coll.Concordance**: add parameters window and limit 
- **text.conc_coll.Collocations**: add parameter samplesize

### Fix 
- **text.corpus.urnlist**: fix urnlist assignment

## v2.0.12.chunk (2022-01-29)
### Refactor 
- **text.chunking**: add attribute self.chunks

### Fix 
- imports


## v2.0.10chunks (2022-01-29)

### Feat
- **text.conc_coll**: add class Counts 
- **text.corpus**: add class Corpus_from_identifiers
- **text.chunking**: add class Chunks
- **text.chunking**: add functions get_chunks, get_chunks_para

### Fix 
- imports
- **dhlab_api.get_chunks**: return dict not dataframe
- apply autopep8

## v2.0.5 (2022-01-19)

### Refactor

- **nbtokenizer**: edit tokens for mail and web addresses

### Feat 
- add Tokens class

### Fix 
- imports


## v2.0.2a (2022-01-18)

### Fix 

- typecheck of corpus objects

## v2.0.1.alpha6 (2022-01-18)

- changed wordcloud import
- fixed corpus transfer in conc_coll


## v2.0.0.beta (2022-01-18)

### Feat
- add get_file_from_github, download_from_github in utils

### Refactor

- New package structure

### Docs

- include installation instructions in README


## v1.0.0 (2022-01-06)

- Set up Github Actions to run automatic linting and testing
- Set up documentation pages
- Include documentation of the code in docstrings


### Fix

- address linting issues from flake8
- reformat code

### Feat

- add documentation summaries for all modules
- add documentation for the repo
- add docstrings from README.md to nbtext.py
- add pylint config file

### Refactor

- reduce code duplication
- update workflow file reference
- change str.format to f-strings
- optimize imports
- rename workflow that packages and publishes dhlab to pypi
- use default publish workflow
- reduce compatible python versions
- update publishing workflow
- type out scope for linting explicitly
- move pylint.yml

## v0.75 (2019-09-09)

- Inital release to pypi
