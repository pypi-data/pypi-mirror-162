# -*- coding: utf-8 -*-
"""
Boost the pipeline with pipeline-turbo 

@author: dreji18, AfreenAman
"""

# multithreading
import concurrent.futures
import tqdm
    
# parallel threading for the pipeline
def turbo_threading(item_list,run_func, *custom, num_threads):
    text_i2predictions = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        threads = dict()
        for item in item_list:
            thread = executor.submit(run_func, item, *custom)
            threads[thread] = item 
        for future in tqdm.tqdm(concurrent.futures.as_completed(threads)):
            result = future.result()
            text_i = threads[future]
            text_i2predictions[text_i] = result
    
    keys = list(text_i2predictions.keys())
    keys.sort()
    result_list = []
    for k in keys:
        result_list.append(text_i2predictions[k])    
    
    return result_list    


