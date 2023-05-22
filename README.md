# Final project for NLP course ODS

## Intro
Just like in other areas, the use of natural language processing and machine learning has become crucial in the film industry. However, pretrained transformer models often fail to perform well in domain-specific tasks due to the lack of domain-specific data. 

In this work, we collect film-industry-specific data and perform domain adaptation of model, comparing the results obtained with model without domain adaptation for the task of predicting the sentiment of movie reviews.

## Data
At the moment, the database contains more than 71,000 films. Reviews were collected by parsing from online cinemas.

To collect a dataset of reviews and their embeddings, a separate package was created - `text2rec`, which includes the following console scripts:
- `get_reviews` - parse reviews using movie ID file as input
- `filter_reviews` - filter reviews, restore punctuation, remove special unicode characters or convert them to `ASCII` encoding range
- `translate_reviews` - translate reviews into English, since the service is based on a model trained only in English
- `get_embeddings` - get review embeddings for semantic search

The package can be installed with the following command:
```sh
pip install -e .
```

For the convenience of using scripts, a script launch line based on `Snakemake` was created. The following command is used to start the pipeline:
```sh
snakemake --cores all
```

By default, snakemake will take the `dataset/raw/{DATASET}_ids.csv` file and run it through all scripts. The startup pipeline can be configured using the `workflow/config.yaml` file, in which the dataset (file with IDs) and the name of the column with the text of reviews are selected.

The `text2rec` package must be installed before using `snakemake`.

Data directory structure:
```sh
data
├───raw ------------ Add .csv files with movie IDs to this folder
├───processed ------ Here are the results of the pipeline - files with review embeddings
└───reviews -------- Root directory for all stages of review processing
     ├───raw -------- Directory with reviews after parsing
     ├───filtered --- Catalog with filtered reviews
     └───translated - Catalog with reviews in English
```

For testing, we used the [imdb dataset](http://ai.stanford.edu/~amaas/data/sentiment/)

## Model
[Base model](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english) is a fine-tune checkpoint of [DistilBERT](https://arxiv.org/abs/1910.01108), fine-tuned on SST-2. 
Weights of the domain adapted model can be found at the [link](https://drive.google.com/file/d/1wslRSQZ3djIylmB_8vFJNsi6wijnYRfN/view?usp=share_link).
You can see more details in the [notebook](domain-adoptation.ipynb).

## Results
The results showed that the domain adapted model is better at classifying specific reviews after finetuning than the model without domain adaptation. The difference in accuracy is visible even with not the most careful selection of hyperparameters.

Accuracy:
With domain adoptation - 82% 
Without domain adoptation - 78%

You can read more details in the work [report](report.pdf).


## Team
Vsevolod Vlasov - @sesevasa64

Yuriy Kim - @Yuki-53