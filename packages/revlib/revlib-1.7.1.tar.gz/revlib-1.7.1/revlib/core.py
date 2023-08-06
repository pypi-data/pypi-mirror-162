import copy
import enum
import threading
import typing

import torch
import torch.utils.checkpoint

DUAL_OR_QUAD_TENSOR = typing.Union[typing.Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
                                   typing.Tuple[torch.Tensor, torch.Tensor]]
TENSOR_OR_LIST = typing.Union[typing.List[torch.Tensor], torch.Tensor]
COUPLING = typing.Callable[[torch.Tensor, TENSOR_OR_LIST], TENSOR_OR_LIST]
FUSED_OPTIMIZER = typing.Optional[typing.Callable[[typing.Iterable], torch.optim.Optimizer]]


class MemoryModes(enum.IntEnum):
    no_savings = 0
    checkpoint = 1
    autograd_graph = 2
    autograd_function = 3


class _ReplaceGrad(torch.autograd.Function):
    @staticmethod
    def forward(ctx, inp0: torch.Tensor, inp1: torch.Tensor, tmp_inp0: torch.Tensor, tmp_inp1: torch.Tensor):
        ctx.save_for_backward(inp0.detach(), inp1.detach())
        return inp0, inp1

    @staticmethod
    def backward(ctx, grad0: torch.Tensor, grad1: torch.Tensor):
        tmp_inp0, tmp_inp1 = ctx.saved_tensors
        return grad0, grad1, tmp_inp0, tmp_inp1


def _set_device(mod: torch.nn.Module, device: str) -> torch.nn.Module:
    if not device:
        return mod
    return copy.deepcopy(mod).to(device, non_blocking=True)


def split_tensor_list(inp: typing.Union[typing.Iterable[torch.Tensor], torch.Tensor]
                      ) -> typing.Union[typing.Tuple[torch.Tensor, typing.List[torch.Tensor]], torch.Tensor]:
    if isinstance(inp, torch.Tensor):
        return inp
    if isinstance(inp, typing.Iterable):
        inp = list(inp)
        return inp[0], inp[1:]
    ValueError(f"Unsupported Type {type(inp)}")


def take_0th_tensor(inp: typing.Union[typing.Iterable[torch.Tensor], torch.Tensor]) -> torch.Tensor:
    out = split_tensor_list(inp)
    if not isinstance(out, torch.Tensor):
        return out[0]
    return inp


class ReversibleWrapper(torch.nn.Module):
    def __init__(self, wrapped_module: torch.nn.Module, coupling_forward: typing.Optional[COUPLING] = None,
                 coupling_inverse: typing.Optional[COUPLING] = None):
        """
        A handy utility-module that allows accessing inverses without rewriting significant amounts of code. This module
        does not do reversibility by itself. It's mostly used as a storage object.

        :param wrapped_module: the module that's supposed to be run in a revnet-like structure
        :param coupling_forward: RevNet uses y0 = (x0 + f(x1)) as a coupling function, but this allows you to set a
        custom one. For example, MomentumNet (https://arxiv.org/abs/2102.07870) uses
        y0 = (beta * x0 + (1 - beta) * f(x1)). The inputs to the coupling function are the residual stream and the
        function output. For more information, look at the examples. default = revnet couplint
        :param coupling_inverse: The inverse of the coupling function. default = revnet inverse
        """
        super(ReversibleWrapper, self).__init__()
        self.wrapped_module = wrapped_module
        self.coupling_forward = coupling_forward or additive_coupling_forward
        self.coupling_inverse = coupling_inverse or additive_coupling_inverse

    def forward(self, x0: torch.Tensor, x1: torch.Tensor, *args, **kwargs) -> TENSOR_OR_LIST:
        return self.coupling_forward(x0, self.wrapped_module(x1, *args, **kwargs))

    def inverse(self, y0: torch.Tensor, y1: torch.Tensor, *args, **kwargs) -> TENSOR_OR_LIST:
        return self.coupling_inverse(y1, self.wrapped_module(y0, *args, **kwargs))


def _optimizer_step(optimizer_step: typing.Optional[typing.Callable[[], None]], module: torch.nn.Module):
    optimizer_step()
    module.zero_grad(set_to_none=True)


class _ReversibleHalfResidualSwapFn(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x0: torch.Tensor, x1: torch.Tensor, back_x0: torch.Tensor, back_x1: torch.Tensor,
                mod: ReversibleWrapper, target_device: str, cuda: bool,
                optimizer_step: typing.Optional[typing.Callable[[], None]], args: typing.Iterable,
                kwargs: dict):
        ctx.mod = mod
        ctx.target_device = target_device
        ctx.forward_rng_state = torch.get_rng_state()
        ctx.cuda = cuda
        ctx.optimizer_step = optimizer_step
        ctx.args = args
        ctx.kwargs = kwargs
        if cuda:
            ctx.cuda_devices, ctx.cuda_states = torch.utils.checkpoint.get_device_states(x0, x1, back_x0, back_x1)
        out = _set_device(mod, target_device)(x0, x1, *args, **kwargs)
        out = split_tensor_list(out)
        if isinstance(out, torch.Tensor):
            residual = None
        else:
            residual = out[1]
            out = out[0]
        return x1, out, back_x0, back_x1, residual

    @staticmethod
    def backward(ctx, dy0: torch.Tensor, dy1: torch.Tensor, y0: torch.Tensor, y1: torch.Tensor, _unused
                 ) -> typing.Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, None, None, None, None, None,
                                   None]:
        original_rng_state = torch.get_rng_state()
        torch.set_rng_state(ctx.forward_rng_state)
        if dy0 is None:
            dy0 = torch.zeros_like(y0)
        if dy1 is None:
            dy1 = torch.zeros_like(y0)
        if ctx.cuda:
            original_cuda_state = torch.utils.checkpoint.get_device_states(dy0, dy1, y0, y1)
            torch.utils.checkpoint.set_device_states(ctx.cuda_devices, ctx.cuda_states)
        with torch.enable_grad():
            y0 = y0.detach().requires_grad_()
            y0.retain_grad()
            new_mod = _set_device(ctx.mod, ctx.target_device)
            mod_out = take_0th_tensor(new_mod.wrapped_module(y0, *ctx.args, **ctx.kwargs))
        with torch.no_grad():
            x0 = ctx.mod.coupling_inverse(y1, mod_out.detach()).detach()
        with torch.enable_grad():
            out = ctx.mod.coupling_forward(x0, mod_out)
        if hasattr(dy1, "thread"):
            dy1.thread.join()
        torch.autograd.backward(out, dy1)
        if ctx.target_device:
            with torch.no_grad():
                for p, new_p in zip(ctx.mod.parameters(), new_mod.parameters()):
                    if new_p.grad is None:
                        continue
                    new_grad = new_p.grad.to(p.device, non_blocking=True)
                    if p.grad is None:
                        p.grad = new_grad
                        continue
                    p.grad.add_(new_grad)
        if ctx.cuda:
            torch.utils.checkpoint.set_device_states(*original_cuda_state)
        torch.set_rng_state(original_rng_state)
        with torch.enable_grad():
            out_grad = ctx.mod.coupling_forward(dy0, y0.grad).detach_()
            if ctx.optimizer_step is not None:
                out_grad.thread = threading.Thread(target=_optimizer_step, args=(ctx.optimizer_step, ctx.mod))
                out_grad.thread.start()
            return dy1.detach(), out_grad, x0, y0, None, None, None, None, None, None


class TensorOffload(torch.autograd.Function):
    """
    Allows offloading a single tensor to another device, without altering the tensor itself. This is kind of like .to()
    from pytorch, without forcing the tensor (or parameter!) to stay on the new device forever.
    """

    @staticmethod
    def forward(ctx, inp: torch.Tensor, reference: torch.Tensor):
        ctx.device = inp.device
        return inp.to(device=reference.device, non_blocking=True)

    @staticmethod
    def backward(ctx, grad_outputs: torch.Tensor):
        return grad_outputs.to(ctx.device, non_blocking=True), None


offload_tensor = TensorOffload.apply
replace_grad = _ReplaceGrad.apply
reverse_and_swap = _ReversibleHalfResidualSwapFn.apply


def additive_coupling_forward(other_stream: torch.Tensor, fn_out: torch.Tensor) -> TENSOR_OR_LIST:
    fn_out = split_tensor_list(fn_out)
    if isinstance(fn_out, torch.Tensor):
        return other_stream + fn_out
    return [other_stream + fn_out[0]] + fn_out[1]


def additive_coupling_inverse(output: torch.Tensor, fn_out: torch.Tensor) -> TENSOR_OR_LIST:
    fn_out = split_tensor_list(fn_out)
    if isinstance(fn_out, torch.Tensor):
        return output - fn_out
    return [output - fn_out[0]] + fn_out[1]


class ReversibleModuleCache:
    x0: torch.Tensor
    x1: torch.Tensor

    def __call__(self, x0: torch.Tensor, x1: torch.Tensor):
        self.x0 = x0.detach()
        self.x1 = x1.detach()


def get_key(idx: int, inp: torch.Tensor):
    return f'Index: {idx}\nSize: {inp.size()}\nDevice: {inp.device}\nDataType: {inp.dtype}'


class ReversibleModule(torch.nn.Module):
    cpu_state: torch.Tensor
    cuda_states: typing.List[torch.Tensor]

    def __init__(self, wrapped_module: torch.nn.Module, coupling_forward: typing.Optional[COUPLING] = None,
                 coupling_inverse: typing.Optional[COUPLING] = None, memory_savings: bool = True,
                 cache: typing.Optional[ReversibleModuleCache] = None, target_device: str = "",
                 fused_optimizer: FUSED_OPTIMIZER = None):

        """
        A `ReversibleModule` that does the heavy lifting of dispatching to various backends in an effort to avoid
        storing all intermediate buffers at the same time. It can wrap any module.

        :param wrapped_module: The one module that's supposed to be wrapped in a reversible way. (You need multiple
        sequential modules to see memory gains.)
        :param coupling_forward: RevNet uses y0 = (x0 + f(x1)) as a coupling function, but this allows you to set a
        custom one. For example, MomentumNet (https://arxiv.org/abs/2102.07870) uses
        y0 = (beta * x0 + (1 - beta) * f(x1)). The inputs to the coupling function are the residual stream and the
        function output. For more information, look at the examples. default = revnet couplint
        :param coupling_inverse: The inverse of the coupling function. default = revnet inverse
        :param memory_savings: whether to use memory savings or not. disabling results in a revnet that will allocate
        all intermediate tensors as a normal non-reversible network would.
        :param cache: an optional cache that's used to store intermediate buffers for the reversible module. if there's
        no cache, it will fall back to using autograd functions.
        :param target_device: Specifies where the parameters should be moved to before computing the forward and
        backward pass. This allows efficient CPU-offloading.
        default = no offloading (keep parameters on the device they're on)
        :param fused_optimizer: Allows an optimizer step to run while the model is computing its backward pass. This
        means that the gradients don't have to be fully instantiated anymore and can improve speed when used with
        cpu-offload due to asynchronous compute. It expects a function that generates an optimizer from a list of
        parameters. (like Adam.__init__) default = no fused optimizer step
        """
        super(ReversibleModule, self).__init__()
        self.wrapped_module = ReversibleWrapper(wrapped_module, coupling_forward, coupling_inverse)
        self.target_device = target_device
        self.memory_savings = memory_savings
        self.cache = cache

        self.cuda_devices = []
        self.cuda: bool = torch.cuda._initialized
        self.autocast: bool = torch.is_autocast_enabled()

        self.counter: int = 0
        self.storage: typing.Dict[str, torch.Tensor] = {}
        self.input_args = []
        self.input_kwargs = {}

        parameters = list(self.wrapped_module.parameters())

        if fused_optimizer is None or not parameters:
            self.fused_optimizer = None
            self.fused_optimizer_step = None
        else:
            self.fused_optimizer = fused_optimizer(parameters)
            self.fused_optimizer_step = self.fused_optimizer.step

        if self.fused_optimizer is not None and not self.memory_savings:
            raise ValueError("Can't fuse the optimizer if RevLib doesn't modify the training graph!")

        if self.fused_optimizer is not None and self.cache is not None:
            raise ValueError("Fused optimizer is not currently supported with checkpointing and autograd-graph.")

    def pack(self, inp: torch.Tensor) -> str:
        self.counter += 1
        return get_key(self.counter - 1, inp)

    def inner_pack(self, inp: torch.Tensor):
        self.storage[get_key(len(self.storage), inp)] = inp

    def inner_unpack(self, key: str):
        raise RuntimeError(f'Tensor not found.\nSpec:\n{key}')

    def unpack(self, key: str) -> torch.Tensor:
        if self.storage:
            if key not in self.storage:
                self.inner_unpack(key)
            return self.storage[key]

        x1 = self.cache.x0
        y1 = self.cache.x1

        with torch.random.fork_rng(self.cuda_devices):
            torch.set_rng_state(self.cpu_state)
            if self.cuda:
                torch.utils.checkpoint.set_device_states(self.cuda_devices, self.cuda_states)
            with torch.enable_grad(), torch.cuda.amp.autocast(self.autocast):
                with torch.autograd.graph.saved_tensors_hooks(self.inner_pack, self.inner_unpack):
                    out = self.wrapped_module.wrapped_module(x1, *self.input_args, **self.input_kwargs)
                x0 = self.wrapped_module.coupling_inverse(y1, take_0th_tensor(out).detach()).detach_()
                self.cache(x0, x1)
                with torch.autograd.graph.saved_tensors_hooks(self.inner_pack, self.inner_unpack):
                    _unused = self.wrapped_module.coupling_forward(x0, out)
        return self.unpack(key)

    def forward(self, inp: DUAL_OR_QUAD_TENSOR, *args, **kwargs) -> DUAL_OR_QUAD_TENSOR:
        self.input_args = args
        self.input_kwargs = kwargs

        x0, x1, *back = inp
        self.cpu_state = torch.get_rng_state()
        if self.cuda:
            self.cuda_devices, self.cuda_states = torch.utils.checkpoint.get_device_states(*inp)

        if not self.memory_savings:
            return x1, self.wrapped_module(x0, x1, *args, **kwargs)

        if self.cache is None:
            x0, x1, y0, y1, res = reverse_and_swap(x0, x1, *back, self.wrapped_module, self.target_device, self.cuda,
                                                   self.fused_optimizer_step, args, kwargs)
            if res is not None:
                x1 = [x1] + res
            return x0, x1, y0, y1

        self.counter = 0
        self.storage = {}
        with torch.autograd.graph.saved_tensors_hooks(self.pack, self.unpack):
            y1 = self.wrapped_module(x0, x1, *args, **kwargs)

        out = split_tensor_list(y1)
        if not isinstance(out, torch.Tensor):
            out = out[0]
        self.cache(x1, out)
        return x1, y1

    def extra_repr(self) -> str:
        return '\n'.join([f'coupling_forward={self.wrapped_module.coupling_forward.__name__}',
                          f'coupling_inverse={self.wrapped_module.coupling_inverse.__name__}',
                          f'target_device={self.target_device if self.target_device else None}'])


class SingleBranchReversibleModule(ReversibleModule):
    def __init__(self, secondary_branch_buffer: typing.List[torch.Tensor], wrapped_module: torch.nn.Module,
                 coupling_forward: typing.Optional[COUPLING] = None,
                 coupling_inverse: typing.Optional[COUPLING] = None, memory_savings: bool = True,
                 cache: typing.Optional[ReversibleModuleCache] = None,
                 target_device: str = "",
                 fused_optimizer: FUSED_OPTIMIZER = None,
                 first: bool = False,
                 last: bool = False):
        """
        A wrapper around `ReversibleModule` that hides all additional outputs and pretends the model is still acting
        the same way it used to.
        Doing so requires some additional buffers which isn't as efficient as handling the RevNet buffers explicitly,
        but it allows seamless integration into existing models.

        :param secondary_branch_buffer: A buffer of tensors that's shared across all instances of `ReversibleModule`,
        which is used to store additional outputs which aren't returned.
        :param wrapped_module: The one module that's supposed to be wrapped in a reversible way. (You need multiple
        sequential modules to see memory gains.)
        :param coupling_forward: RevNet uses y0 = (x0 + f(x1)) as a coupling function, but this allows you to set a
        custom one. For example, MomentumNet (https://arxiv.org/abs/2102.07870) uses
        y0 = (beta * x0 + (1 - beta) * f(x1)). The inputs to the coupling function are the residual stream and the
        function output. For more information, look at the examples. default = revnet couplint
        :param coupling_inverse: The inverse of the coupling function. default = revnet inverse
        :param memory_savings: whether to use memory savings or not. disabling results in a revnet that will allocate
        all intermediate tensors as a normal non-reversible network would.
        :param cache: an optional cache that's used to store intermediate buffers for the reversible module. if there's
        no cache, it will fall back to using autograd functions.
        :param target_device: Specifies where the parameters should be moved to before computing the forward and
        backward pass. This allows efficient CPU-offloading.
        default = no offloading (keep parameters on the device they're on)
        :param fused_optimizer: Allows an optimizer step to run while the model is computing its backward pass. This
        means that the gradients don't have to be fully instantiated anymore and can improve speed when used with
        cpu-offload due to asynchronous compute. It expects a function that generates an optimizer from a list of
        parameters. (like Adam.__init__) default = no fused optimizer step
        :param first: Whether it's the first module of a sequence. If so, it will initialize all buffers and make sure
        they're passed along.
        :param last: Whether it's the last module of a sequence. If so, it will run the necessary clean-up procedures to
        ensure pytorch's autograd will work.
        """
        super(SingleBranchReversibleModule, self).__init__(wrapped_module=wrapped_module,
                                                           coupling_forward=coupling_forward,
                                                           coupling_inverse=coupling_inverse,
                                                           memory_savings=memory_savings,
                                                           cache=cache,
                                                           target_device=target_device,
                                                           fused_optimizer=fused_optimizer)
        self.secondary_branch_buffer = secondary_branch_buffer
        self.first = first
        self.last = last

    def forward(self, x1: torch.Tensor, *args, **kwargs) -> torch.Tensor:  # skipcq: PYL-W0221
        if self.first:
            self.secondary_branch_buffer.clear()
            x0 = back0 = torch.zeros_like(x1)
            back = (back0, back0)
        else:
            x0, *back = self.secondary_branch_buffer.pop()
        inp = (x0, x1)
        if back:
            inp = inp + (back[0], back[1])
        _, y1, *back = super(SingleBranchReversibleModule, self).forward(inp, *args, **kwargs)
        if self.last:
            if self.memory_savings and self.cache is None:
                out = out0 = split_tensor_list(y1)
                if not isinstance(out0, torch.Tensor):
                    out = out0[0]
                _, out = replace_grad(x1, out, *back)
                if not isinstance(out0, torch.Tensor):
                    y1 = [out] + out0[1]
        else:
            self.secondary_branch_buffer.append([x1] + back)
        return y1


class MergeCalls(torch.nn.Module):
    def __init__(self, *modules: SingleBranchReversibleModule, collate_fn: typing.Callable[[torch.Tensor, list], list]):
        """
        MergeCalls acts the same way as nn.Sequential, but allows the usage of a custom collate function which specifies
        which outputs to return. It also allows arguments and keyword-arguments.
        Thanks to MergeCalls, it's trivial to integrate MomentumNets into existing sequential models without giving up
        on the custom tooling built around the models!
        :param modules: all modules that will be executed sequentially
        :param collate_fn: collate function that takes in all outputs and returns a list of tensors.
        """
        super(MergeCalls, self).__init__()
        self.wrapped_modules = torch.nn.ModuleList(modules)
        self.collate_fn = collate_fn

    def forward(self, inp: torch.Tensor, *args, **kwargs) -> typing.Union[torch.Tensor, typing.List[torch.Tensor]]:
        out = []
        for mod in self.wrapped_modules:
            inp = mod(inp, *args, **kwargs)
            inp = split_tensor_list(inp)
            if not isinstance(inp, torch.Tensor):
                out.append([inp[0]] + inp[1])
                inp = inp[0]
        if not out:
            return inp
        return self.collate_fn(inp, out)


class ReversibleSequential(torch.nn.Sequential):
    def __init__(self, *modules, split_dim: typing.Optional[int] = 1,
                 coupling_forward: typing.Optional[typing.List[typing.Optional[COUPLING]]] = None,
                 coupling_inverse: typing.Optional[typing.List[typing.Optional[COUPLING]]] = None,
                 memory_mode: MemoryModes = MemoryModes.autograd_function,
                 target_device: str = "",
                 fused_optimizer: FUSED_OPTIMIZER = None):
        """
        Wrapper around `ReversibleModule` that automatically creates a sequential RevNet as introduced in
        https://arxiv.org/abs/1707.04585

        :param modules: All nn.Modules that should be wrapped. It's the same syntax as nn.Sequential, but adds a
        reversible residual stream.
        :param split_dim: RevNets require two streams. This parameter specifies which dimension to split in half to
        create the two streams. `None` would mean the input gets replicated for both streams. It's usually best to split
        along the features, which is why the default (1) is compatible with convolutions.
        :param coupling_forward: RevNet uses y0 = (x0 + f(x1)) as a coupling function, but this allows you to set a
        custom one. For example, MomentumNet (https://arxiv.org/abs/2102.07870) uses
        y0 = (beta * x0 + (1 - beta) * f(x1)). The inputs to the coupling function are the residual stream and the
        function output. For more information, look at the examples. default = revnet couplint
        :param coupling_inverse: The inverse of the coupling function. default = revnet inverse
        :param memory_mode: One of `MemoryModes`'s values. Some things are only supported in one mode while others
        might only be supported in another. default = autograd function (highest coverage but spotty XLA support)
        :param target_device: Specifies where the parameters should be moved to before computing the forward and
        backward pass. This allows efficient CPU-offloading.
        default = no offloading (keep parameters on the device they're on)
        :param fused_optimizer: Allows an optimizer step to run while the model is computing its backward pass. This
        means that the gradients don't have to be fully instantiated anymore and can improve speed when used with
        cpu-offload due to asynchronous compute. It expects a function that generates an optimizer from a list of
        parameters. (like Adam.__init__) default = no fused optimizer step
        """
        super(ReversibleSequential, self).__init__()
        coupling_forward = list(coupling_forward) if coupling_forward else [None]
        coupling_inverse = list(coupling_inverse) if coupling_inverse else [None]
        memory_savings = memory_mode != MemoryModes.no_savings
        cache = ReversibleModuleCache() if memory_mode in (MemoryModes.checkpoint, MemoryModes.autograd_graph) else None
        self.replace_grad = replace_grad if memory_mode == MemoryModes.autograd_function else lambda *x: x
        for i, m in enumerate(modules):
            if not isinstance(m, ReversibleModule):
                m = ReversibleModule(m,
                                     coupling_forward[i % len(coupling_forward)],
                                     coupling_inverse[i % len(coupling_inverse)],
                                     memory_savings,
                                     copy.deepcopy(cache) if memory_mode == MemoryModes.checkpoint else cache,
                                     target_device,
                                     fused_optimizer)
            self.add_module(f'{i // 2}-{i % 2}', m)
        self.split_dim = split_dim
        self.m = memory_mode

    def forward(self, inp: torch.Tensor, *args,
                layerwise_args_kwargs: typing.Optional[typing.List[typing.Tuple[typing.List[typing.Any],
                                                                                typing.Dict[str, typing.Any]]]] = None,
                **kwargs) -> torch.Tensor:
        if self.split_dim is None:
            inp0 = inp1 = inp
        else:
            inp0, inp1 = inp.chunk(2, self.split_dim)
        zeros = torch.zeros_like(inp0)
        if layerwise_args_kwargs is not None:
            args = [list(args) + arg[0] for arg in args]
            kwargs = [{**kwargs, **arg[1]} for arg in args]
        else:
            args = [args] * len(self)
            kwargs = [kwargs] * len(self)
        if not args:
            args = [[]] * len(self)
        if not kwargs:
            kwargs = [{}] * len(self)
        out = inp0, inp1, zeros, zeros
        for mod, arg, kwarg in zip(self, args, kwargs):
            out = mod(out, *arg, **kwarg)
        return torch.cat(self.replace_grad(*out), dim=self.split_dim)
