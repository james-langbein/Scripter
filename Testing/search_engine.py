from prettyprinter import pprint
from rank_bm25 import BM25Okapi
import spacy
import os

directory = 'C:\\Users\\JamesLangbein\\All\\SQL Scripts'
nlp = spacy.load('en_core_web_sm')
nlp.disable_pipes(['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'ner', 'lemmatizer'])


def get_corpus(root):
    """Assumes that recursive subdirectory search is always desired."""
    _corpus = []
    for path, subdirs, files in os.walk(top=root):
        for filename in files:
            folder_path = path

            title = filename

            title_tokens = filename.split('.')[0].split(' ')

            with open(os.path.join(path, filename), 'r', encoding='UTF-8') as f:
                try:
                    content = f.read()
                    content.replace('--', '')
                    doc = nlp(content)
                    content_tokens = set([token.text for token in doc if token.is_alpha])
                except Exception as e:
                    print(f, e)

            last_modified = os.path.getmtime(path)

            _corpus.append({
                'folder_path': folder_path,
                'title': title,
                'title_tokens': title_tokens,
                'content': content,
                'content_tokens': content_tokens,
                'last_modified': last_modified
            })
    return _corpus


def get_scores(query, tok_corpus):
    bm25 = BM25Okapi(tok_corpus)
    tokenised_query = query.split(' ')
    _item_scores = bm25.get_scores(tokenised_query)
    return _item_scores


def get_top_n_results(query, tok_corpus, full_corpus, n):
    bm25 = BM25Okapi(tok_corpus)
    _results = bm25.get_top_n(query.split(' '), full_corpus, n=n)
    return _results

    # TODO: pickle dump the corpus and reload if exists, rather than rebuilding the corpus
    # TODO: implement get_corpus and get_scores into the GUI code
    # TODO: after loading a saved pickle, iterate through corpus and compare saved mod date vs real mod date
    #       reload file into corpus if real mod date > saved mod date


if __name__ == '__main__':
    # get_scores
    corpus = get_corpus(directory)
    scores = get_scores('health', [x['title_tokens'] for x in corpus])
    relevant_files = [v['title'] for k, v in enumerate(corpus) if scores[k] > 0]
    filelist = [x['title'] for x in corpus]

    pprint(f'Length of corpus: {len(corpus)}')
    pprint(f'Length of results: {len(scores)}')
    pprint(relevant_files)
    pprint(scores)
    pprint(corpus)
    pprint(filelist)

    # get_top_n_results
    # corpus = get_corpus(directory)
    # results = get_top_n_results('AG health', tokenised_corpus, corpus, 20)
    # pprint(results)
