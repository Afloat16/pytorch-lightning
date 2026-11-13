import inspect
import json
import torch
from torchmetrics import Metric
from lightning.pytorch.trainer.connectors.logger_connector.result import _ResultCollection
for enable in (False, True):
    value = torch.tensor(2.0, requires_grad=True)
    result = _ResultCollection(training=True)
    result.log("training_step", "loss", value.square(), on_step=True, on_epoch=True, enable_graph=enable, batch_size=1)
    for step in (True, False):
        cached = result.metrics(on_step=step)["callback"]["loss"]
        print(json.dumps({"enable_graph": enable, "on_step": step, "value": cached.item(), "requires_grad": cached.requires_grad, "grad_fn": str(cached.grad_fn)}), flush=True)
print(inspect.getsource(Metric._wrap_update), flush=True)
