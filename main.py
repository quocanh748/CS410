from pb import create_population, init_run, run_for_n
from pb.mutation_prompts import mutation_prompts
from pb.thinking_styles import thinking_styles

import os
import logging
import argparse
import asyncio

from dotenv import load_dotenv
from rich import print

load_dotenv() # load environment variables

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Run the PromptBreeder Algorithm. Number of units is mp * ts.')
parser.add_argument('-mp', '--num_mutation_prompts', type=int, default=2)     
parser.add_argument('-ts', '--num_thinking_styles', type=int, default=4)     
parser.add_argument('-e', '--num_evals', type=int, default=10)     
parser.add_argument('-n', '--simulations', type=int, default=10)     
parser.add_argument('-p', '--problem', type=str, default="Solve the math word problem, giving your answer as an arabic numeral.")       
parser.add_argument('--use_hf', action='store_true', help='Use Hugging Face model loaded directly in VRAM instead of Ollama')
parser.add_argument('-m', '--model', type=str, default=None, help='Model name. (Defaults: HF -> "Qwen/Qwen2.5-1.5B-Instruct", Ollama -> "qwen2.5:1.5b")')

args = vars(parser.parse_args())

total_evaluations = args['num_mutation_prompts']*args['num_thinking_styles']*args['num_evals']

# Initialize Model Client based on --use_hf flag
if args['use_hf']:
    from pb.hf_model import HFClient
    model_name = args['model'] if args['model'] else "Qwen/Qwen2.5-1.5B-Instruct"
    co = HFClient(model_name=model_name)
else:
    from pb.local_model import LocalClient
    model_name = args['model'] if args['model'] else "qwen2.5:1.5b"
    co = LocalClient(model_name=model_name)

tp_set = mutation_prompts[:int(args['num_mutation_prompts'])]
mutator_set= thinking_styles[:int(args['num_thinking_styles'])]

logger.info(f'You are prompt-optimizing for the problem: {args["problem"]}')

logger.info(f'Creating the population...')
p = create_population(tp_set=tp_set, mutator_set=mutator_set, problem_description=args['problem'])

logger.info(f'Generating the initial prompts...')
init_run(p, co, int(args['num_evals']))

logger.info(f'Starting the genetic algorithm...')
run_for_n(n=int(args['simulations']), population=p, model=co, num_evals=int(args['num_evals']))

print("%"*80)
print("done processing! final gen:")
print(p.units)
