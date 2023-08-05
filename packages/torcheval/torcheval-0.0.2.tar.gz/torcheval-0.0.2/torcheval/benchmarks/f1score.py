import argparse
import torch

from .utils import get_benchmark_stats, setup_distributed, generate_random_input, InputType, rank_0_print
from typing import Any, Dict, Callable
from torcheval.metrics import Metric, MulticlassF1Score
from torcheval.metrics.toolkit import sync_and_compute
import torch.distributed.launcher as pet
import uuid


### INPUT GENERATION
def generate_update_args_multiclass(num_batches:int, batch_size:int, device: torch.device, num_classes: int) -> Dict[str, Any]:
    input = generate_random_input(InputType.MULTICLASS_LOGIT, device, num_batches, batch_size, num_classes=num_classes)
    target = generate_random_input(InputType.MULTICLASS_LABEL, device, num_batches, batch_size, num_classes=num_classes)
    return {"input": input, "target": target}

### METRIC COMPUTATIONS
def run_metric_computation(metric: Metric, num_batches:int, compute_interval:int, update_kwargs: Dict[str, Any]):
    for batch_idx in range(num_batches):
        metric.update(update_kwargs["input"][batch_idx], update_kwargs["target"][batch_idx])
        if (batch_idx + 1) % compute_interval == 0:
            sync_and_compute(metric)

def main(num_batches, batch_size, compute_interval, num_classes):
    device = setup_distributed()

    rank_0_print(f"Benchmark MulticlassF1Score...")
    metric = MulticlassF1Score().to(device)
    update_kwargs = generate_update_args_multiclass(num_batches, batch_size, device, num_classes)
    get_benchmark_stats(metric, num_batches, compute_interval, update_kwargs)

if __name__ == "__main__":
    print("Benchmark F1Score metrics...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-batches", type=int, default=int(10_000))
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--compute_interval", type=int, default=100)
    parser.add_argument("--num-processes", type=int, default=4)
    parser.add_argument("--num-classes", type=int, default=10)
    parser.add_argument("--use-pet", action="store_true", default=False)

    args = parser.parse_args()

    if args.use_pet:
        lc = pet.LaunchConfig(
                min_nodes=1,
                max_nodes=1,
                nproc_per_node=args.num_processes,
                run_id=str(uuid.uuid4()),
                rdzv_backend="c10d",
                rdzv_endpoint="localhost:0",
                max_restarts=0,
                monitor_interval=1,
        )
        pet.elastic_launch(lc, entrypoint=main)(
         args.num_batches, args.batch_size, args.compute_interval, args.num_classes
        )
    else:
        main(args.num_batches, args.batch_size, args.compute_interval, args.num_classes)
