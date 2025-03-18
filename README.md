# Setting Up the Project Requirements with UV package manager

## 1. Install `UV`: A Python Package Manager
If you have python installed

```bash
pip install uv
```
Alternatively, install with a standalone installer

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Install Required Packages
```bash
uv sync
```


## 3. Scrape Meta Data
The following command will generate necessary cleaned resources in cache
```bash
uv run main.py --scrape
```
* You need to have **google chrome** installed if you're going to use the scrape function.

## 4. Embedding

Set up the database password environment variable 
```bash
export VECTOR_DB_PWD=thepasswordprovided
```

The following command will extract embedding from the scraped cache and push to the vectordb
```bash
uv run main.py --embedding
```

# Statistics
## Papers

We manually categorized the paeprs into the following categories

| Identifier      | Description                        | Count |
|-----------------|-----------------------------------|-------|
| vision          | Computer Vision                    | 99    |
| dl_nlp          | Deep Learning for NLP              | 52    |
| audio           | Audio Processing                   | 26    |
| learning_theory | Learning Theory                    | 22    |
| ml_representation| Machine Learning Representation    | 20    |
| ml_classic      | Classical Machine Learning         | 19    |
| dl_rl           | Deep Learning for Reinforcement Learning | 18 |
| dl_general      | General Deep Learning              | 17    |
| dl_rnn          | Deep Learning with RNNs            | 4     |
| dl_opt          | Deep Learning Optimization         | 4     |
| ml_tuning       | Machine Learning Hyperparameter Tuning | 4  |
| bayesian        | Bayesian Methods                   | 3     |
| ml_sampling     | Machine Learning Sampling          | 3     |
| dl_misc         | Miscellaneous Deep Learning        | 1     |
| signal          | Signal Processing                  | 1     |

| Year      | Count |
|-----------|-------|
| 2023      | 58    |
| 2022      | 62    |
| 2021      | 8     |
| 2020      | 11    |
| 2019      | 7     |
| 2018      | 11    |
| 2017      | 13    |
| 2016      | 15    |
| 2015      | 23    |
| 2014      | 22    |
| 2013      | 10    |
| 2012      | 5     |
| 2011      | 2     |
| 2010      | 2     |
| 2009      | 2     |
| 2008      | 1     |
| 2006      | 1     |
| 2003      | 2     |
| 2002      | 3     |
| 2001      | 1     |
| Pre-2000  | 33    |