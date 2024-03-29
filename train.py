import logging
import json

from lib import UserSimulator
from lib import ErrorModelController
from lib import DialogueManager
from run import run_period

logging.basicConfig(
    filename="log/train.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(message)s"
)

N_PERIODS = 50
EPISODES_PER_PERIOD = 100


if __name__ == "__main__":

    dialogue_manager = DialogueManager(kb_filepath="data/knowledge_base.json")
    dialogue_manager.load("models/WarmedUp")
    usersim = UserSimulator(
        kb_filepath="data/knowledge_base.json",
        goals_filepath="data/user_goals.json"
    )
    error_model_controller = ErrorModelController(error_probability=0.02)

    logging.info(
        "**********************************************************\n"
        "******************** TRAINING STARTED ********************\n"
        "**********************************************************\n"
    )

    avg_rewards = []
    avg_successes = []

    for n_period in range(1, N_PERIODS + 1):

        logging.info(
            f"************* TRAINING PERIOD N. {n_period} *************\n"
        )

        avg_success, avg_reward, is_memory_full = run_period(
            dialogue_manager,
            usersim,
            error_model_controller,
            warmup=False,
            max_episodes=EPISODES_PER_PERIOD
        )

        logging.info(f"\nRL AGENT IS TRAINING...")
        dialogue_manager.train()
        if is_memory_full:
            logging.info("FREEING DIALOGUE MANAGER MEMORY...")
            dialogue_manager.empty_rl_mem(fraction=0.1)

        avg_rewards.append(avg_reward)
        avg_successes.append(avg_success)
        logging.info(
            "\n================================================\n"
            f"    TRAINING PERIOD N. {n_period} COMPLETED    \n"
            "------------------------------------------------\n"
            f"Average success = {avg_success}\n"
            f"Average reward = {avg_reward}\n"
            "================================================\n"
        )
    
    train_results = {
        "avg_rewards": avg_rewards,
        "avg_successes": avg_successes
    }
    with open("results/train_results.json", "w") as train_results_file:
        train_results_file.write(json.dumps(train_results))
    dialogue_manager.save("models/Trained")
