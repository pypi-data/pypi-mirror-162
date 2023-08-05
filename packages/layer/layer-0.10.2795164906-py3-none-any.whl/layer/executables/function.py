import hashlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence, Union

import layer
from layer.contracts.asset import AssetType
from layer.contracts.fabrics import Fabric
from layer.executables.packager import (
    FUNCTION_SERIALIZER_NAME,
    FUNCTION_SERIALIZER_VERSION,
    package_function,
)


FunctionOutput = Union["DatasetOutput", "ModelOutput"]


class Function:
    def __init__(
        self,
        func: Callable[..., Any],
        output: FunctionOutput,
        pip_dependencies: Sequence[str],
        resources: Sequence[Path],
        fabric: Fabric,
        source_code: str,
        source_code_digest: str,
    ) -> None:
        self._func = func
        self._output = output
        self._pip_dependencies = pip_dependencies
        self._resources = resources
        self._fabric = fabric
        self._source_code = source_code
        self._source_code_digest = source_code_digest

    @staticmethod
    def from_decorated(func: Callable[..., Any]) -> "Function":
        output = _get_function_output(func)
        pip_dependencies = _get_function_pip_dependencies(func)
        resources = _get_function_resources(func)
        fabric = _get_function_fabric(func)
        wrapped_func = _undecorate_function(func)
        source_code = inspect.getsource(func)
        sha256 = hashlib.sha256()
        sha256.update(source_code.encode("utf-8"))
        source_code_digest = sha256.hexdigest()
        return Function(
            wrapped_func,
            output=output,
            pip_dependencies=pip_dependencies,
            resources=resources,
            fabric=fabric,
            source_code=source_code,
            source_code_digest=source_code_digest,
        )

    @property
    def func(self) -> Callable[..., Any]:
        return self._func

    @property
    def output(self) -> FunctionOutput:
        return self._output

    @property
    def pip_dependencies(self) -> Sequence[str]:
        return self._pip_dependencies

    @property
    def resources(self) -> Sequence[Path]:
        return self._resources

    @property
    def fabric(self) -> Fabric:
        return self._fabric

    @property
    def source_code(self) -> str:
        return self._source_code

    @property
    def source_code_digest(self) -> str:
        return self._source_code_digest

    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            "sdk": {
                "version": layer.__version__,
            },
            "function": {
                "serializer": {
                    "name": FUNCTION_SERIALIZER_NAME,
                    "version": FUNCTION_SERIALIZER_VERSION,
                },
                "output": {
                    "name": self._output.name,
                    "type": self.output_type_name,
                },
                "fabric": {"name": self._fabric.value},
                "source": {
                    "source_code": self._source_code,
                    "digest": self._source_code_digest,
                },
            },
        }

    @property
    def output_type_name(self) -> str:
        if isinstance(self._output, DatasetOutput):
            return AssetType.DATASET.value
        if isinstance(self._output, ModelOutput):
            return AssetType.MODEL.value

    def package(self, output_dir: Optional[Path] = None) -> Path:
        return package_function(
            self._func,
            pip_dependencies=self._pip_dependencies,
            resources=self._resources,
            output_dir=output_dir,
            metadata=self.metadata,
        )


# the names of the function decorators to unwrap user functions from
_DECORATOR_FUNCTION_WRAPPERS = frozenset(
    (
        "DatasetFunctionWrapper",
        "FunctionWrapper",
        "PipRequirementsFunctionWrapper",
        "FabricFunctionWrapper",
        "ResourcesFunctionWrapper",
    )
)


def _undecorate_function(func: Callable[..., Any]) -> Callable[..., Any]:
    # check if function is decorated with any of the layer decorators
    if type(func).__name__ in _DECORATOR_FUNCTION_WRAPPERS and hasattr(
        func, "__wrapped__"
    ):
        return _undecorate_function(func.__wrapped__)  # type: ignore
    else:
        return func


def _get_function_output(func: Callable[..., Any]) -> FunctionOutput:
    asset_type = _get_decorator_attr(func, "asset_type")
    asset_name = _get_decorator_attr(func, "asset_name")
    if asset_type is None or asset_name is None:
        raise FunctionError(
            'either @dataset(name="...") or @model(name="...") top level decorator '
            "is required for each function. Add @dataset or @model decorator on top of existing "
            "decorators to run functions in Layer"
        )
    if asset_type == AssetType.DATASET:
        return DatasetOutput(asset_name)
    if asset_type == AssetType.MODEL:
        return ModelOutput(asset_name)

    raise FunctionError(f"unsupported asset type: '{asset_type}'")


def _get_function_pip_dependencies(func: Callable[..., Any]) -> Sequence[str]:
    pip_packages = _get_decorator_attr(func, "pip_packages") or []
    requirements = _get_decorator_attr(func, "pip_requirements_file")
    if requirements is not None and len(requirements) > 0:
        with open(requirements, "r") as f:
            pip_packages += f.read().splitlines()
    return tuple(pip_packages)


def _get_function_resources(func: Callable[..., Any]) -> Sequence[Path]:
    resource_paths = _get_decorator_attr(func, "resource_paths") or []
    return tuple(Path(resource_path.path) for resource_path in resource_paths)


def _get_function_fabric(func: Callable[..., Any]) -> Fabric:
    return _get_decorator_attr(func, "fabric") or Fabric.default()


def _get_decorator_attr(func: Callable[..., Any], attr: str) -> Optional[Any]:
    if hasattr(func, "layer") and hasattr(func.layer, attr):  # type: ignore
        return getattr(func.layer, attr)  # type: ignore
    return None


@dataclass(frozen=True)
class DatasetOutput:
    name: str


@dataclass(frozen=True)
class ModelOutput:
    name: str


class FunctionError(Exception):
    pass
