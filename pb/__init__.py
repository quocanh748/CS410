import warnings
import random
import re
import logging
import os
import concurrent.futures
from typing import List, Any

from rich import print
import time
try:
    from cohere import Client
except ImportError:
    Client = None


from pb.mutation_operators import mutate
from pb import gsm
from pb.types import EvolutionUnit, Population

logger = logging.getLogger(__name__)

gsm8k_examples = gsm.read_jsonl('pb/data/gsm.jsonl')

def create_population(tp_set: List, mutator_set: List, problem_description: str) -> Population:
    """samples the mutation_prompts and thinking_styles and returns a 'Population' object.

    Args:
        'size' (int): the size of the population to create.
        'problem_description (D)' (str): the problem description we are optimizing for.
    """
    data = {
        'size': len(tp_set)*len(mutator_set),
        'age': 0,
        'problem_description' : problem_description,
        'elites' : [],
        'units': [EvolutionUnit(**{
            'T' : t, 
            'M' : m,
            'P' : '',
            'fitness' : 0,
            'history' : []
            }) for t in tp_set for m in mutator_set]
    }

    return Population(**data)

def init_run(population: Population, model: Any, num_evals: int):
    """ The first run of the population that consumes the prompt_description and 
    creates the first prompt_tasks.
    
    Args:
        population (Population): A population created by `create_population`.
    """

    start_time = time.time()

    prompts = []

    for unit in population.units:    
        template= f"{unit.T} {unit.M} INSTRUCTION: {population.problem_description} INSTRUCTION MUTANT = "
        prompts.append(template)
    
 
    results = model.batch_generate(prompts)

    end_time = time.time()

    logger.info(f"Prompt initialization done. {end_time - start_time}s")

    assert len(results) == population.size, "size of google response to population is mismatched"
    for i, item in enumerate(results):
        population.units[i].P = item[0].text
        print(f"DEBUG: Initial Task-Prompt {i}: {population.units[i].P[:100]}...")

    _evaluate_fitness(population, model, num_evals)
    
    return population

def run_for_n(n: int, population: Population, model: Any, num_evals: int):
    """ Runs the genetic algorithm for n generations.
    """     
    p = population
    for i in range(n):  
        print(f"================== Population {i} ================== ")
        mutate(p, model)
        print("done mutation")
        _evaluate_fitness(p, model, num_evals)
        print("done evaluation")

    return p

def _evaluate_fitness(population: Population, model: Any, num_evals: int) -> Population:
    """ Evaluates each prompt P on a batch of Q&A samples, and populates the fitness values.
    """
    # need to query each prompt, and extract the answer. hardcoded 4 examples for now.
    
    logger.info(f"Starting fitness evaluation...")
    start_time = time.time()

    # Use a random sample for evaluation to avoid overfitting to the first few examples
    batch = random.sample(gsm8k_examples, num_evals)

    elite_fitness = -1
    examples = []
    for unit in population.units:
        unit.fitness = 0
        examples.append([unit.P + ' \n' + example['question'] for example in batch])

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(examples)) as executor:
        future_to_fit = {executor.submit(model.batch_generate, example_batch,  temperature=0): example_batch for example_batch in examples}
        for future in concurrent.futures.as_completed(future_to_fit):
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print(f"Exception during fitness evaluation: {exc}")

    for unit_index, fitness_results in enumerate(results):
        unit = population.units[unit_index]
        for i, x in enumerate(fitness_results):
            answer = gsm.gsm_extract_answer(batch[i]['answer'])
            model_completion = x[0].text
            
            # Try to extract formatted answer first (#### [answer])
            model_answer = gsm.gsm_extract_answer(model_completion)
            
            if model_answer != gsm.INVALID_ANS:
                valid = (model_answer == answer)
            else:
                # Fallback: Find the last number in the output
                # This is a common heuristic for GSM8K models that don't use the #### format
                numbers = re.findall(r"[-+]?\d*\.?\d+", model_completion)
                if numbers:
                    # Clean up the last number (remove commas etc if any, though re.findall above doesn't catch them)
                    last_number = numbers[-1].replace(",", "")
                    valid = (last_number == answer)
                else:
                    valid = False
            
            if valid:
                unit.fitness += (1 / num_evals)

            if unit.fitness > elite_fitness:
                current_elite = unit.model_copy()
                elite_fitness = unit.fitness
    
    # append best unit of generation to the elites list.
    population.elites.append(current_elite)
    end_time = time.time()
    logger.info(f"Done fitness evaluation. {end_time - start_time}s")

    return population