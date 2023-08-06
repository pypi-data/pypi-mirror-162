"""Tests for the Workflow abstraction."""
import json
from typing import Callable

import pytest
from airflow import DAG

from dkist_processing_core import Workflow


def test_workflow_metadata(workflow):
    """
    Given: A workflow instance.
    When: accessing attributes.
    Then: Tha values are properly assigned.
    """
    (
        workflow_instance,
        input_data,
        output_data,
        category,
        detail,
        version,
        tags,
    ) = workflow

    assert workflow_instance.workflow_name == f"{input_data}_to_{output_data}_{category}_{detail}"
    assert workflow_instance.workflow_version == version
    assert workflow_instance.workflow_package.startswith(__package__.split(".")[0])
    assert workflow_instance.nodes == []
    assert isinstance(workflow_instance._dag, DAG)
    assert (
        workflow_instance._dag.dag_id
        == f"{input_data}_to_{output_data}_{category}_{detail}_{version}"
    )
    assert workflow_instance.category == category
    assert workflow_instance.input_data == input_data
    assert workflow_instance.output_data == output_data
    assert workflow_instance.detail == detail
    assert sorted(json.loads(workflow_instance._dag_tags)) == sorted(
        [tag for tag in tags] + [input_data, output_data, category, version]
    )


def test_workflow_add_node(workflow_tasks, workflow):
    """
    Given: A set of tasks and a workflow instance.
    When: Adding the tasks to the workflow in the
      structure of A >> [B, C] >> D.
    Then: the dag object owned by the workflow has the right structure.
    """
    (
        workflow_instance,
        process_input,
        process_output,
        process_category,
        process_detail,
        version,
        tags,
    ) = workflow
    TaskA, TaskB, TaskC, TaskD = workflow_tasks
    task_definitions = {
        TaskA: None,  # none
        TaskB: TaskA,  # single
        TaskC: TaskA,  # single
        TaskD: [TaskB, TaskC],  # list
    }
    task_upstream_expectations = {
        TaskA.__name__: set(),
        TaskB.__name__: {
            TaskA.__name__,
        },
        TaskC.__name__: {
            TaskA.__name__,
        },
        TaskD.__name__: {
            TaskB.__name__,
            TaskC.__name__,
        },
    }
    for task, upstream in task_definitions.items():
        workflow_instance.add_node(task, upstreams=upstream)

    dag = workflow_instance.load()
    assert dag.task_count == 4
    assert len(workflow_instance.nodes) == 4

    for task in dag.tasks:
        assert (
            task.dag_id
            == f"{process_input}_to_{process_output}_{process_category}_{process_detail}_{version}"
        )
        assert task.upstream_task_ids == task_upstream_expectations[task.task_id]


def test_invalid_workflow_add_node(workflow):
    """
    Given: An invalid task (not inheriting from TaskBase)and a workflow instance.
    When: Adding the task to the workflow.
    Then: Get a TypeError.
    """
    workflow_instance, *args = workflow

    class Task:
        pass

    with pytest.raises(TypeError):
        workflow_instance.add_node(Task)


@pytest.mark.parametrize(
    "func, attr",
    [
        pytest.param(repr, "__repr__", id="repr"),
        pytest.param(str, "__str__", id="str"),
    ],
)
def test_tag_db_dunder(workflow, func: Callable, attr):
    """
    Given: Connection to a tag database.
    When: retrieving dunder method that should be implemented.
    Then: It is implemented.
    """
    workflow_instance, *args = workflow

    assert getattr(workflow_instance, attr, None)
    assert func(workflow_instance)


def test_check_dag_name_characters():
    """
    Given: a dag name
    When: checking if it is a valid airflow name or not
    Then: correctly identify valid and invalid names
    """
    Workflow.check_dag_name_characters(dag_name="This_dag_name_is_valid")
    with pytest.raises(ValueError):
        Workflow.check_dag_name_characters(dag_name="Invalid*dag*name")
