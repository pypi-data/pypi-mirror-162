import os
import json
import pandas as pd
from pprint import pprint
from glob import glob

data_ = ["ontonotes5", "conll2003",  "wnut2017", "panx_dataset/en", "bionlp2004", "bc5cdr", "fin"]
data_lower_ = data_ + ["mit_restaurant", "mit_movie_trivia"]
panx_data_ = [
    "panx_dataset/en", "panx_dataset/ja", "panx_dataset/ru", "panx_dataset/ko", "panx_dataset/es", "panx_dataset/ar"
]


def summary(base_model: bool = False, lower: bool = False, panx: bool = False):
    f1_in_domain = {'es': {}, 'ner': {}}
    f1_out_domain = {'es': {}, 'ner': {}}
    if panx:
        assert not lower
    if lower:
        data = data_lower_
    elif panx:
        data = panx_data_
    else:
        data = data_
    checkpoint_dir = './ckpt'
    if base_model:
        checkpoint_dir += '/model_base'
    else:
        checkpoint_dir += '/model_large'

    if lower:
        checkpoint_dir += '_lower'

    print(checkpoint_dir)
    input()
    for i in glob('{}/*'.format(checkpoint_dir)):
        if not os.path.isdir(i):
            continue

        with open('{}/parameter.json'.format(i)) as f:
            param = json.load(f)
        if not base_model and param['transformers_model'] != "xlm-roberta-large":
            continue
        if base_model and param['transformers_model'] != "xlm-roberta-base":
            continue
        if lower and not param['lower_case']:
            continue
        if not lower and param['lower_case']:
            continue
        if len(param['dataset']) > 1:
            train_data = 'all_english'
        else:
            train_data = param['dataset'][0]
            if train_data not in data:
                continue

        for a in glob('{}/test*.json'.format(i)):
            test_data = a.split('test_')[-1].split('.json')[0]

            if lower and 'lower' not in test_data:
                continue
            if not lower and 'lower' in test_data:
                continue
            task = 'es' if 'ignore' in test_data or 'span' in test_data else 'ner'
            test_data = test_data.replace('-', '/').replace('_lower', '').replace('_span', '')
            if test_data not in data:
                continue

            print(train_data, test_data, task)

            with open(a) as f:
                test = json.load(f)
            metric = test['test'] if 'test' in test.keys() else test['valid']
            f1 = round(metric['f1'], 2)

            if train_data not in f1_out_domain[task].keys():
                f1_out_domain[task][train_data] = {}
            f1_out_domain[task][train_data][test_data] = f1
            if test_data == train_data and train_data not in f1_in_domain[task].keys():
                f1_in_domain[task][train_data] = f1

    if not lower:
        in_result = [list(f1_in_domain['ner'].values())]
        in_result_key = list(f1_in_domain['ner'].keys())
        df = pd.DataFrame(in_result, columns=in_result_key, index=['f1']).T
        df = df.T[data].T
        pprint(df)
        if panx:
            df.to_csv('{}/summary_in_domain.f1.panx.csv'.format(checkpoint_dir))
        else:
            df.to_csv('{}/summary_in_domain.f1.csv'.format(checkpoint_dir))

    if panx:
        tmp_df = pd.DataFrame(f1_out_domain['ner']).T
        tmp_df = tmp_df[data]
        tmp_df = tmp_df.T[data].T
        pprint(tmp_df)
        tmp_df.to_csv('{}/summary_out_domain.f1.panx.csv'.format(checkpoint_dir))
    else:
        tmp_df = pd.DataFrame(f1_out_domain['es']).T
        tmp_df = tmp_df[data]
        all_data = data + ["all_english"]
        tmp_df = tmp_df.T[all_data].T
        pprint(tmp_df)
        tmp_df.to_csv('{}/summary_out_domain.f1.span.csv'.format(checkpoint_dir))
        tmp_df = pd.DataFrame(f1_out_domain['ner']).T
        tmp_df = tmp_df[data]
        tmp_df = tmp_df.T['all_english']
        pprint(tmp_df)
        tmp_df.to_csv('{}/summary_out_domain.f1.csv'.format(checkpoint_dir))


if __name__ == '__main__':
    summary(base_model=True, lower=True)
    summary(base_model=False, lower=True)
    summary(base_model=True, lower=False)
    summary(base_model=False, lower=False)

    summary(base_model=True, panx=True)
    summary(base_model=False, panx=True)
