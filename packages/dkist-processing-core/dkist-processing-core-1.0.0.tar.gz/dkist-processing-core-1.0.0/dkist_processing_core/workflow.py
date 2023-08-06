"""Abstraction layer to construct a workflow as an airflow DAG."""
import json
import string
from os import environ
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

from airflow import DAG

from dkist_processing_core._node import Node
from dkist_processing_core._node import task_type_hint
from dkist_processing_core._node import upstreams_type_hint

__all__ = ["Workflow"]

MAXIMUM_ALLOWED_WORKFLOW_NAME_LENGTH = 50


class Workflow:
    """
    Abstraction to create a workflow in the implemented engine api (airflow).

    - Defines the api for task and workflow definition
    - abstracts workflow engine syntax from definition
    - implements workflow and tasks in engine specific syntax
    - engine = airflow
    - contains nodes and the relationships between them

    >>> category = "instrument"
    >>> input_data = "l0"
    >>> output_data = "l1"
    >>> detail = "OCP-use-only"
    >>> version = "V6-12342"
    >>> tags = ["use-XYZ-algorithm"]
    >>> task = Task()
    >>> workflow_instance = Workflow(
    >>>    category=category,
    >>>    input_data=input_data,
    >>>    output_data=output_data,
    >>>    detail=detail,
    >>>    workflow_package=__package__,
    >>>    workflow_version=version,
    >>>    tags=tags
    >>>)
    >>> workflow_instance.add_node(task=task, upstreams=None)
    """

    def __init__(
        self,
        input_data: str,
        output_data: str,
        category: str,
        workflow_package: str,
        detail: Optional[str] = None,
        tags: Optional[List[str]] = None,
        workflow_version: Optional[str] = None,
    ):
        """
        Create a workflow instance.

        Parameters
        ----------
        input_data: Description of the primary inputs to the workflow e.g. l0
        output_data: Description of the primary outputs of the workflow e.g. l1
        category: Category for the process the workflow executes e.g. instrument name
        detail: Extra information to separate this workflow from a similar workflow
        workflow_package: The string representing the dot notation location of the
          workflow definition. e.g. __package__
        tags: tags to be used in airflow's UI when searching for dags
        workflow_version: Version of the workflow being deployed.  Typically populated by the CI/CD
          build process.

        """
        self.workflow_package = workflow_package
        self.category = category
        self.input_data = input_data
        self.output_data = output_data
        self.detail = detail
        self.workflow_name = f"{self.input_data}_to_{self.output_data}_{category}"
        if self.detail:
            self.workflow_name += f"_{self.detail}"
        if len(self.workflow_name) > MAXIMUM_ALLOWED_WORKFLOW_NAME_LENGTH:
            raise ValueError(
                f"Workflow name {self.workflow_name} is {len(self.workflow_name)} characters long. "
                f"Limit is {MAXIMUM_ALLOWED_WORKFLOW_NAME_LENGTH} characters."
            )
        self.workflow_version = workflow_version or environ.get("BUILD_VERSION", "dev")
        self.tags = tags or []
        self._dag_name = f"{self.workflow_name}_{self.workflow_version}"
        self.check_dag_name_characters(self._dag_name)
        self._dag = self._initialize_local_dag()
        self.nodes = []

    @staticmethod
    def check_dag_name_characters(dag_name: str):
        """
        Figure out if the dag name is an Airflow-allowed name.

        Can only contain
        * ascii letters
        * numbers
        * dash (-)
        * dot (.)
        * underscore (_)

        Raise error if non-allowed characters are found.
        """
        allowed_chars = (
            [c for c in string.ascii_letters] + ["-", ".", "_"] + [n for n in string.digits]
        )
        if not all([char in allowed_chars for char in dag_name]):
            raise ValueError(
                f"Dag name {dag_name} contains invalid characters. "
                f"Only ascii letters and the dash, dot, and "
                f"underscore symbols are permitted."
            )

    @property
    def _dag_tags(self) -> str:
        """
        Return the list of dag tags to be used in Airflow's UI.

        Equal to the list of supplied tags plus the workflow version, input and output data,
        and category.
        """
        if isinstance(self.tags, str):
            self.tags = [self.tags]
        tags = self.tags + [self.workflow_version, self.input_data, self.output_data, self.category]
        # Make sure there are no duplicate tags
        tags = list(set(tags))
        return json.dumps(tags)

    @property
    def _dag_definition(self) -> str:
        return f"DAG(dag_id='{self._dag_name}', start_date=days_ago(2), schedule_interval=None, catchup=False, tags={self._dag_tags})"

    def _initialize_local_dag(self) -> DAG:
        from airflow.utils.dates import days_ago

        return eval(self._dag_definition)

    def add_node(
        self,
        task: task_type_hint,
        upstreams: upstreams_type_hint = None,
    ) -> None:
        """Add a node and edges from that node to the workflow."""
        node = Node(
            workflow_name=self.workflow_name,
            workflow_version=self.workflow_version,
            workflow_package=self.workflow_package,
            task=task,
            upstreams=upstreams,
        )
        self.nodes.append(node)
        # confirm that the node can be properly added to a dag
        self._dag.add_task(node.operator)
        for upstream, downstream in node.dependencies:
            self._dag.set_dependency(upstream, downstream)

    def load(self) -> DAG:
        """Retrieve the native engine (airflow) workflow object."""
        return self._dag

    def export(self, export_path: Optional[Union[str, Path]] = None) -> Path:
        """Write a file representation of the workflow which can be run independently of the task dependencies."""
        export_path = export_path or "export/"
        export_path = Path(export_path)
        export_path.mkdir(exist_ok=True)
        workflow_py = export_path / f"{self._dag_name}.py"

        with workflow_py.open(mode="w") as f:
            f.write(
                f"#  {self.workflow_name} workflow version {self.workflow_version} definition rendered for airflow scheduler\n"
            )
            f.write(self._workflow_imports)
            f.write("# Workflow\n")
            f.write(self._workflow_instantiation)
            f.write("    # Nodes\n")
            for n in self.nodes:
                operator = f"{n.task.__name__.lower()}_operator"
                f.write(f"    {operator} = {n.operator_definition}")
                f.write("\n")
            f.write("    # Edges\n")
            f.write(self._workflow_edges)
            f.write("\n")
        return workflow_py

    @property
    def _workflow_imports(self) -> str:
        imports = [
            "from datetime import timedelta",
            "from functools import partial",
            "",
            "from airflow import DAG",
            "from airflow.operators.bash import BashOperator",
            "from airflow.utils.dates import days_ago",
            "",
            "from dkist_processing_core._failure_callback import chat_ops_notification",
            "",
            "",
        ]
        return "\n".join(imports)

    @property
    def _workflow_instantiation(self) -> str:
        return f"with {self._dag_definition} as d:\n    pass\n"

    @property
    def _workflow_edges(self) -> str:
        edges = []
        for n in self.nodes:
            for upstream, downstream in n.dependencies:
                edges.append(f"    d.set_dependency('{upstream}', '{downstream}')")
        return "\n".join(edges)

    def __repr__(self):
        """Detailed representation of the workflow."""
        return (
            f"Workflow("
            f"input_data={self.input_data}, "
            f"output_data={self.output_data}, "
            f"category={self.category}, "
            f"detail={self.detail}, "
            f"workflow_package={self.workflow_package}, "
            f"workflow_version={self.workflow_version}, "
            f")"
        )

    def __str__(self):
        """Representation of the workflow as a string."""
        return repr(self)
