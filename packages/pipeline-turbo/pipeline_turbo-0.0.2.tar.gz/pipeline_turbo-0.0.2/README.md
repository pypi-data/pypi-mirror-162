pipeline-turbo is a package that will accelerate your processing pipeline. It works with the multi-threading concept in the background. It has been successful in both CPU and GPU tasks.

The only pre-requisite is to load the function running for a single process and adjust the threads according to your resource availability.

Read more about threading here: https://www.activestate.com/blog/how-to-manage-threads-in-python/

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install pipeline-turbo

```bash
pip install pipeline-turbo
```

## Example Usage

```python
# Create your pipeline process 
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = ['This framework generates embeddings for each input sentence',
    'Sentences are passed as a list of string.',
    'The quick brown fox jumps over the lazy dog.']

sentences = sentences*100
test_list = sentences *100

# define the function which runs for 1 sentence/instance
def return_embed(sentence, test_list):
    
    query_vect = model.encode([sentence])
    
    score_list = []
    for k in test_list:
        val_vect = model.encode([k])
        cos_sim = util.cos_sim(query_vect, val_vect)
        score_list.append(cos_sim)
    
    return score_list

# call the turbo_threading function
"""
the iterator is 'sentence' which lies in 'sentences list' and that has to be defined as the first argument
followed by the function and its other arguments
finally define the thread based on your resource availability
"""
from pipeline_turbo.turbo import turbo_threading
turbo_out = turbo_threading(sentences, return_embed, test_list, num_threads=5)

"""
you can pass any number of arguments inside the function, but the iterable list has to be defined first
The performance varies based on the processing speed of your machine/compute
"""

```

## About
This package is created by Deepak John Reji, Afreen Aman. It was first used to speed up some deep learning pipeline projects and later made it open source


## License
[MIT](https://choosealicense.com/licenses/mit/) License
